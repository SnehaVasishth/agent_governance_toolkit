from agent_runtime import (
    ExecutionRing,
    ReversibilityLevel,
    ActionClassifier,
    RingEnforcer,
    RingElevationManager,
)
from hypervisor.rings.classifier import ActionDescriptor
from hypervisor.rings.elevation import RingElevationError


agent_did = "did:mesh:l11-agent"
session_id = "l11-session-001"

classifier = ActionClassifier()
enforcer = RingEnforcer()
elevation_mgr = RingElevationManager()


def mk_action(name: str, is_read_only: bool, is_admin: bool, reversibility: ReversibilityLevel) -> ActionDescriptor:
    return ActionDescriptor(
        action_id=name,
        name=name,
        execute_api=f"tool://{name}",
        is_read_only=is_read_only,
        is_admin=is_admin,
        reversibility=reversibility,
    )


actions = [
    mk_action("web_search", is_read_only=True, is_admin=False, reversibility=ReversibilityLevel.FULL),
    mk_action("read_file", is_read_only=True, is_admin=False, reversibility=ReversibilityLevel.FULL),
    mk_action("delete_file", is_read_only=False, is_admin=False, reversibility=ReversibilityLevel.PARTIAL),
    mk_action("run_command", is_read_only=False, is_admin=False, reversibility=ReversibilityLevel.NONE),
]

print("\n=== Classification ===")
required_rings = {}
for act in actions:
    cls = classifier.classify(act)
    required_rings[act.action_id] = cls.ring
    print(f"{act.action_id:15} -> {cls.ring.name} (risk_weight={cls.risk_weight})")

current_ring = ExecutionRing.RING_3_SANDBOX
eff_score = 60.0  # lower score => lower effective privilege in this model

print("\n=== Baseline Enforcement (RING_3_SANDBOX) ===")
baseline_results = {}
for act in actions:
    decision = enforcer.check(current_ring, act, eff_score)
    baseline_results[act.action_id] = decision
    print(
        f"{act.action_id:15} | required={decision.required_ring.name} "
        f"allowed={decision.allowed} reason={decision.reason}"
    )

target_action_id = "run_command"
target_action = next(a for a in actions if a.action_id == target_action_id)
target_required = required_rings[target_action_id]

print("\n=== Elevation Request ===")
elevation = None
elevation_error = None
try:
    elevation = elevation_mgr.request_elevation(
        agent_did=agent_did,
        session_id=session_id,
        current_ring=current_ring,
        target_ring=target_required,
        ttl_seconds=300,
        attestation="change-ticket:CHG-123",
        reason="L11 controlled elevation test",
    )
except RingElevationError as exc:
    elevation_error = str(exc)
    print("Elevation denied by runtime:", elevation_error)

print("Granted:", elevation is not None)
if elevation:
    print("Elevation ID:", elevation.elevation_id)
    print("Original Ring:", elevation.original_ring.name)
    print("Elevated Ring:", elevation.elevated_ring.name)

effective_ring = elevation_mgr.get_effective_ring(
    agent_did=agent_did,
    session_id=session_id,
    base_ring=current_ring,
)

retry_decision = enforcer.check(effective_ring, target_action, eff_score)

print("\n=== Retry After Elevation ===")
print("Effective ring:", effective_ring.name)
print("Allowed:", retry_decision.allowed, "| Reason:", retry_decision.reason)

print("\n=== Revoke Elevation ===")
if elevation:
    elevation_mgr.revoke_elevation(elevation.elevation_id)
    print("Revoked elevation:", elevation.elevation_id)

post_revoke_ring = elevation_mgr.get_effective_ring(
    agent_did=agent_did,
    session_id=session_id,
    base_ring=current_ring,
)

post_revoke_decision = enforcer.check(post_revoke_ring, target_action, eff_score)

print("Effective ring after revoke:", post_revoke_ring.name)
print("Allowed after revoke:", post_revoke_decision.allowed, "| Reason:", post_revoke_decision.reason)

if elevation is not None:
    assert retry_decision.allowed is True, "Expected target action to pass after elevation"
    assert post_revoke_decision.allowed is False, "Expected target action blocked again after revoke"
    print("\nL11 PASS: classifier + enforcer + elevation workflow verified.")
else:
    assert elevation_error is not None and "community_edition" in elevation_error
    assert retry_decision.allowed is False
    assert post_revoke_decision.allowed is False
    print("\nL11 PASS (Community Edition): classification + enforcement verified, and elevation denial path validated.")

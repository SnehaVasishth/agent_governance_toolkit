from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from agent_runtime import KillSwitch, QuarantineManager
from hypervisor.liability.quarantine import QuarantineReason
from hypervisor.security.kill_switch import KillReason


@dataclass
class AuditEvent:
    at: datetime
    event_type: str
    agent_did: str
    session_id: str
    payload: dict[str, Any]


def run_l13_demo() -> None:
    kill_switch = KillSwitch()
    quarantine_mgr = QuarantineManager()

    audit_log: list[AuditEvent] = []
    terminated_agents: set[str] = set()

    risky_agent = "did:mesh:risky-agent"
    safe_substitute = "did:mesh:safe-substitute"
    isolated_agent = "did:mesh:isolated-agent"
    session_with_substitute = "sess-l13-001"
    session_without_substitute = "sess-l13-002"

    def make_terminate_cb(agent_did: str):
        def _cb() -> None:
            terminated_agents.add(agent_did)
            print(f"TERMINATED PROCESS CALLBACK => {agent_did}")

        return _cb

  
    kill_switch.register_agent(risky_agent, make_terminate_cb(risky_agent))
    
    kill_switch.register_agent(isolated_agent, make_terminate_cb(isolated_agent))
    kill_switch.register_agent(safe_substitute, make_terminate_cb(safe_substitute))
    
    kill_switch.register_substitute(session_with_substitute, safe_substitute)

    forensic = {
        "ring_breach_score": 0.97,
        "violations": ["attempted_tool_escalation", "policy_bypass_probe"],
        "source": "runtime_anomaly_detector",
    }

    quarantine_record = quarantine_mgr.quarantine(
        agent_did=risky_agent,
        session_id=session_with_substitute,
        reason=QuarantineReason.RING_BREACH,
        details="High-confidence ring breach during privileged tool execution",
        duration_seconds=600,
        forensic_data=forensic,
    )

    audit_log.append(
        AuditEvent(
            at=datetime.now(UTC),
            event_type="quarantine_requested",
            agent_did=risky_agent,
            session_id=session_with_substitute,
            payload={
                "quarantine_id": quarantine_record.quarantine_id,
                "reason": quarantine_record.reason.value,
                "details": quarantine_record.details,
                "forensic": forensic,
                "active": quarantine_record.is_active,
            },
        )
    )

    in_flight_steps = [
        {"step_id": "step-ship-1", "saga_id": "saga-ord-1001"},
        {"step_id": "step-ship-2", "saga_id": "saga-ord-1001"},
    ]

    kill_result_handoff = kill_switch.kill(
        agent_did=risky_agent,
        session_id=session_with_substitute,
        reason=KillReason.RING_BREACH,
        in_flight_steps=in_flight_steps,
        details="Emergency containment after runtime breach detection",
    )

    audit_log.append(
        AuditEvent(
            at=datetime.now(UTC),
            event_type="kill_triggered",
            agent_did=risky_agent,
            session_id=session_with_substitute,
            payload={
                "kill_id": kill_result_handoff.kill_id,
                "reason": kill_result_handoff.reason.value,
                "terminated": kill_result_handoff.terminated,
                "handoff_success_count": kill_result_handoff.handoff_success_count,
                "compensation_triggered": kill_result_handoff.compensation_triggered,
            },
        )
    )

    quarantine_mgr.quarantine(
        agent_did=isolated_agent,
        session_id=session_without_substitute,
        reason=QuarantineReason.BEHAVIORAL_DRIFT,
        details="Repeated unsafe output behavior",
        duration_seconds=300,
    )

    kill_result_compensate = kill_switch.kill(
        agent_did=isolated_agent,
        session_id=session_without_substitute,
        reason=KillReason.BEHAVIORAL_DRIFT,
        in_flight_steps=[{"step_id": "step-billing-1", "saga_id": "saga-ord-2001"}],
        details="Emergency kill with no eligible substitute",
    )

    audit_log.append(
        AuditEvent(
            at=datetime.now(UTC),
            event_type="kill_triggered",
            agent_did=isolated_agent,
            session_id=session_without_substitute,
            payload={
                "kill_id": kill_result_compensate.kill_id,
                "reason": kill_result_compensate.reason.value,
                "terminated": kill_result_compensate.terminated,
                "handoff_success_count": kill_result_compensate.handoff_success_count,
                "compensation_triggered": kill_result_compensate.compensation_triggered,
            },
        )
    )

    print("\n=== L13 Scenario 1: Kill With Substitute Handoff ===")
    print("kill_id:", kill_result_handoff.kill_id)
    print("terminated:", kill_result_handoff.terminated)
    print("handoff_success_count:", kill_result_handoff.handoff_success_count)
    print("compensation_triggered:", kill_result_handoff.compensation_triggered)
    print("handoff statuses:", [h.status.value for h in kill_result_handoff.handoffs])

    print("\n=== L13 Scenario 2: Kill Without Substitute (Compensation Path) ===")
    print("kill_id:", kill_result_compensate.kill_id)
    print("terminated:", kill_result_compensate.terminated)
    print("handoff_success_count:", kill_result_compensate.handoff_success_count)
    print("compensation_triggered:", kill_result_compensate.compensation_triggered)
    print("handoff statuses:", [h.status.value for h in kill_result_compensate.handoffs])

    print("\n=== Quarantine History (Preview Behavior) ===")
    for rec in quarantine_mgr.get_history():
        print(
            f"quarantine_id={rec.quarantine_id} agent={rec.agent_did} "
            f"session={rec.session_id} reason={rec.reason.value} active={rec.is_active}"
        )

    print("\n=== Audit Events ===")
    for ev in audit_log:
        print(
            f"{ev.at.isoformat()} | {ev.event_type} | agent={ev.agent_did} "
            f"session={ev.session_id} payload={ev.payload}"
        )

    assert risky_agent in terminated_agents
    assert isolated_agent in terminated_agents

    assert kill_result_handoff.terminated is True
    assert kill_result_handoff.handoff_success_count == 2
    assert kill_result_handoff.compensation_triggered is False

    assert kill_result_compensate.terminated is True
    assert kill_result_compensate.handoff_success_count == 0
    assert kill_result_compensate.compensation_triggered is True

    # Public Preview note: quarantine is logged but not actively enforced.
    assert quarantine_mgr.is_quarantined(risky_agent, session_with_substitute) is False
    assert quarantine_record.is_active is False

    print("\nL13 PASS: kill switch containment + quarantine/audit flow verified.")


if __name__ == "__main__":
    run_l13_demo()

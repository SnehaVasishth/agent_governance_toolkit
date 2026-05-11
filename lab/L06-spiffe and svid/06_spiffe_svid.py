from agentmesh import AgentIdentity
from agentmesh.identity.spiffe import SPIFFERegistry, SVID
from agent_os import PolicyEngine
from agent_control_plane import Condition, ConditionalPermission

def infer_env_from_workload_path(workload_path: str) -> str:
    p = workload_path.lower()
    if "/prod/" in p or p.endswith("/prod"):
        return "prod"
    return "dev"

def map_svid_to_context(svid: SVID, workload_path: str) -> dict:
    return {
        "agent_did": svid.agent_did,
        "spiffe_id": svid.spiffe_id,
        "trust_domain": svid.trust_domain,
        "workload_path": workload_path,
        "env": infer_env_from_workload_path(workload_path),
    }
    
def build_policy(agent_role:str,context:dict)->PolicyEngine :
    policy=PolicyEngine()
    policy.add_constraint(
        role=agent_role,
        allowed_tools= ["web_search","read_file","delete_file"],
    )
    
    delete_file_prod_only= ConditionalPermission(
        tool_name="delete_file",
        conditions= [Condition(attribute_path="env",operator="eq",value="prod")],
        require_all=True,
    )
    policy.add_conditional_permission(agent_role,delete_file_prod_only)
    policy.set_agent_context(agent_role,context)
    policy.freeze()
    return policy

def is_allowed(policy:PolicyEngine, agent_role:str,tool:str, args:dict)-> tuple[bool,str]:
    violation = policy.check_violation(agent_role, tool, args)
    return (violation is None, violation or "allowed")

def main()-> None:
    print("\n=== L07: SPIFFE/SVID Importance Demo ===\n")
    dev_agent=AgentIdentity.create(
        name="l07-dev-agent",
        sponsor="snehav@leewayhertz.com",
        capabilities=["web_search", "read_file", "delete_file"],
        organization="dev",
        description= "Dev workload identity",
    )
    dev_role= str(dev_agent.did)
    
    registry= SPIFFERegistry(trust_domain="agentmesh.local")
    
    dev_spiffe=registry.register(
        agent_did=dev_role,
        agent_name=dev_agent.name,
        organization=dev_agent.organization
    )
    dev_svid= dev_spiffe.issue_svid(
        ttl_hours=1,
        svid_type="x509"
    )
    dev_svid_valid= registry.validate_svid(dev_svid)
    
    print("DEV Agent DID:", dev_agent.did)
    print("DEV SPIFFE ID", dev_spiffe.spiffe_id)
    print("DEV workload path:",dev_spiffe.workload_path)
    print("DEV SVID Valid:",dev_svid_valid)
    
    if not dev_svid_valid:
        raise RuntimeError("DEV SVID invalid; cannot continue demo")
    
    
    spoofed_context={
        "agent_did": dev_role,
        "env" : "prod",
        "source": "untrusted-caller-input",
    }
    insecure_policy= build_policy(dev_role,spoofed_context)
    insecure_allowed, insecure_reason = is_allowed(
        insecure_policy, dev_role, "delete_file", {"path": r"C:\project\data.txt"}
        
    )
    print("context used",spoofed_context)
    print("delete_file allowed:", insecure_allowed)
    print("reason:",insecure_reason)
    
    trusted_context =map_svid_to_context(dev_svid,dev_spiffe.workload_path)
    secure_policy= build_policy(dev_role,trusted_context)
    secure_allowed,secure_reason= is_allowed(
        secure_policy, dev_role, "delete_file",{"path": r"C:\project\data.txt"}
    )
    print("\n[SECURE PATH - validated SPIFFE/SVID claims]")
    print("delete_file allowed:",secure_allowed)
    print("reason:",secure_reason)
    
    wrong_registry= SPIFFERegistry(trust_domain="other.local")
    wrong_domain_valid= wrong_registry.validate_svid(dev_svid)
    
    print("\n[TRUST DOMAIN CHECK]")
    print("SVID valid under wrong trust domain:", wrong_domain_valid)
    
    assert insecure_allowed, (
        "Expected insecure path to be vulnerable (spoofed env=prod should pass)"
    )
    
    assert not secure_allowed, (
        "Expected secure path to deny delete_file for dev workload"
    )
    assert not wrong_domain_valid, (
        "Expected SVID to fail validation in wrong trust domain"
    )
    
    print("\nRESULT:")
    print("INSECURE_PATH_ALLOWED =", insecure_allowed)
    print("SECURE_PATH_ALLOWED   =", secure_allowed)
    print("WRONG_DOMAIN_VALID    =", wrong_domain_valid)
    print("\nL07 PASS: You can now see why SPIFFE/SVID is required.")
    print("It prevents policy decisions from trusting spoofable caller claims.\n")

if __name__ == "__main__":
    main()
    
    
    
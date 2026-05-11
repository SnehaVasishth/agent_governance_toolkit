import json
from agentmesh import AgentMeshClient
from pathlib import Path
policy_path = Path(__file__).with_name("policy.yaml")
policy_yaml = policy_path.read_text(encoding="utf-8")

def audit_to_dict(audit_entry):
    if audit_entry is None:
        return None
    if hasattr(audit_entry, "model_dump"):
        return audit_entry.model_dump()
    if hasattr(audit_entry, "dict"):
        return audit_entry.dict()
    if isinstance(audit_entry, dict):
        return audit_entry
    return {"raw": str(audit_entry)}

client = AgentMeshClient(
    agent_id="l10-agent",
    capabilities=["web_search","read_file"],
    policy_yaml=policy_yaml,
    trust_config={
        "initial_score":500,
        "success_delta": 10,
        "failure_delta" : -20
    },
)

cases = [
    ("web_search", {"query": "OWASP Agentic Top 10"}),
    ("delete_file", {"path": r"C:\project\data.txt"}),
]

results=[]

for action,ctx in cases:
    result=client.execute_with_governance(action,ctx)
    results.append((action,ctx,result))
    
    
for action, ctx, result in results:
    print("\n=== Action ===")
    print("action:", action)
    print("context:", ctx)
    print("decision:", result.decision)
    print("allowed:", result.allowed)
    print("trust_score_after:", result.trust_score)
    print("audit_entry:", json.dumps(audit_to_dict(result.audit_entry), indent=2, default=str))

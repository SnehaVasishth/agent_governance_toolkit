from datetime import datetime, timezone
from agentmesh import AgentIdentity, CredentialManager

agent= AgentIdentity.create(
    name="l05-agent",
    sponsor= "snehav@leewayhertz.com",
    capabilities=["web_search","read_file"],
    organization= "zbrain-labs",
    description="L05 identity lab agent",
    
)

print("DID:", str(agent.did))
print("Key id:",agent.verification_key_id)
print("status:",agent.status)

payload=f"L05 credential flow @ {datetime.now(timezone.utc).isoformat()}".encode("utf-8")
signature= agent.sign(payload)
is_valid_sig= agent.verify_signature(payload,signature)

cred_mgr= CredentialManager(default_ttl=900)

cred=cred_mgr.issue(
    agent_did= str(agent.did),
    capabilities=["web_search"],
    resources=["docs/*"],
    ttl_seconds=600,
    issued_for= "L05 demo"
)
print("credential Id:", cred.credential_id)
print("credential status:", cred.status)
print("credential valid now:",cred.is_valid())


token= cred.to_bearer_token()
validated_cred= cred_mgr.validate(token)

print("Token validated:", validated_cred is not None)
print("Validated credential id:", validated_cred.credential_id if validated_cred else None)


rotated= cred_mgr.rotate(cred.credential_id)
print("rotated created:", rotated is not None)
print("after rotattion", rotated)
if rotated:
    print("New credential ID:", rotated.credential_id)
    print("Previous credential ID:", rotated.previous_credential_id)
    
target_id= rotated.credential_id if rotated else cred.credential_id
revoked= cred_mgr.revoke(target_id,reason="L05 revocation test")


print("revoked",revoked)
token_after_revoke= rotated.to_bearer_token() if rotated else cred.to_bearer_token()
validated_after_revoke = cred_mgr.validate(token_after_revoke)
print("token valid after revoke:", validated_after_revoke is not None)
active = cred_mgr.get_active_for_agent(str(agent.did))
print("Active credentials for agent:", len(active))
for c in active:
    print("-", c.credential_id, c.status, c.expires_at)

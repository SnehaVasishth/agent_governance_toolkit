# Agent Governance Toolkit - MAF-First Hands-on Roadmap

This version is aligned to your mind map and your preference to build PoCs using Microsoft Agent Framework.

Validated local environment:
- `agent_governance_toolkit=3.3.0`
- `agent_os_kernel=3.3.0`
- `agentmesh_platform=3.3.0`
- `agent_hypervisor=3.3.0`
- `agentmesh-runtime=2.3.0`
- `agent_sre=3.3.0`
- `agent-framework=1.2.2`

## 1) Mind Map Coverage Matrix

Every concept in your mind map is now explicitly mapped to labs:

1. Policy Engine
- Deterministic enforcement: `L01`, `L02`, `L03`
- YAML policy: `L02`
- OPA/Rego support: `L04`
- Cedar support: `L04`

2. Zero-Trust Identity
- Ed25519 credentials: `L05`
- ML-DSA-65 credentials: `L06`
- SPIFFE/SVID integration: `L07`
- Trust scoring: `L08`

3. Execution Sandboxing
- 4-tier privilege rings: `L11`
- Saga orchestration: `L12`
- Kill switch control: `L13`

4. Agent SRE
- SLOs & error budgets: `L14`
- Circuit breakers: `L15`
- Chaos engineering: `L16`

5. Security Scanners (OWASP Agentic Top 10 coverage)
- MCP security scanner: `L09`
- Shadow AI discovery: `L17`
- Contributor reputation: `L18`

6. Ecosystem & Integrations
- Microsoft Agent Framework: `L19`, `L20`, `L21`, `L22`
- Semantic Kernel: `L23`
- LangChain/LangGraph: `L24`
- CrewAI & AutoGen: `L25`
- OpenAI Agents SDK: `L26`

7. Cloud Platforms
- Azure AI Foundry: `L27`
- AWS Bedrock: `L28`
- Google ADK: `L29`

8. Technical Implementation
- Language SDKs (Python/TS/.NET/Rust/Go): `L30`
- Performance (<0.1ms and throughput characterization): `L31`
- Security model (application governance, middleware, deterministic vs probabilistic): `L03`, `L20`, `L32`

## 2) Lab Sequence (MAF-First)

## Foundation Track

### L00 - Package and Namespace Mapping
Goal: map pip packages to import namespaces and CLIs.
Hands-on:
1. Verify package versions with `pip show`.
2. Run `agent-os`, `agentmesh`, `hypervisor`, `agent-sre`, `agent-compliance` help commands.
Deliverable: `notes/00-package-map.md`.

### L01 - Kernel Interception Basics
Goal: deterministic allow/deny for tool actions.
Hands-on:
1. Use `KernelSpace`, `PolicyEngine`, `SyscallType`.
2. Execute one allowed and one blocked tool call.
Deliverable: `labs/01_kernel_enforcement.py`.

### L02 - Policy-as-Code Lifecycle
Goal: policy validation, testing, and drift control.
Hands-on:
1. Create `policies/base.yaml` and `policies/strict.yaml`.
2. Use `agent-os policy validate/test/diff`.
Deliverable: `policies/` + scenario tests.

### L03 - Deterministic vs Probabilistic Governance
Goal: compare hard policy enforcement with LLM moderation decisions.
Hands-on:
1. Route same requests through deterministic policy and probabilistic classifier.
2. Measure disagreement cases and risk.
Deliverable: `labs/03_deterministic_vs_probabilistic.md`.

### L04 - OPA/Rego and Cedar Policy Interop
Goal: evaluate policy portability patterns.
Hands-on:
1. Model one policy in YAML, Rego-like form, and Cedar-like form.
2. Build translation checks and decision equivalence tests.
Deliverable: `labs/04_policy_interop/`.

## Identity and Trust Track

### L05 - Ed25519 Identity and Credential Flow
Goal: create agent DID and sign/verify credentials.
Hands-on:
1. Use `agentmesh` identity primitives.
2. Validate credential lifecycle states.
Deliverable: `labs/05_identity_ed25519.py`.

### L06 - ML-DSA-65 Readiness Pattern
Goal: test crypto-agile identity abstraction for PQ transition.
Hands-on:
1. Add algorithm metadata and verification strategy hooks.
2. Run compatibility tests across signature schemes.
Deliverable: `labs/06_crypto_agility.md`.

### L07 - SPIFFE/SVID Integration Drill
Goal: bridge workload identity to agent identity.
Hands-on:
1. Map SVID identity claims to agent DID/session policy.
2. Enforce authorization from mapped claims.
Deliverable: `labs/07_spiffe_svid_bridge.py`.

### L08 - Trust Scoring and Revocation
Goal: trust evolution and governance feedback loop.
Hands-on:
1. `agentmesh trust list/inspect/graph/attest/revoke`.
2. Observe score deltas on success/failure events.
Deliverable: `artifacts/08_trust_timeline.json`.

## Runtime and Isolation Track

### L09 - MCP Security Scanner and Response Scanner
Goal: detect tool poisoning and unsafe responses.
Hands-on:
1. `MCPSecurityScanner` for tool metadata.
2. `MCPResponseScanner` for output threats.
Deliverable: `labs/09_mcp_security.py`.

### L10 - Unified Governance Loop (Policy + Audit + Trust)
Goal: single call path via governance client.
Hands-on:
1. Wrap actions with `AgentMeshClient.execute_with_governance`.
2. Track decision, audit entry, trust update.
Deliverable: `labs/10_unified_governance_loop.py`.

### L11 - 4-Tier Privilege Rings
Goal: enforce ring-based action classification and elevation.
Hands-on:
1. Use `ExecutionRing`, `RingEnforcer`, `RingElevationManager`.
2. Trigger valid/invalid ring elevation flows.
Deliverable: `labs/11_execution_rings.py`.

### L12 - Saga Orchestration and Compensation
Goal: transactional workflow safety.
Hands-on:
1. Build a multi-step saga.
2. Inject failure and verify compensation path.
Deliverable: `labs/12_saga_rollback.py`.

### L13 - Kill Switch and Quarantine Controls
Goal: emergency containment.
Hands-on:
1. Trigger kill switch on risky session.
2. Quarantine and audit affected identity/session.
Deliverable: `labs/13_kill_switch_quarantine.py`.

## Reliability and Compliance Track

### L14 - SLOs and Error Budgets
Goal: reliability targets for agent systems.
Hands-on:
1. Define SLI + SLO + error budget.
2. Simulate budget burn transitions.
Deliverable: `labs/14_slo_budget.py`.

### L15 - Circuit Breakers for Agent Flows
Goal: protect downstream systems and control cascading failures.
Hands-on:
1. Configure circuit breaker thresholds.
2. Simulate trip/recover cycles.
Deliverable: `labs/15_circuit_breakers.py`.

### L16 - Chaos and Adversarial Governance Testing
Goal: resilience against governance bypass attempts.
Hands-on:
1. Run adversarial policy vectors.
2. Run replay/golden comparison.
Deliverable: `labs/16_chaos_adversarial.py`.

### L17 - Shadow AI Discovery
Goal: detect unmanaged agent/tool usage paths.
Hands-on:
1. Scan code/config for unmanaged model/tool endpoints.
2. Tag and report shadow AI findings.
Deliverable: `artifacts/17_shadow_ai_report.md`.

### L18 - Contributor Reputation and Supply Chain Signals
Goal: tie artifact trust to provenance and contributor quality.
Hands-on:
1. Combine integrity manifest with contributor/release metadata.
2. Build promotion gate policy.
Deliverable: `labs/18_contributor_reputation_gate.py`.

## Microsoft Agent Framework Track (Primary PoC Track)

### L19 - Create MAF Agent with Governed Tools
Goal: standard MAF agent with Agent OS policy wrapper.
Hands-on:
1. Build agent using `agent_framework`.
2. Route tool execution through `KernelSpace`/`PolicyEngine`.
Deliverable: `maf_labs/19_maf_governed_agent.py`.

### L20 - Middleware Integration Pattern
Goal: application-level governance middleware for MAF.
Hands-on:
1. Add request/response interception middleware.
2. Log policy decisions and violations.
Deliverable: `maf_labs/20_maf_middleware.py`.

### L21 - MAF + AgentMesh Trust-Aware Delegation
Goal: only trusted agents can delegate sensitive tasks.
Hands-on:
1. Register MAF agent identities in AgentMesh.
2. Enforce trust threshold for handoff.
Deliverable: `maf_labs/21_maf_trust_delegation.py`.

### L22 - MAF + Runtime Isolation + SRE
Goal: production-ready PoC control loop.
Hands-on:
1. Run MAF workflows under rings/saga controls.
2. Attach SLO monitoring and kill-switch policies.
Deliverable: `maf_labs/22_maf_runtime_sre.py`.

## Cross-Framework Interop Track

### L23 - Semantic Kernel Adapter Lab
Goal: governance parity check with Semantic Kernel.
Deliverable: `interop_labs/23_semantic_kernel_adapter.py`.

### L24 - LangChain / LangGraph Adapter Lab
Goal: governance parity check with LangChain/LangGraph.
Deliverable: `interop_labs/24_langchain_langgraph_adapter.py`.

### L25 - CrewAI & AutoGen Adapter Lab
Goal: governance parity check with multi-agent frameworks.
Deliverable: `interop_labs/25_crewai_autogen_adapter.py`.

### L26 - OpenAI Agents SDK Adapter Lab
Goal: compare enforcement flow with OpenAI Agents SDK.
Deliverable: `interop_labs/26_openai_agents_adapter.py`.

## Cloud Platform Track

### L27 - Azure AI Foundry Governance Path
Goal: policy, trust, and SRE around Foundry-hosted agent path.
Deliverable: `cloud_labs/27_azure_foundry.md`.

### L28 - AWS Bedrock Governance Path
Goal: apply same control pattern for Bedrock stack.
Deliverable: `cloud_labs/28_aws_bedrock.md`.

### L29 - Google ADK Governance Path
Goal: apply same control pattern for Google ADK path.
Deliverable: `cloud_labs/29_google_adk.md`.

## Technical Depth Track

### L30 - Language SDK Parity Matrix
Goal: map Python/TypeScript/.NET/Rust/Go capabilities and gaps.
Deliverable: `notes/30_sdk_parity_matrix.md`.

### L31 - Performance Benchmark Lab
Goal: measure policy decision latency and throughput in your setup.
Hands-on:
1. Micro-benchmark deterministic checks.
2. Stress test governance loop throughput.
Deliverable: `artifacts/31_perf_benchmarks.json`.

### L32 - Security Model Validation
Goal: validate app-level governance + middleware enforcement assumptions.
Hands-on:
1. Simulate bypass attempts at app, middleware, and tool layers.
2. Verify deterministic controls always dominate.
Deliverable: `artifacts/32_security_model_validation.md`.

## 3) Suggested Execution Order

1. Week 1: `L00-L05` (foundation + policy + identity basics)
2. Week 2: `L06-L13` (identity depth + runtime isolation + kill switch)
3. Week 3: `L14-L18` (SRE + compliance + security scanners)
4. Week 4: `L19-L22` (Microsoft Agent Framework core PoC track)
5. Week 5 (optional): `L23-L32` (interop + cloud + perf + security depth)

## 4) Minimum Set for Your Immediate MAF PoCs

If you want fastest path first, do this subset:
1. `L01`, `L02`, `L05`, `L08`
2. `L11`, `L12`, `L13`
3. `L14`, `L15`, `L16`
4. `L19`, `L20`, `L21`, `L22`

## 5) Project-Specific Notes

1. [policy_example.py](d:/ZBrain_Project/agent_governance_toolkit_poc/policy_example.py) currently has an incomplete import and should be fixed before running labs.
2. [agent.py](d:/ZBrain_Project/agent_governance_toolkit_poc/agent.py) is a good starting seed for `L01` and `L19`.
3. In this environment, package artifact versions can show `3.3.0` while some module `__version__` values show `3.2.2`; track deployment versions via `pip show`.

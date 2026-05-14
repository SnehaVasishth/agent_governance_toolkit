from agent_sre.slo.indicators import TaskSuccessRate, ResponseLatency
from agent_sre.slo.objectives import ErrorBudget, SLO
from agent_sre.slo.dashboard import SLODashboard, ReportPeriod


def print_status(label: str, slo: SLO, latency_sli: ResponseLatency) -> None:
    print(f"\n[{label}]")
    print("status:", slo.evaluate().value)
    print("remaining_budget_percent:", round(slo.error_budget.remaining_percent, 2))
    print("consumed_budget_units:", round(slo.error_budget.consumed, 2))
    print("burn_rate:", round(slo.error_budget.burn_rate(), 2))
    print("firing_alerts:", [a.name for a in slo.error_budget.firing_alerts()])
    print("latency_p95_current_ms:", latency_sli.current_value())


def run_phase(
    phase_name: str,
    events: int,
    fail_rate: float,
    latency_ms: float,
    slo: SLO,
    success_sli: TaskSuccessRate,
    latency_sli: ResponseLatency,
    dashboard: SLODashboard,
) -> None:
    failures = int(events * fail_rate)

    for i in range(events):
        is_good = i >= failures
        success_sli.record_task(success=is_good, metadata={"phase": phase_name})
        latency_sli.record_latency(latency_ms, metadata={"phase": phase_name})
        slo.record_event(good=is_good)

    dashboard.take_snapshot()
    print_status(phase_name, slo, latency_sli)


def main() -> None:
    success_sli = TaskSuccessRate(target=0.99, window="30d")
    latency_sli = ResponseLatency(target_ms=1200.0, percentile=0.95, window="1h")

    budget = ErrorBudget(
        total=100.0,
        window_seconds=3600,
        burn_rate_alert=5.0,
        burn_rate_critical=8.0,
    )

    slo = SLO(
        name="agent_reliability_slo",
        indicators=[success_sli, latency_sli],
        error_budget=budget,
        description="Task success + latency reliability objective",
        labels={"service": "orchestrator", "env": "lab"},
    )

    dashboard = SLODashboard()
    dashboard.register_slo(slo)

    run_phase("phase_1_healthy", 100, 0.01, 500, slo, success_sli, latency_sli, dashboard)
    run_phase("phase_2_warning_burn", 80, 0.20, 900, slo, success_sli, latency_sli, dashboard)
    run_phase("phase_3_critical_burn", 80, 0.70, 1500, slo, success_sli, latency_sli, dashboard)

    while not slo.error_budget.is_exhausted:
        success_sli.record_task(success=False, metadata={"phase": "phase_4_exhaust"})
        latency_sli.record_latency(2200, metadata={"phase": "phase_4_exhaust"})
        slo.record_event(good=False)

    dashboard.take_snapshot()
    print_status("phase_4_exhausted", slo, latency_sli)

    print("\n[dashboard_summary]", dashboard.health_summary())

    dashboard.record_compliance(
        slo_name=slo.name,
        period=ReportPeriod.DAY,
        compliant=not slo.error_budget.is_exhausted,
        budget_consumed_percent=(slo.error_budget.consumed / slo.error_budget.total) * 100.0,
        avg_burn_rate=slo.error_budget.burn_rate(),
        incidents=1 if slo.error_budget.is_exhausted else 0,
    )

    report = dashboard.compliance_report(slo_name=slo.name, period=ReportPeriod.DAY)
    print("[compliance_report_count]", len(report))

    assert slo.evaluate().value == "exhausted"
    assert slo.error_budget.remaining_percent == 0.0
    assert len(dashboard.snapshots_in_range(slo_name=slo.name)) >= 4

    print("\nL14 PASS: SLI + SLO + error budget burn transitions verified.")


if __name__ == "__main__":
    main()

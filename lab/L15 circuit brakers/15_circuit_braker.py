import time
from agent_sre.cascade.circuit_breaker import   CascadeDetector, CircuitBreaker,CircuitBreakerConfig, CircuitOpenError,



def print_breaker(label: str, breaker: CircuitBreaker) -> None:
    print(f"[{label}] state={breaker.state} failures={breaker.failure_count}")


def downstream_fail() -> str:
    raise RuntimeError("downstream dependency failed")


def downstream_ok() -> str:
    return "ok"


def main() -> None:
 
    cfg = CircuitBreakerConfig(
        failure_threshold=3,
        recovery_timeout_seconds=1.5,
        half_open_max_calls=1,
    )

  
    cb = CircuitBreaker(agent_id="agent-A", config=cfg)
    print_breaker("start", cb)

    for _ in range(3):
        try:
            cb.call(downstream_fail)
        except RuntimeError:
            pass

    print_breaker("after_trip", cb)

  
    try:
        cb.call(downstream_ok)
    except CircuitOpenError as exc:
        print("open_blocked_retry_after_seconds:", round(exc.retry_after, 2))

    print("waiting_for_recovery_window...")
    time.sleep(1.6)
    print("state_after_timeout:", cb.get_state().value)

    probe_result = cb.call(downstream_ok)
    print("half_open_probe_result:", probe_result)
    print_breaker("after_recovery", cb)

   
    for _ in range(3):
        try:
            cb.call(downstream_fail)
        except RuntimeError:
            pass
    print_breaker("trip_again", cb)

    time.sleep(1.6)
    print("state_after_timeout_again:", cb.get_state().value)

    try:
        cb.call(downstream_fail) 
    except RuntimeError:
        pass
    print_breaker("half_open_failed_reopen", cb)

    
    agents = ["agent-A", "agent-B", "agent-C"]
    detector = CascadeDetector(agents=agents, cascade_threshold=2, config=cfg)

    for agent_id in ["agent-A", "agent-B"]:
        breaker = detector.get_breaker(agent_id)
        for _ in range(3):
            try:
                breaker.call(downstream_fail)
            except RuntimeError:
                pass

    print("affected_agents:", detector.get_affected_agents())
    print("cascade_detected:", detector.check_cascade())

    # 9) Lab checks.
    assert cb.state == "OPEN"
    assert detector.check_cascade() is True

    print("L15 PASS: trip/recover cycles and cascade detection verified.")


if __name__ == "__main__":
    main()

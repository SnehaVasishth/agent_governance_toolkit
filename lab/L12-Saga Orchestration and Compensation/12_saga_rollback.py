import asyncio
from dataclasses import dataclass, field
from typing import Any, Callable

from agent_runtime import SagaOrchestrator, SagaState, StepState


@dataclass
class OrderState:
    """In-memory state so we can observe forward actions and compensation."""

    inventory_reserved: bool = False
    payment_charged: bool = False
    shipment_created: bool = False
    ledger: list[str] = field(default_factory=list)


def reserve_inventory(state: OrderState, order_id: str) -> dict[str, Any]:
    state.inventory_reserved = True
    state.ledger.append(f"reserve_inventory:{order_id}")
    return {"ok": True, "step": "reserve_inventory", "order_id": order_id}


def release_inventory(state: OrderState, order_id: str) -> dict[str, Any]:
    state.inventory_reserved = False
    state.ledger.append(f"release_inventory:{order_id}")
    return {"ok": True, "step": "release_inventory", "order_id": order_id}


def charge_payment(state: OrderState, order_id: str) -> dict[str, Any]:
    state.payment_charged = True
    state.ledger.append(f"charge_payment:{order_id}")
    return {"ok": True, "step": "charge_payment", "order_id": order_id}


def refund_payment(state: OrderState, order_id: str, fail_refund: bool = False) -> dict[str, Any]:
    if fail_refund:
        raise RuntimeError("payment gateway refund timeout")
    state.payment_charged = False
    state.ledger.append(f"refund_payment:{order_id}")
    return {"ok": True, "step": "refund_payment", "order_id": order_id}


def create_shipment(state: OrderState, order_id: str, inject_failure: bool = True) -> dict[str, Any]:
    if inject_failure:
        raise RuntimeError("courier service unavailable")
    state.shipment_created = True
    state.ledger.append(f"create_shipment:{order_id}")
    return {"ok": True, "step": "create_shipment", "order_id": order_id}


def cancel_shipment(state: OrderState, order_id: str) -> dict[str, Any]:
    state.shipment_created = False
    state.ledger.append(f"cancel_shipment:{order_id}")
    return {"ok": True, "step": "cancel_shipment", "order_id": order_id}


async def run_step(
    orchestrator: SagaOrchestrator,
    saga_id: str,
    step_id: str,
    fn: Callable[[], dict[str, Any]],
) -> dict[str, Any]:
    return await orchestrator.execute_step(saga_id=saga_id, step_id=step_id, executor=lambda: asyncio.to_thread(fn))


async def execute_order_saga(
    *,
    order_id: str,
    inject_shipping_failure: bool,
    inject_refund_failure: bool,
) -> None:
    orchestrator = SagaOrchestrator()
    state = OrderState()

    saga = orchestrator.create_saga(session_id=f"session-{order_id}")

    reserve_step = orchestrator.add_step(
        saga_id=saga.saga_id,
        action_id="reserve_inventory",
        agent_did="did:mesh:inventory-agent",
        execute_api="tool://inventory/reserve",
        undo_api="tool://inventory/release",
        timeout_seconds=5,
    )

    charge_step = orchestrator.add_step(
        saga_id=saga.saga_id,
        action_id="charge_payment",
        agent_did="did:mesh:payment-agent",
        execute_api="tool://payment/charge",
        undo_api="tool://payment/refund",
        timeout_seconds=5,
    )

    ship_step = orchestrator.add_step(
        saga_id=saga.saga_id,
        action_id="create_shipment",
        agent_did="did:mesh:shipping-agent",
        execute_api="tool://shipping/create",
        undo_api="tool://shipping/cancel",
        timeout_seconds=5,
    )

    step_handlers = {
        reserve_step.step_id: lambda: reserve_inventory(state, order_id),
        charge_step.step_id: lambda: charge_payment(state, order_id),
        ship_step.step_id: lambda: create_shipment(
            state,
            order_id,
            inject_failure=inject_shipping_failure,
        ),
    }

    compensation_handlers = {
        "tool://inventory/release": lambda: release_inventory(state, order_id),
        "tool://payment/refund": lambda: refund_payment(
            state,
            order_id,
            fail_refund=inject_refund_failure,
        ),
        "tool://shipping/cancel": lambda: cancel_shipment(state, order_id),
    }

    print(f"\n=== L12 Saga Run: order={order_id} ===")
    print("Initial state:", state)

    try:
        for step in saga.steps:
            result = await run_step(orchestrator, saga.saga_id, step.step_id, step_handlers[step.step_id])
            print(f"FORWARD OK  | {step.action_id:17} | result={result}")

        saga.transition(SagaState.COMPLETED)
        print("Saga completed with no rollback.")

    except Exception as forward_error:
        print(f"FORWARD FAIL| error={forward_error}")
        failed_steps = await orchestrator.compensate(
            saga_id=saga.saga_id,
            compensator=lambda step: asyncio.to_thread(compensation_handlers[step.undo_api]),
        )

        if failed_steps:
            print("Compensation had failures. Saga escalated.")
        else:
            print("Compensation succeeded. Saga safely rolled back.")

    print("Final saga state:", saga.state.value)
    print("Final order state:", state)

    print("Step states:")
    for step in saga.steps:
        print(
            f"- {step.action_id:17} state={step.state.value:21} "
            f"undo={step.undo_api} error={step.error}"
        )

    print("Ledger:", state.ledger)

    if inject_shipping_failure and not inject_refund_failure:
        assert saga.state == SagaState.COMPLETED
        assert state.inventory_reserved is False
        assert state.payment_charged is False
        assert state.shipment_created is False
        assert reserve_step.state == StepState.COMPENSATED
        assert charge_step.state == StepState.COMPENSATED

    if inject_shipping_failure and inject_refund_failure:
        assert saga.state == SagaState.ESCALATED
        assert charge_step.state == StepState.COMPENSATION_FAILED


async def main() -> None:
    await execute_order_saga(
        order_id="ORD-1001",
        inject_shipping_failure=True,
        inject_refund_failure=False,
    )

 
    await execute_order_saga(
        order_id="ORD-1002",
        inject_shipping_failure=True,
        inject_refund_failure=True,
    )


if __name__ == "__main__":
    asyncio.run(main())

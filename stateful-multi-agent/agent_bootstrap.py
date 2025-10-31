import sys
import logging
from typing import Tuple, Dict, Any

from composition_root import build_container
from stateful_multi_agent.customer_service_agent.agent import CustomerServiceAgent

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def _seed(container: Dict[str, Any]) -> Dict[str, str]:
    services = container['services']
    # Create a policy
    from application_services.policy_application_service import CreatePolicyCommand
    p = services['policies'].create_policy(CreatePolicyCommand(name="Standard", policy_type="standard", refund_period_days=30))
    # Create two courses
    from application_services.course_application_service import CreateCourseCommand
    c1 = services['courses'].create_course(CreateCourseCommand(title="Course A", description="Intro A", policy_id=p.policy_id))
    c2 = services['courses'].create_course(CreateCourseCommand(title="Course B", description="Intro B", policy_id=p.policy_id))
    # Register a user
    from application_services.user_application_service import RegisterUserCommand
    u = services['users'].register_user(RegisterUserCommand(email="demo@example.com", password="pass", profile={"first":"Demo"}))
    # Place an order for that user
    from application_services.order_application_service import PlaceOrderCommand
    o = services['orders'].place_order(PlaceOrderCommand(user_id=u.user_id, course_ids=[c1.course_id], total_amount=100.0, payment_info={"method":"demo"}))
    return {
        "policy_id": p.policy_id,
        "course_a": c1.course_id,
        "course_b": c2.course_id,
        "user_id": u.user_id,
        "order_id": o.order_id,
    }


def get_agent_and_container() -> Tuple[Any, Dict[str, Any]]:
    container = build_container()
    return CustomerServiceAgent, container


def get_agent_container_and_seed() -> Tuple[Any, Dict[str, Any], Dict[str, str]]:
    agent, container = get_agent_and_container()
    ids = _seed(container)
    return agent, container, ids


def main() -> None:
    agent, container, ids = get_agent_container_and_seed()
    logger.info("Customer Service Agent initialized. Type 'quit' to exit.")
    logger.info(f"Seeded: user={ids['user_id']} courses={[ids['course_a'], ids['course_b']]} policy={ids['policy_id']} order={ids['order_id']}")

    while True:
        try:
            line = input('> ').strip()
        except (EOFError, KeyboardInterrupt):  # pragma: no cover
            print()
            break
        if not line:
            continue
        if line.lower() in ('quit','exit'):
            break
        try:
            print(f"(agent placeholder) You said: {line}")
        except Exception as e:  # pragma: no cover
            print(f"Error: {e}")


if __name__ == '__main__':  # pragma: no cover
    main()

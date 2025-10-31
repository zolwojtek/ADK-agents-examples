import sys
import logging
from typing import Dict, Any

from composition_root import build_container

# Optional: import the customer service agent if available
try:
    from stateful_multi_agent.customer_service_agent.agent import CustomerServiceAgent
except Exception:  # pragma: no cover
    CustomerServiceAgent = None

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger("chat")

HELP = """
Commands:
  help
  quit
  register_user <email>
  create_policy <name> <type> <days>
  create_course <title> <policy_id>
  place_order <user_id> <course_id[,course_id...]>
  request_refund <order_id> <reason>
  grant_access <user_id> <course_id>
  show orders <user_id>
  show access <user_id>
  show catalog
""".strip()


def seed(container: Dict[str, Any]) -> Dict[str, str]:
    services = container['services']
    # Create policy
    from application_services.policy_application_service import CreatePolicyCommand
    pres = services['policies'].create_policy(CreatePolicyCommand(name="Standard", policy_type="standard", refund_period_days=30))
    policy_id = pres.policy_id
    # Create courses
    from application_services.course_application_service import CreateCourseCommand
    cres1 = services['courses'].create_course(CreateCourseCommand(title="Course A", description="Intro", policy_id=policy_id))
    cres2 = services['courses'].create_course(CreateCourseCommand(title="Course B", description="Advanced", policy_id=policy_id))
    # Register user
    from application_services.user_application_service import RegisterUserCommand
    ures = services['users'].register_user(RegisterUserCommand(email="demo@example.com", password="pass", profile={"first":"Demo"}))
    return {"policy_id": policy_id, "course_a": cres1.course_id, "course_b": cres2.course_id, "user_id": ures.user_id}


def parse_and_execute(container: Dict[str, Any], line: str) -> None:
    services = container['services']
    projections = container['projections']

    parts = line.strip().split()
    if not parts:
        return
    cmd = parts[0].lower()

    if cmd == 'help':
        print(HELP)
        return
    if cmd in ('quit', 'exit'):  # pragma: no cover
        sys.exit(0)

    try:
        if cmd == 'register_user':
            email = parts[1]
            from application_services.user_application_service import RegisterUserCommand
            res = services['users'].register_user(RegisterUserCommand(email=email, password='pass', profile={}))
            print(f"User registered: {res.user_id}")

        elif cmd == 'create_policy':
            name, ptype, days = parts[1], parts[2], int(parts[3])
            from application_services.policy_application_service import CreatePolicyCommand
            res = services['policies'].create_policy(CreatePolicyCommand(name=name, policy_type=ptype, refund_period_days=days))
            print(f"Policy created: {res.policy_id}")

        elif cmd == 'create_course':
            title = parts[1]
            policy_id = parts[2]
            from application_services.course_application_service import CreateCourseCommand
            res = services['courses'].create_course(CreateCourseCommand(title=title, description="", policy_id=policy_id))
            print(f"Course created: {res.course_id}")

        elif cmd == 'place_order':
            user_id = parts[1]
            course_ids = parts[2].split(',')
            from application_services.order_application_service import PlaceOrderCommand
            res = services['orders'].place_order(PlaceOrderCommand(user_id=user_id, course_ids=course_ids, total_amount=100.0, payment_info={"method":"demo"}))
            print(f"Order placed: {res.order_id} status={res.status}")

        elif cmd == 'request_refund':
            order_id = parts[1]
            reason = ' '.join(parts[2:]) or 'not satisfied'
            from application_services.order_application_service import RequestRefundCommand
            res = services['orders'].request_refund(RequestRefundCommand(order_id=order_id, refund_reason=reason))
            print(f"Refund: order={res.order_id} status={res.status}")

        elif cmd == 'grant_access':
            user_id, course_id = parts[1], parts[2]
            from application_services.access_application_service import GrantAccessCommand
            res = services['access'].grant_access(GrantAccessCommand(user_id=user_id, course_id=course_id, access_type='enroll'))
            print(f"Access granted: {res.access_id} status={res.status}")

        elif cmd == 'show':
            topic = parts[1].lower()
            if topic == 'orders':
                user_id = parts[2]
                data = projections['order_history'].get_orders_for_user(user_id)
                print({"orders": data})
            elif topic == 'access':
                user_id = parts[2]
                data = projections['user_access'].get_user_access(user_id)
                print(data)
            elif topic == 'catalog':
                data = projections['course_catalog'].get_all()
                print({k: v['title'] for k, v in data.items()})
            else:
                print('Unknown show topic')
        else:
            print('Unknown command. Type help')
    except Exception as e:
        print(f"Error: {e}")


def main():
    container = build_container()
    ids = seed(container)

    if CustomerServiceAgent:
        agent = CustomerServiceAgent()
        logger.info("Customer Service Agent ready. Type 'help' for commands. 'quit' to exit.")
    else:
        agent = None
        logger.info("Chat ready (no main agent module found). Type 'help' for commands. 'quit' to exit.")

    print(f"Seeded: user={ids['user_id']} courses={[ids['course_a'], ids['course_b']]} policy={ids['policy_id']}")

    while True:
        try:
            line = input('> ').strip()
        except (EOFError, KeyboardInterrupt):  # pragma: no cover
            print()
            break
        if not line:
            continue
        # In a richer setup, we would pass through the agent for NLU/intent; here we directly parse
        parse_and_execute(container, line)


if __name__ == '__main__':  # pragma: no cover
    main()

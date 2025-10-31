from typing import Dict, Any

# Event bus
from domain.events.event_bus import EventBus, EventHandler

# AI agent handlers
from ai_agents.order_event_handlers import (
    OrderAnalyticsHandler,
    OrderCustomerServiceHandler,
    OrderFraudDetectionHandler,
)
from ai_agents.access_event_handlers import (
    AccessAnalyticsHandler,
    AccessLearningAssistantHandler,
    AccessEngagementHandler,
)
from ai_agents.course_event_handlers import (
    CourseAnalyticsHandler,
    CourseCatalogHandler,
    CourseQualityHandler,
)
from ai_agents.user_event_handlers import (
    UserAnalyticsHandler,
    UserOnboardingHandler,
    UserSecurityHandler,
)
from ai_agents.policy_event_handlers import (
    PolicyAnalyticsHandler,
    PolicyComplianceHandler,
    PolicyLifecycleHandler,
)

# Repositories (in-memory implementations)
from infrastructure.repositories.order_repository import InMemoryOrderRepository
from infrastructure.repositories.user_repository import InMemoryUserRepository
from infrastructure.repositories.course_repository import InMemoryCourseRepository
from infrastructure.repositories.access_repository import InMemoryAccessRepository
from infrastructure.repositories.policy_repository import InMemoryPolicyRepository

# Application services
from application_services.order_application_service import OrderApplicationService
from application_services.user_application_service import UserApplicationService
from application_services.access_application_service import AccessApplicationService
from application_services.course_application_service import CourseApplicationService
from application_services.policy_application_service import PolicyApplicationService

# Read models / projections
from read_models.user_access_projection import UserAccessProjection
from read_models.course_catalog_projection import CourseCatalogProjection
from read_models.order_history_projection import OrderHistoryProjection
from read_models.policy_usage_projection import PolicyUsageProjection
from read_models.revenue_summary_projection import RevenueSummaryProjection


class ProjectionEventHandler(EventHandler):
    def __init__(self, name: str, projection: Any):
        self._name = name
        self._projection = projection
    @property
    def handler_name(self) -> str:
        return f"projection:{self._name}"
    def handle(self, event) -> None:  # type: ignore[override]
        self._projection.handle(event)


def _subscribe_handlers(bus: EventBus, projections: Dict[str, Any]) -> None:
    # Orders - AI handlers
    order_handlers = [
        OrderAnalyticsHandler(), OrderCustomerServiceHandler(), OrderFraudDetectionHandler()
    ]
    for et in [
        'OrderPlaced','OrderPaid','OrderRefundRequested','OrderRefunded','OrderCancelled','OrderPaymentFailed'
    ]:
        for h in order_handlers:
            bus.subscribe(et, h)
    # Orders - projections
    oh = ProjectionEventHandler('order_history', projections['order_history'])
    for et in ['OrderPlaced','OrderPaid','OrderRefundRequested','OrderRefunded','OrderCancelled','OrderPaymentFailed']:
        bus.subscribe(et, oh)

    # Access - AI handlers
    access_handlers = [
        AccessAnalyticsHandler(), AccessLearningAssistantHandler(), AccessEngagementHandler()
    ]
    for et in [
        'CourseAccessGranted','AccessRevoked','AccessExpired','ProgressUpdated','CourseCompleted'
    ]:
        for h in access_handlers:
            bus.subscribe(et, h)
    # Access - projections
    ua = ProjectionEventHandler('user_access', projections['user_access'])
    for et in ['CourseAccessGranted','AccessRevoked','AccessExpired','ProgressUpdated','CourseCompleted']:
        bus.subscribe(et, ua)

    # Courses - AI handlers
    course_handlers = [
        CourseAnalyticsHandler(), CourseCatalogHandler(), CourseQualityHandler()
    ]
    for et in ['CourseCreated','CourseUpdated','CoursePolicyChanged','CourseDeprecated','PolicyUpdated']:
        for h in course_handlers:
            bus.subscribe(et, h)
    # Courses - projections
    cc = ProjectionEventHandler('course_catalog', projections['course_catalog'])
    for et in ['CourseCreated','CourseUpdated','CoursePolicyChanged','PolicyUpdated']:
        bus.subscribe(et, cc)

    # Users - AI handlers
    user_handlers = [
        UserAnalyticsHandler(), UserOnboardingHandler(), UserSecurityHandler()
    ]
    for et in ['UserRegistered','UserProfileUpdated','UserEmailChanged']:
        for h in user_handlers:
            bus.subscribe(et, h)

    # Policies - AI handlers
    policy_handlers = [
        PolicyAnalyticsHandler(), PolicyComplianceHandler(), PolicyLifecycleHandler()
    ]
    for et in ['PolicyCreated','PolicyUpdated','PolicyDeprecated','PolicyReactivated']:
        for h in policy_handlers:
            bus.subscribe(et, h)
    # Policies - projections
    pu = ProjectionEventHandler('policy_usage', projections['policy_usage'])
    for et in ['PolicyCreated','PolicyUpdated','CoursePolicyChanged']:
        bus.subscribe(et, pu)

    # Revenue - projections only
    rs = ProjectionEventHandler('revenue_summary', projections['revenue_summary'])
    for et in ['OrderPaid','OrderRefunded']:
        bus.subscribe(et, rs)


def build_container() -> Dict[str, Any]:
    event_bus = EventBus()

    # Projections
    projections = {
        'user_access': UserAccessProjection(),
        'course_catalog': CourseCatalogProjection(),
        'order_history': OrderHistoryProjection(),
        'policy_usage': PolicyUsageProjection(),
        'revenue_summary': RevenueSummaryProjection(),
    }

    _subscribe_handlers(event_bus, projections)

    # In-memory repositories
    order_repo = InMemoryOrderRepository()
    user_repo = InMemoryUserRepository()
    course_repo = InMemoryCourseRepository()
    access_repo = InMemoryAccessRepository()
    policy_repo = InMemoryPolicyRepository()

    # Application services
    order_service = OrderApplicationService(order_repo, user_repo, course_repo, event_bus)
    user_service = UserApplicationService(user_repo, event_bus)
    access_service = AccessApplicationService(access_repo, user_repo, course_repo, event_bus)
    course_service = CourseApplicationService(course_repo, policy_repo, event_bus)
    policy_service = PolicyApplicationService(policy_repo, event_bus)

    return {
        'event_bus': event_bus,
        'repos': {
            'orders': order_repo,
            'users': user_repo,
            'courses': course_repo,
            'access': access_repo,
            'policies': policy_repo,
        },
        'services': {
            'orders': order_service,
            'users': user_service,
            'access': access_service,
            'courses': course_service,
            'policies': policy_service,
        },
        'projections': projections,
    }

"""
AI Agent event handlers for Course domain events.
"""

from typing import Dict, Any, List
from datetime import datetime
import logging

from domain.events.event_bus import EventHandler
from domain.events.domain_event import DomainEvent
from domain.courses.events import (
    CourseCreated, CourseUpdated, CourseDeprecated, CoursePolicyChanged
)


class CourseAnalyticsHandler(EventHandler):
    """AI Agent that analyzes course patterns and provides insights."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.course_metrics = {
            'total_courses_created': 0,
            'total_courses_updated': 0,
            'total_courses_deprecated': 0,
            'total_policy_changes': 0,
            'active_courses': set(),
            'deprecated_courses': set(),
            'courses_by_policy': {}  # policy_id -> [course_ids]
        }
    
    @property
    def handler_name(self) -> str:
        return "CourseAnalyticsAI"
    
    def handle(self, event: DomainEvent) -> None:
        """Handle course domain events for analytics."""
        if isinstance(event, CourseCreated):
            self._handle_course_created(event)
        elif isinstance(event, CourseUpdated):
            self._handle_course_updated(event)
        elif isinstance(event, CourseDeprecated):
            self._handle_course_deprecated(event)
        elif isinstance(event, CoursePolicyChanged):
            self._handle_policy_changed(event)
    
    def _handle_course_created(self, event: CourseCreated) -> None:
        """Handle course creation for analytics."""
        self.course_metrics['total_courses_created'] += 1
        self.course_metrics['active_courses'].add(event.course_id.value)
        
        # Track courses by policy
        policy_id = event.policy_id.value
        if policy_id not in self.course_metrics['courses_by_policy']:
            self.course_metrics['courses_by_policy'][policy_id] = []
        self.course_metrics['courses_by_policy'][policy_id].append(event.course_id.value)
        
        self.logger.info(f"📊 Analytics: Course created - ID: {event.course_id.value}, Title: {event.title.value}, Policy: {policy_id}")
        self.logger.info(f"📊 Analytics: Total courses created: {self.course_metrics['total_courses_created']}")
        self.logger.info(f"📊 Analytics: Active courses: {len(self.course_metrics['active_courses'])}")
    
    def _handle_course_updated(self, event: CourseUpdated) -> None:
        """Handle course update for analytics."""
        self.course_metrics['total_courses_updated'] += 1
        
        self.logger.info(f"📊 Analytics: Course updated - ID: {event.course_id.value}, Title: {event.title.value}")
        self.logger.info(f"📊 Analytics: Total courses updated: {self.course_metrics['total_courses_updated']}")
    
    def _handle_course_deprecated(self, event: CourseDeprecated) -> None:
        """Handle course deprecation for analytics."""
        self.course_metrics['total_courses_deprecated'] += 1
        
        course_id = event.course_id.value
        if course_id in self.course_metrics['active_courses']:
            self.course_metrics['active_courses'].remove(course_id)
        self.course_metrics['deprecated_courses'].add(course_id)
        
        self.logger.info(f"📊 Analytics: Course deprecated - ID: {course_id}, Title: {event.title.value}")
        self.logger.info(f"📊 Analytics: Total courses deprecated: {self.course_metrics['total_courses_deprecated']}")
        self.logger.info(f"📊 Analytics: Active courses: {len(self.course_metrics['active_courses'])}")
    
    def _handle_policy_changed(self, event: CoursePolicyChanged) -> None:
        """Handle policy change for analytics."""
        self.course_metrics['total_policy_changes'] += 1
        
        course_id = event.course_id.value
        old_policy = event.old_policy_id.value
        new_policy = event.new_policy_id.value
        
        # Update policy mapping
        if old_policy in self.course_metrics['courses_by_policy']:
            if course_id in self.course_metrics['courses_by_policy'][old_policy]:
                self.course_metrics['courses_by_policy'][old_policy].remove(course_id)
        
        if new_policy not in self.course_metrics['courses_by_policy']:
            self.course_metrics['courses_by_policy'][new_policy] = []
        self.course_metrics['courses_by_policy'][new_policy].append(course_id)
        
        self.logger.info(f"📊 Analytics: Policy changed for course {course_id} - Old: {old_policy}, New: {new_policy}")
        self.logger.info(f"📊 Analytics: Total policy changes: {self.course_metrics['total_policy_changes']}")
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get current analytics summary."""
        return {
            'metrics': {
                **self.course_metrics,
                'active_courses_count': len(self.course_metrics['active_courses']),
                'deprecated_courses_count': len(self.course_metrics['deprecated_courses']),
                'unique_policies_count': len(self.course_metrics['courses_by_policy'])
            },
            'timestamp': datetime.now().isoformat(),
            'agent': self.handler_name
        }


class CourseCatalogHandler(EventHandler):
    """AI Agent that manages course catalog and provides recommendations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.catalog = {}  # course_id -> course_info
        self.recommendations = []
        self.catalog_updates = []
    
    @property
    def handler_name(self) -> str:
        return "CourseCatalogAI"
    
    def handle(self, event: DomainEvent) -> None:
        """Handle course domain events for catalog management."""
        if isinstance(event, CourseCreated):
            self._handle_course_created(event)
        elif isinstance(event, CourseUpdated):
            self._handle_course_updated(event)
        elif isinstance(event, CourseDeprecated):
            self._handle_course_deprecated(event)
        elif isinstance(event, CoursePolicyChanged):
            self._handle_policy_changed(event)
    
    def _handle_course_created(self, event: CourseCreated) -> None:
        """Handle course creation for catalog."""
        course_id = event.course_id.value
        
        self.catalog[course_id] = {
            'id': course_id,
            'title': event.title.value,
            'policy_id': event.policy_id.value,
            'status': 'active',
            'created_at': event.occurred_on
        }
        
        recommendation = f"📚 Catalog: New course '{event.title.value}' added to catalog! Preparing for publication..."
        self.recommendations.append(recommendation)
        self.catalog_updates.append(f"Course {course_id} created and added to catalog")
        
        self.logger.info(f"📚 Catalog: {recommendation}")
        self.logger.info(f"📚 Catalog: Total courses in catalog: {len(self.catalog)}")
    
    def _handle_course_updated(self, event: CourseUpdated) -> None:
        """Handle course update for catalog."""
        course_id = event.course_id.value
        
        if course_id in self.catalog:
            self.catalog[course_id]['title'] = event.title.value
            self.catalog[course_id]['description'] = event.description.value
            
            recommendation = f"📚 Catalog: Course '{event.title.value}' updated. Refreshing catalog listings..."
            self.recommendations.append(recommendation)
            self.catalog_updates.append(f"Course {course_id} updated in catalog")
            
            self.logger.info(f"📚 Catalog: {recommendation}")
    
    def _handle_course_deprecated(self, event: CourseDeprecated) -> None:
        """Handle course deprecation for catalog."""
        course_id = event.course_id.value
        
        if course_id in self.catalog:
            self.catalog[course_id]['status'] = 'deprecated'
            
            recommendation = f"📚 Catalog: Course '{event.title.value}' deprecated. Updating catalog visibility..."
            self.recommendations.append(recommendation)
            self.catalog_updates.append(f"Course {course_id} marked as deprecated")
            
            self.logger.info(f"📚 Catalog: {recommendation}")
    
    def _handle_policy_changed(self, event: CoursePolicyChanged) -> None:
        """Handle policy change for catalog."""
        course_id = event.course_id.value
        
        if course_id in self.catalog:
            self.catalog[course_id]['policy_id'] = event.new_policy_id.value
            
            recommendation = f"📚 Catalog: Policy changed for course {course_id}. Validating catalog compliance..."
            self.recommendations.append(recommendation)
            self.catalog_updates.append(f"Course {course_id} policy updated")
            
            self.logger.info(f"📚 Catalog: {recommendation}")
    
    def get_catalog(self) -> Dict[str, Dict[str, Any]]:
        """Get current catalog."""
        return self.catalog.copy()
    
    def get_course_info(self, course_id: str) -> Dict[str, Any]:
        """Get information about a specific course."""
        return self.catalog.get(course_id, {}).copy()
    
    def get_recommendations(self) -> List[str]:
        """Get list of catalog recommendations."""
        return self.recommendations.copy()
    
    def get_catalog_updates(self) -> List[str]:
        """Get list of catalog updates."""
        return self.catalog_updates.copy()


class CourseQualityHandler(EventHandler):
    """AI Agent that monitors course quality and compliance."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.course_quality_scores = {}  # course_id -> quality_score
        self.quality_alerts = []
        self.compliance_checks = []
    
    @property
    def handler_name(self) -> str:
        return "CourseQualityAI"
    
    def handle(self, event: DomainEvent) -> None:
        """Handle course domain events for quality monitoring."""
        if isinstance(event, CourseCreated):
            self._handle_course_created(event)
        elif isinstance(event, CourseUpdated):
            self._handle_course_updated(event)
        elif isinstance(event, CourseDeprecated):
            self._handle_course_deprecated(event)
        elif isinstance(event, CoursePolicyChanged):
            self._handle_policy_changed(event)
    
    def _handle_course_created(self, event: CourseCreated) -> None:
        """Handle course creation for quality monitoring."""
        course_id = event.course_id.value
        
        # Initial quality check
        quality_score = self._calculate_initial_quality_score(event)
        self.course_quality_scores[course_id] = quality_score
        
        # Compliance check
        compliance = self._check_compliance(event)
        self.compliance_checks.append({
            'course_id': course_id,
            'check_type': 'creation',
            'passed': compliance['passed'],
            'issues': compliance['issues']
        })
        
        if not compliance['passed']:
            alert = f"⚠️ Quality Alert: Course {course_id} has compliance issues: {', '.join(compliance['issues'])}"
            if not any(course_id in existing_alert for existing_alert in self.quality_alerts[-3:]):
                self.quality_alerts.append(alert)
                self.logger.warning(alert)
        
        self.logger.info(f"🔍 Quality: Course {course_id} created - Quality score: {quality_score}/100, Compliance: {'PASS' if compliance['passed'] else 'FAIL'}")
    
    def _handle_course_updated(self, event: CourseUpdated) -> None:
        """Handle course update for quality monitoring."""
        course_id = event.course_id.value
        
        # Recalculate quality score after update
        if course_id in self.course_quality_scores:
            quality_score = self._calculate_quality_score_after_update(event)
            self.course_quality_scores[course_id] = quality_score
            
            # Check if quality improved or degraded
            if quality_score < 50:
                alert = f"⚠️ Quality Alert: Course {course_id} has low quality score ({quality_score}/100) after update"
                if not any(course_id in existing_alert for existing_alert in self.quality_alerts[-3:]):
                    self.quality_alerts.append(alert)
                    self.logger.warning(alert)
            
            self.logger.info(f"🔍 Quality: Course {course_id} updated - New quality score: {quality_score}/100")
    
    def _handle_course_deprecated(self, event: CourseDeprecated) -> None:
        """Handle course deprecation for quality monitoring."""
        course_id = event.course_id.value
        
        if course_id in self.course_quality_scores:
            # Deprecated courses have reduced quality score
            self.course_quality_scores[course_id] = max(0, self.course_quality_scores[course_id] - 20)
        
        self.logger.info(f"🔍 Quality: Course {course_id} deprecated - Quality score adjusted")
    
    def _handle_policy_changed(self, event: CoursePolicyChanged) -> None:
        """Handle policy change for quality monitoring."""
        course_id = event.course_id.value
        
        # Compliance check after policy change
        compliance = self._check_policy_compliance(event)
        self.compliance_checks.append({
            'course_id': course_id,
            'check_type': 'policy_change',
            'passed': compliance['passed'],
            'issues': compliance['issues']
        })
        
        if not compliance['passed']:
            alert = f"⚠️ Quality Alert: Policy change for course {course_id} may cause compliance issues"
            if not any(course_id in existing_alert for existing_alert in self.quality_alerts[-3:]):
                self.quality_alerts.append(alert)
                self.logger.warning(alert)
        
        self.logger.info(f"🔍 Quality: Policy changed for course {course_id} - Compliance: {'PASS' if compliance['passed'] else 'FAIL'}")
    
    def _calculate_initial_quality_score(self, event: CourseCreated) -> float:
        """Calculate initial quality score for a new course."""
        score = 70.0  # Base score for new course
        
        # Check if title is provided and not empty
        if event.title.value and len(event.title.value.strip()) > 0:
            score += 10.0
        
        # Check if policy is assigned
        if event.policy_id.value:
            score += 10.0
        
        return min(100.0, score)
    
    def _calculate_quality_score_after_update(self, event: CourseUpdated) -> float:
        """Calculate quality score after course update."""
        score = 60.0  # Base score
        
        # Check title
        if event.title.value and len(event.title.value.strip()) > 0:
            score += 15.0
        
        # Check description (more points for longer descriptions)
        if event.description.value:
            desc_length = len(event.description.value.strip())
            if desc_length > 100:
                score += 15.0
            elif desc_length > 50:
                score += 10.0
            else:
                score += 5.0
        
        return min(100.0, score)
    
    def _check_compliance(self, event: CourseCreated) -> Dict[str, Any]:
        """Check compliance for course creation."""
        issues = []
        
        # Basic compliance checks
        if not event.title.value or len(event.title.value.strip()) == 0:
            issues.append("Missing title")
        
        if not event.policy_id.value:
            issues.append("No refund policy assigned")
        
        return {
            'passed': len(issues) == 0,
            'issues': issues
        }
    
    def _check_policy_compliance(self, event: CoursePolicyChanged) -> Dict[str, Any]:
        """Check compliance after policy change."""
        issues = []
        
        # Check if policy change is valid (old and new are different)
        if event.old_policy_id.value == event.new_policy_id.value:
            issues.append("Policy unchanged")
        
        return {
            'passed': len(issues) == 0,
            'issues': issues
        }
    
    def get_quality_score(self, course_id: str) -> float:
        """Get quality score for a specific course."""
        return self.course_quality_scores.get(course_id, 0.0)
    
    def get_quality_alerts(self) -> List[str]:
        """Get list of quality alerts."""
        return self.quality_alerts.copy()
    
    def get_compliance_checks(self) -> List[Dict[str, Any]]:
        """Get list of compliance checks."""
        return self.compliance_checks.copy()

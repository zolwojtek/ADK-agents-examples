"""
AI Agent event handlers for Access domain events.
"""

from typing import Dict, Any, List
from datetime import datetime
import logging

from domain.events.event_bus import EventHandler
from domain.events.domain_event import DomainEvent
from domain.access.events import (
    CourseAccessGranted, AccessRevoked, AccessExpired, 
    ProgressUpdated, CourseCompleted
)
from domain.shared.value_objects import AccessId, UserId, CourseId, Progress


class AccessAnalyticsHandler(EventHandler):
    """AI Agent that analyzes access patterns and provides insights."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.access_metrics = {
            'total_accesses_granted': 0,
            'total_accesses_revoked': 0,
            'total_accesses_expired': 0,
            'total_courses_completed': 0,
            'average_progress': 0.0,
            'active_users': set(),
            'active_courses': set()
        }
    
    @property
    def handler_name(self) -> str:
        return "AccessAnalyticsAI"
    
    def handle(self, event: DomainEvent) -> None:
        """Handle access domain events for analytics."""
        if isinstance(event, CourseAccessGranted):
            self._handle_access_granted(event)
        elif isinstance(event, AccessRevoked):
            self._handle_access_revoked(event)
        elif isinstance(event, AccessExpired):
            self._handle_access_expired(event)
        elif isinstance(event, ProgressUpdated):
            self._handle_progress_updated(event)
        elif isinstance(event, CourseCompleted):
            self._handle_course_completed(event)
    
    def _handle_access_granted(self, event: CourseAccessGranted) -> None:
        """Handle access granted for analytics."""
        self.access_metrics['total_accesses_granted'] += 1
        self.access_metrics['active_users'].add(event.user_id.value)
        self.access_metrics['active_courses'].add(event.course_id.value)
        
        self.logger.info(f"📊 Analytics: Access granted - User: {event.user_id.value}, Course: {event.course_id.value}")
        self.logger.info(f"📊 Analytics: Total accesses granted: {self.access_metrics['total_accesses_granted']}")
        self.logger.info(f"📊 Analytics: Active users: {len(self.access_metrics['active_users'])}")
        self.logger.info(f"📊 Analytics: Active courses: {len(self.access_metrics['active_courses'])}")
    
    def _handle_access_revoked(self, event: AccessRevoked) -> None:
        """Handle access revoked for analytics."""
        self.access_metrics['total_accesses_revoked'] += 1
        
        self.logger.info(f"📊 Analytics: Access revoked - User: {event.user_id.value}, Course: {event.course_id.value}, Reason: {event.reason}")
        self.logger.info(f"📊 Analytics: Total accesses revoked: {self.access_metrics['total_accesses_revoked']}")
    
    def _handle_access_expired(self, event: AccessExpired) -> None:
        """Handle access expired for analytics."""
        self.access_metrics['total_accesses_expired'] += 1
        
        self.logger.info(f"📊 Analytics: Access expired - User: {event.user_id.value}, Course: {event.course_id.value}")
        self.logger.info(f"📊 Analytics: Expired at: {event.expired_at}")
        self.logger.info(f"📊 Analytics: Total accesses expired: {self.access_metrics['total_accesses_expired']}")
    
    def _handle_progress_updated(self, event: ProgressUpdated) -> None:
        """Handle progress update for analytics."""
        progress_value = event.progress.value
        self._update_average_progress(progress_value)
        
        self.logger.info(f"📊 Analytics: Progress updated - User: {event.user_id.value}, Course: {event.course_id.value}, Progress: {progress_value}%")
    
    def _handle_course_completed(self, event: CourseCompleted) -> None:
        """Handle course completion for analytics."""
        self.access_metrics['total_courses_completed'] += 1
        
        self.logger.info(f"📊 Analytics: Course completed - User: {event.user_id.value}, Course: {event.course_id.value}")
        self.logger.info(f"📊 Analytics: Total courses completed: {self.access_metrics['total_courses_completed']}")
    
    def _update_average_progress(self, new_progress: float) -> None:
        """Update average progress calculation."""
        # Simplified calculation - in real scenario would track progress more accurately
        current_avg = self.access_metrics['average_progress']
        self.access_metrics['average_progress'] = (current_avg + new_progress) / 2
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get current analytics summary."""
        return {
            'metrics': {
                **self.access_metrics,
                'active_users_count': len(self.access_metrics['active_users']),
                'active_courses_count': len(self.access_metrics['active_courses'])
            },
            'timestamp': datetime.now().isoformat(),
            'agent': self.handler_name
        }


class AccessLearningAssistantHandler(EventHandler):
    """AI Agent that provides personalized learning assistance based on access events."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.user_learning_profiles = {}  # Track user learning patterns
        self.recommendations = []
    
    @property
    def handler_name(self) -> str:
        return "AccessLearningAssistantAI"
    
    def handle(self, event: DomainEvent) -> None:
        """Handle access domain events for learning assistance."""
        if isinstance(event, CourseAccessGranted):
            self._handle_access_granted(event)
        elif isinstance(event, ProgressUpdated):
            self._handle_progress_updated(event)
        elif isinstance(event, CourseCompleted):
            self._handle_course_completed(event)
        elif isinstance(event, AccessExpired):
            self._handle_access_expired(event)
    
    def _handle_access_granted(self, event: CourseAccessGranted) -> None:
        """Handle access granted for learning assistance."""
        user_id = event.user_id.value
        course_id = event.course_id.value
        
        # Initialize learning profile if needed
        if user_id not in self.user_learning_profiles:
            self.user_learning_profiles[user_id] = {
                'active_courses': [],
                'completed_courses': [],
                'learning_streak': 0
            }
        
        self.user_learning_profiles[user_id]['active_courses'].append(course_id)
        
        recommendation = f"📚 Learning Assistant: Welcome! Starting journey with course {course_id}. Creating personalized learning path..."
        self.recommendations.append(recommendation)
        self.logger.info(f"🎓 LearningAssistant: {recommendation}")
        self.logger.info(f"🎓 LearningAssistant: User {user_id} now has {len(self.user_learning_profiles[user_id]['active_courses'])} active courses")
    
    def _handle_progress_updated(self, event: ProgressUpdated) -> None:
        """Handle progress update for learning assistance."""
        user_id = event.user_id.value
        course_id = event.course_id.value
        progress = event.progress.value
        
        # Track learning streak
        if user_id in self.user_learning_profiles:
            self.user_learning_profiles[user_id]['learning_streak'] += 1
        
        # Provide encouragement based on progress
        if progress >= 50.0 and progress < 75.0:
            recommendation = f"🎓 LearningAssistant: Great progress! You're halfway through course {course_id}. Keep up the momentum!"
            self.recommendations.append(recommendation)
            self.logger.info(f"🎓 LearningAssistant: {recommendation}")
        elif progress >= 75.0 and progress < 100.0:
            recommendation = f"🎓 LearningAssistant: Almost there! You're {progress}% through course {course_id}. Finish strong!"
            self.recommendations.append(recommendation)
            self.logger.info(f"🎓 LearningAssistant: {recommendation}")
    
    def _handle_course_completed(self, event: CourseCompleted) -> None:
        """Handle course completion for learning assistance."""
        user_id = event.user_id.value
        course_id = event.course_id.value
        
        if user_id in self.user_learning_profiles:
            if course_id in self.user_learning_profiles[user_id]['active_courses']:
                self.user_learning_profiles[user_id]['active_courses'].remove(course_id)
            self.user_learning_profiles[user_id]['completed_courses'].append(course_id)
        
        recommendation = f"🎉 LearningAssistant: Congratulations! You completed course {course_id}! Here are related courses you might enjoy..."
        self.recommendations.append(recommendation)
        self.logger.info(f"🎓 LearningAssistant: {recommendation}")
    
    def _handle_access_expired(self, event: AccessExpired) -> None:
        """Handle access expiration for learning assistance."""
        user_id = event.user_id.value
        course_id = event.course_id.value
        
        recommendation = f"⏰ LearningAssistant: Access to course {course_id} expired. Would you like to renew your access?"
        self.recommendations.append(recommendation)
        self.logger.info(f"🎓 LearningAssistant: {recommendation}")
    
    def get_recommendations(self) -> List[str]:
        """Get list of learning recommendations."""
        return self.recommendations.copy()
    
    def get_user_learning_profile(self, user_id: str) -> Dict[str, Any]:
        """Get learning profile for a specific user."""
        return self.user_learning_profiles.get(user_id, {}).copy()


class AccessEngagementHandler(EventHandler):
    """AI Agent that tracks user engagement and retention patterns."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.user_engagement = {}  # Track user engagement metrics
        self.engagement_alerts = []  # Alerts for low engagement
        self.retention_patterns = {}  # Track retention patterns
    
    @property
    def handler_name(self) -> str:
        return "AccessEngagementAI"
    
    def handle(self, event: DomainEvent) -> None:
        """Handle access domain events for engagement tracking."""
        if isinstance(event, CourseAccessGranted):
            self._handle_access_granted(event)
        elif isinstance(event, ProgressUpdated):
            self._handle_progress_updated(event)
        elif isinstance(event, CourseCompleted):
            self._handle_course_completed(event)
        elif isinstance(event, AccessExpired):
            self._handle_access_expired(event)
        elif isinstance(event, AccessRevoked):
            self._handle_access_revoked(event)
    
    def _handle_access_granted(self, event: CourseAccessGranted) -> None:
        """Track engagement when access is granted."""
        user_id = event.user_id.value
        course_id = event.course_id.value
        
        if user_id not in self.user_engagement:
            self.user_engagement[user_id] = {
                'accesses': [],
                'progress_events': [],
                'last_activity': None,
                'engagement_score': 100.0  # Start with full engagement
            }
        
        self.user_engagement[user_id]['accesses'].append({
            'course_id': course_id,
            'granted_at': event.occurred_on
        })
        self.user_engagement[user_id]['last_activity'] = event.occurred_on
        
        self.logger.info(f"📈 Engagement: User {user_id} granted access to course {course_id}")
    
    def _handle_progress_updated(self, event: ProgressUpdated) -> None:
        """Track engagement when progress is updated."""
        user_id = event.user_id.value
        progress = event.progress.value
        
        if user_id in self.user_engagement:
            self.user_engagement[user_id]['progress_events'].append({
                'progress': progress,
                'updated_at': event.occurred_on
            })
            self.user_engagement[user_id]['last_activity'] = event.occurred_on
            
            # Update engagement score based on recent activity
            self._update_engagement_score(user_id)
        
        self.logger.info(f"📈 Engagement: User {user_id} updated progress to {progress}%")
    
    def _handle_course_completed(self, event: CourseCompleted) -> None:
        """Track engagement when course is completed."""
        user_id = event.user_id.value
        
        if user_id in self.user_engagement:
            self.user_engagement[user_id]['engagement_score'] = min(100.0, self.user_engagement[user_id]['engagement_score'] + 10.0)
            self.user_engagement[user_id]['last_activity'] = event.occurred_on
        
        self.logger.info(f"📈 Engagement: User {user_id} completed course - engagement score increased")
    
    def _handle_access_expired(self, event: AccessExpired) -> None:
        """Track engagement when access expires."""
        user_id = event.user_id.value
        
        if user_id in self.user_engagement:
            # Decrease engagement score for expired access
            self.user_engagement[user_id]['engagement_score'] = max(0.0, self.user_engagement[user_id]['engagement_score'] - 5.0)
        
        self.logger.info(f"📈 Engagement: Access expired for user {user_id} - engagement score decreased")
    
    def _handle_access_revoked(self, event: AccessRevoked) -> None:
        """Track engagement when access is revoked."""
        user_id = event.user_id.value
        
        if user_id in self.user_engagement:
            # Significant decrease in engagement score for revoked access
            self.user_engagement[user_id]['engagement_score'] = max(0.0, self.user_engagement[user_id]['engagement_score'] - 15.0)
            
            # Check if engagement is critically low
            if self.user_engagement[user_id]['engagement_score'] < 20.0:
                alert = f"⚠️ Engagement Alert: User {user_id} has low engagement score ({self.user_engagement[user_id]['engagement_score']:.1f})"
                if not any(f"User {user_id}" in existing_alert for existing_alert in self.engagement_alerts[-3:]):
                    self.engagement_alerts.append(alert)
                    self.logger.warning(alert)
        
        self.logger.info(f"📈 Engagement: Access revoked for user {user_id} - engagement score decreased")
    
    def _update_engagement_score(self, user_id: str) -> None:
        """Update engagement score based on activity patterns."""
        if user_id not in self.user_engagement:
            return
        
        user_data = self.user_engagement[user_id]
        recent_progress = len([e for e in user_data['progress_events'] 
                              if (datetime.now() - e['updated_at']).days < 7])
        
        # Increase engagement for recent activity
        if recent_progress > 0:
            user_data['engagement_score'] = min(100.0, user_data['engagement_score'] + 2.0)
        
        # Check for low engagement (no activity in 30 days)
        if user_data['last_activity']:
            days_since_activity = (datetime.now() - user_data['last_activity']).days
            if days_since_activity > 30:
                user_data['engagement_score'] = max(0.0, user_data['engagement_score'] - 5.0)
                
                if user_data['engagement_score'] < 30.0:
                    alert = f"⚠️ Engagement Alert: User {user_id} has low engagement - {days_since_activity} days since last activity"
                    if not any(f"User {user_id}" in existing_alert for existing_alert in self.engagement_alerts[-3:]):
                        self.engagement_alerts.append(alert)
                        self.logger.warning(alert)
    
    def get_engagement_alerts(self) -> List[str]:
        """Get list of engagement alerts."""
        return self.engagement_alerts.copy()
    
    def get_user_engagement_score(self, user_id: str) -> float:
        """Get engagement score for a specific user."""
        return self.user_engagement.get(user_id, {}).get('engagement_score', 0.0)

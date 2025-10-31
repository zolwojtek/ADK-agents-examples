"""
AI Agent event handlers for User domain events.
"""

from typing import Dict, Any, List
from datetime import datetime
import logging

from domain.events.event_bus import EventHandler
from domain.events.domain_event import DomainEvent
from domain.users.events import (
    UserRegistered, UserProfileUpdated, UserEmailChanged
)
from domain.shared.value_objects import UserId, EmailAddress
from domain.users.value_objects import UserProfile


class UserAnalyticsHandler(EventHandler):
    """AI Agent that analyzes user patterns and provides insights."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.user_metrics = {
            'total_users_registered': 0,
            'total_profile_updates': 0,
            'total_email_changes': 0,
            'users_by_registration_date': {},  # date -> count
            'profile_completion_rate': 0.0
        }
    
    @property
    def handler_name(self) -> str:
        return "UserAnalyticsAI"
    
    def handle(self, event: DomainEvent) -> None:
        """Handle user domain events for analytics."""
        if isinstance(event, UserRegistered):
            self._handle_user_registered(event)
        elif isinstance(event, UserProfileUpdated):
            self._handle_profile_updated(event)
        elif isinstance(event, UserEmailChanged):
            self._handle_email_changed(event)
    
    def _handle_user_registered(self, event: UserRegistered) -> None:
        """Handle user registration for analytics."""
        self.user_metrics['total_users_registered'] += 1
        
        # Track registration by date
        registration_date = event.occurred_on.date()
        date_str = registration_date.isoformat()
        if date_str not in self.user_metrics['users_by_registration_date']:
            self.user_metrics['users_by_registration_date'][date_str] = 0
        self.user_metrics['users_by_registration_date'][date_str] += 1
        
        self.logger.info(f"📊 Analytics: User registered - ID: {event.user_id.value}, Email: {event.email.value}")
        self.logger.info(f"📊 Analytics: Total users registered: {self.user_metrics['total_users_registered']}")
        self.logger.info(f"📊 Analytics: Registrations today: {self.user_metrics['users_by_registration_date'].get(date_str, 0)}")
    
    def _handle_profile_updated(self, event: UserProfileUpdated) -> None:
        """Handle profile update for analytics."""
        self.user_metrics['total_profile_updates'] += 1
        
        # Update profile completion rate
        self._update_profile_completion_rate(event.profile)
        
        self.logger.info(f"📊 Analytics: Profile updated - User ID: {event.user_id.value}")
        self.logger.info(f"📊 Analytics: Total profile updates: {self.user_metrics['total_profile_updates']}")
    
    def _handle_email_changed(self, event: UserEmailChanged) -> None:
        """Handle email change for analytics."""
        self.user_metrics['total_email_changes'] += 1
        
        self.logger.info(f"📊 Analytics: Email changed - User ID: {event.user_id.value}, Old: {event.old_email.value}, New: {event.new_email.value}")
        self.logger.info(f"📊 Analytics: Total email changes: {self.user_metrics['total_email_changes']}")
    
    def _update_profile_completion_rate(self, profile: UserProfile) -> None:
        """Update profile completion rate calculation."""
        # Simple calculation - check if profile has key fields filled
        fields_to_check = [
            profile.first_name,
            profile.last_name,
            profile.bio,
            profile.avatar_url
        ]
        completed_fields = sum(1 for field in fields_to_check if field and len(str(field).strip()) > 0)
        
        # Simplified calculation - in real scenario would track across all users
        completion_rate = (completed_fields / len(fields_to_check)) * 100
        self.user_metrics['profile_completion_rate'] = completion_rate
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get current analytics summary."""
        return {
            'metrics': self.user_metrics.copy(),
            'timestamp': datetime.now().isoformat(),
            'agent': self.handler_name
        }


class UserOnboardingHandler(EventHandler):
    """AI Agent that handles user onboarding and welcome flows."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.onboarding_flows = []
        self.user_onboarding_status = {}  # user_id -> onboarding_status
        self.welcome_messages = []
    
    @property
    def handler_name(self) -> str:
        return "UserOnboardingAI"
    
    def handle(self, event: DomainEvent) -> None:
        """Handle user domain events for onboarding."""
        if isinstance(event, UserRegistered):
            self._handle_user_registered(event)
        elif isinstance(event, UserProfileUpdated):
            self._handle_profile_updated(event)
        elif isinstance(event, UserEmailChanged):
            self._handle_email_changed(event)
    
    def _handle_user_registered(self, event: UserRegistered) -> None:
        """Handle user registration for onboarding."""
        user_id = event.user_id.value
        email = event.email.value
        
        # Initialize onboarding status
        self.user_onboarding_status[user_id] = {
            'registered': True,
            'profile_completed': False,
            'email_verified': False,
            'onboarding_complete': False
        }
        
        # Send welcome message
        welcome_message = f"🎉 Welcome {event.name}! Your account has been created. Let's get you started!"
        self.welcome_messages.append(welcome_message)
        self.onboarding_flows.append(f"User {user_id} registration - Welcome email sent")
        
        self.logger.info(f"🎉 Onboarding: {welcome_message}")
        self.logger.info(f"🎉 Onboarding: Initiated onboarding flow for user {user_id}")
    
    def _handle_profile_updated(self, event: UserProfileUpdated) -> None:
        """Handle profile update for onboarding."""
        user_id = event.user_id.value
        
        if user_id in self.user_onboarding_status:
            self.user_onboarding_status[user_id]['profile_completed'] = True
            
            # Check if onboarding is complete
            if self._check_onboarding_complete(user_id):
                self.user_onboarding_status[user_id]['onboarding_complete'] = True
                completion_message = f"✅ Onboarding complete for user {user_id}! Profile is fully set up."
                self.onboarding_flows.append(completion_message)
                self.logger.info(f"🎉 Onboarding: {completion_message}")
        
        message = f"📝 Profile updated for user {user_id}. Continuing onboarding flow..."
        self.onboarding_flows.append(message)
        self.logger.info(f"🎉 Onboarding: {message}")
    
    def _handle_email_changed(self, event: UserEmailChanged) -> None:
        """Handle email change for onboarding."""
        user_id = event.user_id.value
        
        # Email change requires re-verification
        if user_id in self.user_onboarding_status:
            self.user_onboarding_status[user_id]['email_verified'] = False
            
            message = f"📧 Email changed for user {user_id}. Re-verification required."
            self.onboarding_flows.append(message)
            self.logger.info(f"🎉 Onboarding: {message}")
    
    def _check_onboarding_complete(self, user_id: str) -> bool:
        """Check if user onboarding is complete."""
        if user_id not in self.user_onboarding_status:
            return False
        
        status = self.user_onboarding_status[user_id]
        return (
            status['registered'] and
            status['profile_completed'] and
            status['email_verified']
        )
    
    def get_onboarding_status(self, user_id: str) -> Dict[str, bool]:
        """Get onboarding status for a specific user."""
        return self.user_onboarding_status.get(user_id, {}).copy()
    
    def get_welcome_messages(self) -> List[str]:
        """Get list of welcome messages."""
        return self.welcome_messages.copy()
    
    def get_onboarding_flows(self) -> List[str]:
        """Get list of onboarding flow actions."""
        return self.onboarding_flows.copy()


class UserSecurityHandler(EventHandler):
    """AI Agent that monitors user security and detects suspicious activity."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.user_security_profiles = {}  # user_id -> security_profile
        self.security_alerts = []
        self.suspicious_activities = []
    
    @property
    def handler_name(self) -> str:
        return "UserSecurityAI"
    
    def handle(self, event: DomainEvent) -> None:
        """Handle user domain events for security monitoring."""
        if isinstance(event, UserRegistered):
            self._handle_user_registered(event)
        elif isinstance(event, UserProfileUpdated):
            self._handle_profile_updated(event)
        elif isinstance(event, UserEmailChanged):
            self._handle_email_changed(event)
    
    def _handle_user_registered(self, event: UserRegistered) -> None:
        """Handle user registration for security monitoring."""
        user_id = event.user_id.value
        email = event.email.value
        
        # Initialize security profile
        self.user_security_profiles[user_id] = {
            'email': email,
            'registration_date': event.occurred_on,
            'profile_changes': 0,
            'email_changes': 0,
            'last_email_change': None,
            'risk_score': 0.0  # 0 = low risk, 100 = high risk
        }
        
        # Check for suspicious registration patterns
        self._check_registration_patterns(event)
        
        self.logger.info(f"🔒 Security: User {user_id} registered - Security profile initialized")
    
    def _handle_profile_updated(self, event: UserProfileUpdated) -> None:
        """Handle profile update for security monitoring."""
        user_id = event.user_id.value
        
        if user_id in self.user_security_profiles:
            self.user_security_profiles[user_id]['profile_changes'] += 1
            
            # Multiple rapid profile changes might be suspicious
            if self.user_security_profiles[user_id]['profile_changes'] > 5:
                alert = f"🚨 Security Alert: User {user_id} has excessive profile changes ({self.user_security_profiles[user_id]['profile_changes']})"
                if not any(user_id in existing_alert for existing_alert in self.security_alerts[-3:]):
                    self.security_alerts.append(alert)
                    self.user_security_profiles[user_id]['risk_score'] = min(100.0, self.user_security_profiles[user_id]['risk_score'] + 10.0)
                    self.logger.warning(alert)
        
        self.logger.info(f"🔒 Security: Profile updated for user {user_id}")
    
    def _handle_email_changed(self, event: UserEmailChanged) -> None:
        """Handle email change for security monitoring."""
        user_id = event.user_id.value
        
        if user_id in self.user_security_profiles:
            self.user_security_profiles[user_id]['email_changes'] += 1
            self.user_security_profiles[user_id]['last_email_change'] = event.occurred_on
            
            # Check for suspicious email change patterns
            email_changes = self.user_security_profiles[user_id]['email_changes']
            
            if email_changes > 3:
                alert = f"🚨 Security Alert: User {user_id} has changed email {email_changes} times - potential account takeover attempt"
                if not any(user_id in existing_alert for existing_alert in self.security_alerts[-3:]):
                    self.security_alerts.append(alert)
                    self.suspicious_activities.append({
                        'user_id': user_id,
                        'activity': 'excessive_email_changes',
                        'timestamp': event.occurred_on
                    })
                    self.user_security_profiles[user_id]['risk_score'] = min(100.0, self.user_security_profiles[user_id]['risk_score'] + 20.0)
                    self.logger.warning(alert)
            
            # Check for rapid email changes
            last_change = self.user_security_profiles[user_id]['last_email_change']
            if last_change and email_changes >= 2:
                time_diff = (event.occurred_on - last_change).total_seconds()
                if time_diff < 3600:  # Less than 1 hour between changes
                    alert = f"🚨 Security Alert: User {user_id} changed email rapidly - potential security issue"
                    if not any(user_id in existing_alert for existing_alert in self.security_alerts[-3:]):
                        self.security_alerts.append(alert)
                        self.logger.warning(alert)
        
        self.logger.info(f"🔒 Security: Email changed for user {user_id}")
    
    def _check_registration_patterns(self, event: UserRegistered) -> None:
        """Check for suspicious registration patterns."""
        email = event.email.value
        user_id = event.user_id.value
        
        # Check for suspicious email patterns
        suspicious_domains = ['temp-mail', '10minutemail', 'throwaway']
        email_lower = email.lower()
        
        for domain in suspicious_domains:
            if domain in email_lower:
                alert = f"🚨 Security Alert: Suspicious email domain detected for user {user_id}: {email}"
                if not any(user_id in existing_alert for existing_alert in self.security_alerts[-3:]):
                    self.security_alerts.append(alert)
                    self.user_security_profiles[user_id]['risk_score'] = min(100.0, self.user_security_profiles[user_id]['risk_score'] + 15.0)
                    self.logger.warning(alert)
                break
    
    def get_security_profile(self, user_id: str) -> Dict[str, Any]:
        """Get security profile for a specific user."""
        return self.user_security_profiles.get(user_id, {}).copy()
    
    def get_security_alerts(self) -> List[str]:
        """Get list of security alerts."""
        return self.security_alerts.copy()
    
    def get_suspicious_activities(self) -> List[Dict[str, Any]]:
        """Get list of suspicious activities."""
        return self.suspicious_activities.copy()
    
    def get_user_risk_score(self, user_id: str) -> float:
        """Get risk score for a specific user."""
        return self.user_security_profiles.get(user_id, {}).get('risk_score', 0.0)

"""
Unit tests for PolicyRepository implementation.
"""

import pytest
from uuid import uuid4

from infrastructure.repositories.policy_repository import PolicyRepository
from domain.policies.aggregates import RefundPolicy
from domain.policies.value_objects import PolicyName, PolicyConditions, PolicyStatus
from domain.shared.value_objects import PolicyId, PolicyType, RefundPeriod


class TestPolicyRepository:
    """Test PolicyRepository implementation."""
    
    @pytest.fixture
    def policy_repository(self):
        """Create a test policy repository."""
        return PolicyRepository()
    
    @pytest.fixture
    def policy_data(self):
        """Create test policy data."""
        return {
            "id": PolicyId(str(uuid4())),
            "name": PolicyName("Standard Refund Policy"),
            "policy_type": PolicyType.STANDARD,
            "refund_period": RefundPeriod(30),
            "conditions": PolicyConditions("Standard refund conditions"),
            "status": PolicyStatus.ACTIVE
        }
    
    @pytest.fixture
    def policy(self, policy_data):
        """Create a test policy."""
        return RefundPolicy.create_policy(
            name=policy_data["name"],
            policy_type=policy_data["policy_type"],
            refund_period=policy_data["refund_period"],
            conditions=policy_data["conditions"]
        )
    
    def test_save_policy(self, policy_repository, policy):
        """Test saving a policy."""
        saved_policy = policy_repository.save(policy)
        
        assert saved_policy == policy
        assert policy_repository.get_by_id(policy.id) == policy
        assert policy_repository.count() == 1
    
    def test_get_by_id(self, policy_repository, policy):
        """Test getting policy by ID."""
        policy_repository.save(policy)
        
        retrieved_policy = policy_repository.get_by_id(policy.id)
        assert retrieved_policy == policy
        
        non_existent_id = PolicyId(str(uuid4()))
        assert policy_repository.get_by_id(non_existent_id) is None
    
    def test_get_by_name(self, policy_repository, policy):
        """Test getting policy by name."""
        policy_repository.save(policy)
        
        retrieved_policy = policy_repository.get_by_name(policy.name.value)
        assert retrieved_policy == policy
        
        assert policy_repository.get_by_name("Non-existent Policy") is None
    
    def test_get_by_type(self, policy_repository, policy):
        """Test getting policies by type."""
        policy_repository.save(policy)
        
        policies = policy_repository.get_by_type(policy.policy_type)
        assert len(policies) == 1
        assert policies[0] == policy
        
        policies = policy_repository.get_by_type(PolicyType.EXTENDED)
        assert len(policies) == 0
    
    def test_get_by_status(self, policy_repository, policy):
        """Test getting policies by status."""
        policy_repository.save(policy)
        
        policies = policy_repository.get_by_status(policy.status)
        assert len(policies) == 1
        assert policies[0] == policy
        
        policies = policy_repository.get_by_status("deprecated")
        assert len(policies) == 0
    
    def test_get_active_policies(self, policy_repository, policy):
        """Test getting active policies."""
        policy_repository.save(policy)
        
        active_policies = policy_repository.get_active_policies()
        assert len(active_policies) == 1
        assert active_policies[0] == policy
        
        # Deprecate policy
        policy.deprecate("Policy is being phased out")
        policy_repository.save(policy)
        
        active_policies = policy_repository.get_active_policies()
        assert len(active_policies) == 0
    
    def test_get_deprecated_policies(self, policy_repository, policy):
        """Test getting deprecated policies."""
        policy_repository.save(policy)
        
        deprecated_policies = policy_repository.get_deprecated_policies()
        assert len(deprecated_policies) == 0
        
        # Deprecate policy
        policy.deprecate("Policy is being phased out")
        policy_repository.save(policy)
        
        deprecated_policies = policy_repository.get_deprecated_policies()
        assert len(deprecated_policies) == 1
        assert deprecated_policies[0] == policy
    
    def test_get_refund_policies(self, policy_repository, policy):
        """Test getting refund policies."""
        policy_repository.save(policy)
        
        refund_policies = policy_repository.get_refund_policies()
        assert len(refund_policies) == 1
        assert refund_policies[0] == policy
    
    def test_get_policy_by_refund_period(self, policy_repository, policy):
        """Test getting policy by refund period."""
        policy_repository.save(policy)
        
        retrieved_policy = policy_repository.get_policy_by_refund_period(policy.refund_period)
        assert retrieved_policy == policy
        
        different_period = RefundPeriod(60)
        assert policy_repository.get_policy_by_refund_period(different_period) is None
    
    def test_name_uniqueness(self, policy_repository, policy):
        """Test name uniqueness constraint."""
        policy_repository.save(policy)
        
        # Try to save another policy with same name
        duplicate_policy = RefundPolicy(
            id=PolicyId(str(uuid4())),
            name=policy.name,  # Same name
            policy_type=PolicyType.EXTENDED,
            refund_period=RefundPeriod(0),
            conditions=PolicyConditions("Different conditions"),
            status=PolicyStatus.ACTIVE
        )
        
        with pytest.raises(ValueError, match="Policy with name .* already exists"):
            policy_repository.save(duplicate_policy)
    
    def test_update_policy_name(self, policy_repository, policy):
        """Test updating policy name."""
        policy_repository.save(policy)
        
        new_name = PolicyName("Updated Refund Policy")
        policy.name = new_name
        
        updated_policy = policy_repository.save(policy)
        assert updated_policy.name == new_name
        assert policy_repository.get_by_name(new_name.value) == policy
        assert policy_repository.get_by_name("Standard Refund Policy") is None
    
    def test_delete_policy(self, policy_repository, policy):
        """Test deleting policy."""
        policy_repository.save(policy)
        assert policy_repository.count() == 1
        
        result = policy_repository.delete(policy.id)
        assert result is True
        assert policy_repository.count() == 0
        assert policy_repository.get_by_id(policy.id) is None
        assert policy_repository.get_by_name(policy.name.value) is None
        
        # Try to delete non-existent policy
        result = policy_repository.delete(PolicyId(str(uuid4())))
        assert result is False
    
    def test_get_all_policies(self, policy_repository, policy):
        """Test getting all policies."""
        policy_repository.save(policy)
        
        policies = policy_repository.get_all()
        assert len(policies) == 1
        assert policies[0] == policy
    
    def test_exists(self, policy_repository, policy):
        """Test checking if policy exists."""
        assert not policy_repository.exists(policy.id)
        
        policy_repository.save(policy)
        assert policy_repository.exists(policy.id)
    
    def test_clear_repository(self, policy_repository, policy):
        """Test clearing repository."""
        policy_repository.save(policy)
        assert policy_repository.count() == 1
        
        policy_repository.clear()
        assert policy_repository.count() == 0
        assert policy_repository.get_by_id(policy.id) is None
    
    def test_multiple_policies(self, policy_repository):
        """Test repository with multiple policies."""
        policy1 = RefundPolicy.create_policy(
            name=PolicyName("Standard Refund Policy"),
            policy_type=PolicyType.STANDARD,
            refund_period=RefundPeriod(30),
            conditions=PolicyConditions("Standard refund conditions")
        )
        
        policy2 = RefundPolicy.create_policy(
            name=PolicyName("Extended Refund Policy"),
            policy_type=PolicyType.STANDARD,
            refund_period=RefundPeriod(60),
            conditions=PolicyConditions("Extended refund conditions")
        )
        
        policy_repository.save(policy1)
        policy_repository.save(policy2)
        
        assert policy_repository.count() == 2
        
        # Test type queries
        refund_policies = policy_repository.get_by_type(PolicyType.STANDARD)
        assert len(refund_policies) == 2
        assert policy1 in refund_policies
        assert policy2 in refund_policies
        
        # Test status queries
        active_policies = policy_repository.get_active_policies()
        assert len(active_policies) == 2
        assert policy1 in active_policies
        assert policy2 in active_policies

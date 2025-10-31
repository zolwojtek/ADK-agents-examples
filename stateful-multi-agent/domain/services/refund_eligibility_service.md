# RefundEligibilityService Documentation

## **📋 RefundEligibilityService Overview**

The `RefundEligibilityService` is a **domain service** that evaluates whether orders and their associated course access are eligible for refunds based on business policies. It orchestrates complex cross-aggregate logic to determine refund eligibility.

### **🎯 Purpose**
This service orchestrates **cross-aggregate operations** between Orders, Access, and Policies domains, specifically:
- **Evaluating refund eligibility** based on policy rules
- **Checking access records** for refund constraints
- **Applying business policies** to determine refund decisions
- **Providing detailed eligibility reports** for administrative decisions

### **🏗️ Architecture**

**Dependencies:**
- `AccessRepository` - For access record queries
- `PolicyRepository` - For refund policy retrieval
- `OrderRepository` - For order validation
- `AccessRecord` aggregate - For access business logic
- `RefundPolicy` aggregate - For policy business logic
- `Order` aggregate - For order validation
- Value objects: `OrderId`

**Key Methods:**

#### **1. `evaluate_refund_eligibility(order_id, current_time)`**
- **Purpose**: Comprehensive refund eligibility evaluation
- **Process**: 
  1. Validates order exists and is in paid status
  2. Gets all access records for the order
  3. Checks each access record against its policy
  4. Returns eligibility status with detailed reasoning
- **Returns**: `Tuple[bool, str]` - (is_eligible, reason)
- **Use Case**: Customer service refund requests, admin refund processing

#### **2. `get_eligible_courses_for_refund(order_id, current_time)`**
- **Purpose**: Get specific courses eligible for refund
- **Process**:
  1. Validates order and status
  2. Filters access records by policy eligibility
  3. Returns list of eligible access records
- **Returns**: `List[AccessRecord]` - Eligible courses only
- **Use Case**: Partial refund processing, detailed eligibility reports

#### **3. `_get_access_records_for_order(order)`**
- **Purpose**: Private method to retrieve all access records for an order
- **Process**:
  1. Iterates through order items
  2. Finds access record for each user-course combination
  3. Collects all found access records
- **Smart Logic**: Handles missing access records gracefully

#### **4. `_get_policy_for_access_record(access_record)`**
- **Purpose**: Private method to get refund policy for an access record
- **Current State**: Returns `None` (placeholder for future implementation)
- **Future Implementation**: Needs course-policy relationship mapping
- **Use Case**: Policy-based refund decisions

### **🔧 Design Patterns**

**Domain Service Pattern:**
- ✅ **Orchestrates** complex multi-aggregate operations
- ✅ **Coordinates** between Order, Access, and Policy domains
- ✅ **Applies** business rules across aggregates
- ✅ **Provides** high-level eligibility evaluation

**Repository Pattern:**
- ✅ **Dependency injection** of multiple repositories
- ✅ **Abstraction** over persistence details
- ✅ **Testable** with mock repositories

**Policy Pattern:**
- ✅ **Encapsulates** business rules in policies
- ✅ **Delegates** eligibility logic to aggregates
- ✅ **Maintainable** policy-based decisions

### **💡 Key Benefits**

1. **Business Rule Centralization**: All refund eligibility logic in one place
2. **Policy-Driven Decisions**: Flexible business rules through policies
3. **Detailed Reporting**: Comprehensive eligibility reasons
4. **Partial Refund Support**: Handles mixed eligibility scenarios
5. **Cross-Domain Coordination**: Seamless integration of multiple domains

### **🔄 Usage Examples**

```python
# Check refund eligibility
is_eligible, reason = service.evaluate_refund_eligibility(
    order_id=order_id,
    current_time=datetime.now()
)

# Get eligible courses for partial refund
eligible_courses = service.get_eligible_courses_for_refund(
    order_id=order_id,
    current_time=datetime.now()
)

# Process based on eligibility
if is_eligible:
    if "All courses eligible" in reason:
        # Full refund
        process_full_refund(order_id)
    else:
        # Partial refund
        process_partial_refund(order_id, eligible_courses)
```

### **🚨 Important Notes**

- **Policy Integration**: Currently returns `None` for policies (needs implementation)
- **Status Validation**: Ensures orders are in paid status before evaluation
- **Graceful Handling**: Handles missing access records and policies
- **Detailed Reasoning**: Provides specific reasons for eligibility decisions
- **Partial Refund Support**: Can handle mixed eligibility scenarios

### **🔮 Future Implementation Needs**

1. **Course-Policy Mapping**: Implement `_get_policy_for_access_record()`
2. **Policy Repository**: Connect to actual policy data
3. **Business Rules**: Implement complex eligibility logic
4. **Audit Trail**: Track eligibility decisions for compliance

This service follows DDD principles by orchestrating complex business rules while keeping domain logic in the appropriate aggregates and policies.

# OrderProcessingService Documentation

## **📋 OrderProcessingService Overview**

The `OrderProcessingService` is a **domain service** that orchestrates the complete order lifecycle, from payment processing to access management. It handles the critical business flow of converting paid orders into course access.

### **🎯 Purpose**
This service orchestrates **cross-aggregate operations** between Orders and Access domains, specifically:
- **Processing payments** and confirming orders
- **Granting course access** after successful payment
- **Processing refunds** and revoking access
- **Managing access lifecycle** during order operations

### **🏗️ Architecture**

**Dependencies:**
- `OrderRepository` - For order persistence
- `AccessRepository` - For access persistence
- `Order` aggregate - For order business logic
- `AccessRecord` aggregate - For access business logic
- Value objects: `OrderId`, `UserId`, `CourseId`, `Money`

**Key Methods:**

#### **1. `process_payment(order_id, payment_info, access_expires_at)`**
- **Purpose**: Complete the payment flow and grant access to courses
- **Process**: 
  1. Validates order exists and is in pending status
  2. Creates PaymentInfo value object
  3. Confirms payment on Order aggregate
  4. Saves order changes
  5. Grants access to all courses in the order
- **Use Case**: Payment gateway callback, manual payment confirmation

#### **2. `process_refund(order_id, refund_amount, refund_reason)`**
- **Purpose**: Process refund and revoke access to courses
- **Process**:
  1. Validates order exists and is in paid status
  2. Approves refund on Order aggregate
  3. Saves order changes
  4. Revokes access to all courses in the order
- **Use Case**: Admin refund processing, customer service refunds

#### **3. `_grant_course_access(user_id, course_id, purchase_date, access_expires_at)`**
- **Purpose**: Private method to handle access granting logic
- **Process**:
  1. Checks for existing access
  2. If active access exists, returns it
  3. If expired/revoked access exists, reactivates it
  4. If no access exists, creates new access record
- **Smart Logic**: Prevents duplicate access, handles reactivation

#### **4. `_revoke_course_access(user_id, course_id, reason)`**
- **Purpose**: Private method to handle access revocation
- **Process**:
  1. Finds existing access record
  2. Revokes access with reason
  3. Saves changes
- **Graceful Handling**: Returns None if no access found

### **🔧 Design Patterns**

**Domain Service Pattern:**
- ✅ **Orchestrates** complex cross-aggregate workflows
- ✅ **Coordinates** between Order and Access domains
- ✅ **Handles** transaction-like operations
- ✅ **Provides** high-level business operations

**Repository Pattern:**
- ✅ **Dependency injection** of multiple repositories
- ✅ **Abstraction** over persistence details
- ✅ **Testable** with mock repositories

**Private Method Pattern:**
- ✅ **Encapsulates** complex access logic
- ✅ **Reusable** across different operations
- ✅ **Maintainable** and focused methods

### **💡 Key Benefits**

1. **Business Flow Orchestration**: Complete order-to-access workflow
2. **Idempotency**: Smart handling of existing access records
3. **Error Handling**: Comprehensive validation and error messages
4. **Separation of Concerns**: Order logic vs Access logic properly separated
5. **Reusability**: Can be used by application services, APIs, admin tools

### **🔄 Usage Examples**

```python
# Payment processing
access_records = service.process_payment(
    order_id=order_id,
    payment_info={
        "payment_id": "pay_123",
        "method": "credit_card",
        "transaction_id": "txn_456"
    },
    access_expires_at=datetime.now() + timedelta(days=365)
)

# Refund processing
revoked_records = service.process_refund(
    order_id=order_id,
    refund_amount=Money(99.99, "USD"),
    refund_reason="Customer request"
)
```

### **🚨 Important Notes**

- **Status Validation**: Ensures orders are in correct state before processing
- **Access Deduplication**: Prevents creating duplicate access records
- **Access Reactivation**: Can reactivate expired access instead of creating new records
- **Error Propagation**: Clear error messages for debugging and user feedback

This service follows DDD principles by orchestrating complex business workflows while keeping domain logic in the appropriate aggregates.

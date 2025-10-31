# AccessLifecycleService Documentation

## **📋 AccessLifecycleService Overview**

The `AccessLifecycleService` is a **domain service** that manages the lifecycle of user access to courses. It handles access expiration, reactivation, and querying operations.

### **🎯 Purpose**
This service orchestrates **cross-aggregate operations** related to access management, specifically:
- **Expiring access** when time limits are reached
- **Reactivating access** for users who had expired/revoked access
- **Querying expired access** for administrative purposes

### **🏗️ Architecture**

**Dependencies:**
- `AccessRepository` - For persistence operations
- `AccessRecord` aggregate - For business logic
- Value objects: `UserId`, `CourseId`

**Key Methods:**

#### **1. `expire_access_records(current_time)`**
- **Purpose**: Batch expire all access records that have passed their expiration date
- **Process**: 
  1. Gets all active access records
  2. Checks each one against current time
  3. Expires records that are past due
  4. Saves changes and returns expired records
- **Use Case**: Scheduled job to clean up expired access

#### **2. `reactivate_user_access(user_id, course_id, new_expiration)`**
- **Purpose**: Restore access for a specific user-course combination
- **Process**:
  1. Finds existing access record
  2. Calls aggregate's `reactivate_access()` method
  3. Saves the updated record
- **Use Case**: Admin manually reactivating access after payment issues

#### **3. `get_expired_access_for_user(user_id)`**
- **Purpose**: Query all expired access for a specific user
- **Process**: Filters user's access records to find expired ones
- **Use Case**: User dashboard showing expired courses

### **🔧 Design Patterns**

**Domain Service Pattern:**
- ✅ **Orchestrates** cross-aggregate operations
- ✅ **Doesn't contain** business logic (delegates to aggregates)
- ✅ **Handles** persistence coordination
- ✅ **Provides** high-level operations

**Repository Pattern:**
- ✅ **Dependency injection** of `AccessRepository`
- ✅ **Abstraction** over persistence details
- ✅ **Testable** with mock repositories

### **💡 Key Benefits**

1. **Separation of Concerns**: Access lifecycle logic is centralized
2. **Reusability**: Can be used by application services, scheduled jobs, admin tools
3. **Testability**: Easy to unit test with mocked dependencies
4. **Consistency**: Ensures proper aggregate method calls and persistence

### **🔄 Usage Examples**

```python
# Scheduled job to expire access
expired = service.expire_access_records(datetime.now())

# Admin reactivating user access
service.reactivate_user_access(user_id, course_id, new_expiration)

# User dashboard showing expired courses
expired_courses = service.get_expired_access_for_user(user_id)
```

This service follows DDD principles by keeping business logic in aggregates while providing orchestration for complex operations that span multiple aggregates or require coordination with persistence.

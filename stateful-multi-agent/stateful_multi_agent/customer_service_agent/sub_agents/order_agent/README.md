# Order Agent Documentation

## Overview

This agent is one of the sub-agents for the main customer_service_agent and is responsible for managing purchase history and processing refund operations. It provides comprehensive order management capabilities while ensuring secure and accurate transaction handling.

## Capabilities

1. **Order Management**
   - Access and explain order history
   - Process refund requests
   - Verify purchase eligibility
   - Track order status

2. **Refund Processing**
   - Verify refund eligibility
   - Handle refund requests
   - Explain refund policies
   - Document refund reasons

3. **Customer Support**
   - Provide order details
   - Answer purchase queries
   - Handle order issues
   - Coordinate with other agents

## Tools

1. **get_order_history**
   - Retrieves detailed order history
   - Includes purchase dates and status
   - Provides course information
   - Tracks refund eligibility

2. **process_refund**
   - Handles refund requests
   - Validates eligibility
   - Updates user state
   - Records refund details

## State Management

The agent maintains:
- Purchase records
- Refund history
- Transaction timestamps
- Order status updates

## Security Considerations

1. **Transaction Validation**
   - Verify user identity
   - Check refund eligibility
   - Validate state updates
   - Track transaction history

2. **Data Protection**
   - Secure order information
   - Protected refund processing
   - State validation
   - Error handling

## Important Notes

- In Google AI Agent Builder (ADK), an agent can use either built-in tools or custom-defined tools in a single turn — not both together
- Different execution paths should be tested thoroughly:
  - Non-existent orders
  - Invalid refund requests
  - Data access issues
  - State update failures
- Regular auditing of refund operations is recommended
- Integration with payment systems requires careful monitoring

## Testing Guidelines

1. Test order operations:
   - Order history retrieval
   - Refund processing
   - State updates
   - Error scenarios

2. Verify data handling:
   - Order record accuracy
   - Refund eligibility checks
   - Transaction logging
   - State consistency

3. Check security measures:
   - User verification
   - Access control
   - Data protection
   - Transaction validation
# Sales Agent Documentation

## Overview

This agent is one of the sub-agents for the main customer_service_agent and is responsible for handling sales of IT Developers Platform courses. It manages course purchases, provides pricing information, and ensures proper course access after purchase.

## Capabilities

1. **Course Sales**
   - Present course value propositions
   - Handle course purchase process
   - Verify existing purchases
   - Provide pricing information

2. **Customer Support**
   - Direct post-purchase queries
   - Handle pricing questions
   - Manage course access verification
   - Provide course information

3. **Error Handling**
   - Handle purchase errors gracefully
   - Validate state updates
   - Provide clear error messages

## Tools

1. **get_courses**
   - Fetches list of available courses with details
   - Includes pricing, duration, and level information
   - Returns structured course data

2. **purchase_course**
   - Processes course purchases
   - Updates user state
   - Validates purchase eligibility
   - Records transaction history

## State Management

The agent maintains and updates:
- Purchase history
- Interaction records
- Course access information
- Transaction details

## Security Considerations

1. **Purchase Validation**
   - Verifies course availability
   - Checks for duplicate purchases
   - Validates state updates

2. **Data Protection**
   - Secure handling of purchase information
   - State validation before updates
   - Error handling for sensitive operations

## Important Notes

- It's crucial to analyze the agent's work from different security angles
- Consider adding human verification for purchases above certain thresholds
- Implement rate limiting for purchase attempts
- Regular auditing of purchase transactions is recommended
- Integration with payment processing should be carefully monitored

## Testing Guidelines

1. Test purchase flows:
   - New course purchase
   - Duplicate purchase attempts
   - Invalid course IDs
   - State update failures

2. Verify error handling:
   - Network issues
   - State validation failures
   - Invalid input data
   - Rate limiting scenarios
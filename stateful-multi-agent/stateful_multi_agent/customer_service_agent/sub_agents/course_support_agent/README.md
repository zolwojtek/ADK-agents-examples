# Course Support Agent Documentation

## Overview

This agent is one of the sub-agents for the main customer_service_agent and is responsible for answering questions about available courses and their content. It provides comprehensive course support while ensuring users have appropriate access to course materials.

## Capabilities

1. **Course Information Access**
   - Access and provide course content information
   - Verify course ownership before providing details
   - Navigate users to specific course sections
   - Track course progress

2. **Learning Support**
   - Explain course concepts clearly
   - Connect course sections logically
   - Provide learning guidance
   - Encourage hands-on practice

3. **Error Handling**
   - Handle course access errors gracefully
   - Validate state updates
   - Provide clear error messages
   - Manage access restrictions

## Tools

1. **get_courses**
   - Fetches list of available courses
   - Returns course metadata
   - Supports course discovery
   - Validates course existence

2. **get_course_content**
   - Retrieves detailed course content
   - Provides section information
   - Supports content navigation
   - Handles access control

## Content Management

The agent handles:
- Course structure
- Learning materials
- Progress tracking
- Access verification

## State Management

Maintains and updates:
- Course access records
- Learning progress
- Interaction history
- User preferences

## Important Notes

- In Google AI Agent Builder (ADK), an agent can use either built-in tools or custom-defined tools in a single turn — not both together
- Different execution paths should be tested:
  - Non-existent courses
  - Access restrictions
  - Content availability
  - State updates
- Regular content updates should be reflected immediately
- Integration with learning management systems requires careful handling

## Testing Guidelines

1. Test content access:
   - Course information retrieval
   - Content navigation
   - Access control
   - Error handling

2. Verify learning support:
   - Concept explanations
   - Section connections
   - Progress tracking
   - Practice guidance

3. Check error scenarios:
   - Invalid course requests
   - Access restrictions
   - Content updates
   - State validation

## Best Practices

1. Content Delivery
   - Provide clear explanations
   - Use consistent formatting
   - Include practical examples
   - Support different learning styles

2. Access Control
   - Verify course ownership
   - Check access expiration
   - Handle restrictions gracefully
   - Maintain access logs

3. Progress Tracking
   - Monitor section completion
   - Track learning milestones
   - Provide progress feedback
   - Support learning goals
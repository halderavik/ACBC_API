# ACBC API Documentation

## Overview

The ACBC (Adaptive Choice-Based Conjoint) API is a FastAPI-based backend service that implements a complete conjoint analysis workflow. The API supports three main phases: BYO (Build-Your-Own) configuration, screening tasks, and tournament choices.

**Base URL:** `https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com`

**API Documentation:** `https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com/docs`

---

## Table of Contents

1. [Authentication](#authentication)
2. [Workflow Overview](#workflow-overview)
3. [BYO Configuration](#byo-configuration)
4. [Screening Tasks](#screening-tasks)
5. [Tournament Choices](#tournament-choices)
6. [Error Handling](#error-handling)
7. [Data Models](#data-models)
8. [Examples](#examples)

---

## Authentication

Currently, the API does not require authentication. All endpoints are publicly accessible.

---

## Workflow Overview

The ACBC workflow consists of three sequential phases:

1. **BYO Configuration** - Define attributes and their possible values
2. **Screening Tasks** - Rate concept combinations to establish initial preferences
3. **Tournament Choices** - Make pairwise choices to refine preference estimates

Each phase builds upon the previous one, creating an adaptive learning system.

---

## BYO Configuration

### POST /api/byo-config

Creates a new session with BYO (Build-Your-Own) configuration and initializes screening tasks.

**Endpoint:** `POST /api/byo-config`

**Request Body:**
```json
{
  "session_id": "string (optional)",
  "selected_attributes": {
    "attribute_name": ["value1", "value2", "value3"],
    "another_attribute": ["option1", "option2", "option3"]
  }
}
```

**Parameters:**
- `session_id` (optional): Custom session identifier. If not provided, a UUID will be generated
- `selected_attributes` (required): Dictionary where keys are attribute names and values are arrays of possible values

**Example Request:**
```json
{
  "session_id": "test123",
  "selected_attributes": {
    "brand": ["Nike", "Adidas", "Puma"],
    "material": ["leather", "canvas", "synthetic"],
    "style": ["casual", "athletic", "formal"]
  }
}
```

**Response:**
```json
{
  "session_id": "test123"
}
```

**What Happens:**
- Creates a new session record in the database
- Stores the BYO configuration
- Generates screening tasks based on the attribute combinations
- Returns the session ID for future API calls

**Error Responses:**
- `422 Unprocessable Entity`: Missing or invalid `selected_attributes`
- `500 Internal Server Error`: Database or processing errors

---

## Screening Tasks

### GET /api/screening/design

Retrieves the screening design for a specific session.

**Endpoint:** `GET /api/screening/design?session_id={session_id}`

**Parameters:**
- `session_id` (required): The session ID from the BYO configuration

**Example Request:**
```
GET /api/screening/design?session_id=test123
```

**Response:**
```json
[
  {
    "id": 1,
    "concept": {
      "brand": "Nike",
      "material": "leather",
      "style": "casual"
    },
    "position": 1,
    "response": null
  },
  {
    "id": 2,
    "concept": {
      "brand": "Adidas",
      "material": "canvas",
      "style": "athletic"
    },
    "position": 2,
    "response": null
  }
]
```

**Response Fields:**
- `id`: Unique identifier for the screening task
- `concept`: Object containing attribute-value combinations
- `position`: Order of presentation
- `response`: User's response (null until submitted)

**Error Responses:**
- `400 Bad Request`: Missing session_id parameter
- `404 Not Found`: Session not found

### POST /api/screening/responses

Submits screening responses and calculates initial utility estimates.

**Endpoint:** `POST /api/screening/responses`

**Request Body:**
```json
{
  "session_id": "string",
  "responses": [boolean, boolean, boolean, ...]
}
```

**Parameters:**
- `session_id` (required): The session ID
- `responses` (required): Array of boolean values corresponding to each screening task (true = like, false = dislike)

**Example Request:**
```json
{
  "session_id": "test123",
  "responses": [true, false, true, false, true]
}
```

**Response:**
```json
{
  "status": "ok"
}
```

**What Happens:**
- Records user responses for each screening task
- Calculates initial utility estimates based on preferences
- Updates the session with utility data for tournament phase

**Error Responses:**
- `404 Not Found`: Session not found
- `422 Unprocessable Entity`: Invalid response format

---

## Tournament Choices

### GET /api/tournament/choice

Retrieves tournament choice tasks for a specific session and task number.

**Endpoint:** `GET /api/tournament/choice?session_id={session_id}&task_number={task_number}`

**Parameters:**
- `session_id` (required): The session ID
- `task_number` (optional): Task number (defaults to 1)

**Example Request:**
```
GET /api/tournament/choice?session_id=test123&task_number=1
```

**Response:**
```json
{
  "task_number": 1,
  "concepts": [
    {
      "id": 1,
      "attributes": {
        "brand": "Nike",
        "material": "leather",
        "style": "casual"
      }
    },
    {
      "id": 2,
      "attributes": {
        "brand": "Adidas",
        "material": "canvas",
        "style": "athletic"
      }
    }
  ]
}
```

**Response Fields:**
- `task_number`: Current tournament task number
- `concepts`: Array of concept pairs for choice tasks

**Error Responses:**
- `400 Bad Request`: Missing session_id or invalid task_number
- `404 Not Found`: Session not found

### POST /api/tournament/choice-response

Submits a choice response and updates utility estimates.

**Endpoint:** `POST /api/tournament/choice-response`

**Request Body:**
```json
{
  "session_id": "string",
  "task_number": "integer",
  "selected_concept_id": "integer"
}
```

**Parameters:**
- `session_id` (required): The session ID
- `task_number` (required): Current task number
- `selected_concept_id` (required): ID of the chosen concept

**Example Request:**
```json
{
  "session_id": "test123",
  "task_number": 1,
  "selected_concept_id": 1
}
```

**Response:**
```json
{
  "next_task": 2
}
```

**What Happens:**
- Records the user's choice
- Updates utility estimates using adaptive algorithms
- Returns the next task number

**Error Responses:**
- `404 Not Found`: Session or task not found
- `422 Unprocessable Entity`: Invalid concept ID

---

## Error Handling

### Common HTTP Status Codes

- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request parameters
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Validation error
- **500 Internal Server Error**: Server error

### Error Response Format

```json
{
  "detail": "Error message description"
}
```

For validation errors:
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "field_name"],
      "msg": "Field required",
      "input": {}
    }
  ]
}
```

---

## Data Models

### BYOConfig
```json
{
  "session_id": "string (optional)",
  "selected_attributes": {
    "attribute_name": ["value1", "value2", "value3"]
  }
}
```

### ScreeningDesignOut
```json
{
  "id": "integer",
  "concept": {
    "attribute_name": "value"
  },
  "position": "integer",
  "response": "boolean (nullable)"
}
```

### ScreeningResponseIn
```json
{
  "session_id": "string",
  "responses": ["boolean"]
}
```

### TournamentDesignOut
```json
{
  "task_number": "integer",
  "concepts": [
    {
      "id": "integer",
      "attributes": {
        "attribute_name": "value"
      }
    }
  ]
}
```

### ChoiceResponseIn
```json
{
  "session_id": "string",
  "task_number": "integer",
  "selected_concept_id": "integer"
}
```

---

## Examples

### Complete Workflow Example

#### 1. Create BYO Configuration
```bash
curl -X POST "https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com/api/byo-config" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "example123",
    "selected_attributes": {
      "color": ["red", "blue", "green"],
      "size": ["small", "medium", "large"],
      "price": [10, 20, 30]
    }
  }'
```

#### 2. Get Screening Design
```bash
curl "https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com/api/screening/design?session_id=example123"
```

#### 3. Submit Screening Responses
```bash
curl -X POST "https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com/api/screening/responses" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "example123",
    "responses": [true, false, true, false, true]
  }'
```

#### 4. Get Tournament Choice
```bash
curl "https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com/api/tournament/choice?session_id=example123&task_number=1"
```

#### 5. Submit Choice Response
```bash
curl -X POST "https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com/api/tournament/choice-response" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "example123",
    "task_number": 1,
    "selected_concept_id": 1
  }'
```

### Postman Collection

You can import these requests into Postman:

1. **BYO Configuration**
   - Method: POST
   - URL: `{{base_url}}/api/byo-config`
   - Body: Raw JSON with BYOConfig

2. **Screening Design**
   - Method: GET
   - URL: `{{base_url}}/api/screening/design?session_id={{session_id}}`

3. **Screening Responses**
   - Method: POST
   - URL: `{{base_url}}/api/screening/responses`
   - Body: Raw JSON with ScreeningResponseIn

4. **Tournament Choice**
   - Method: GET
   - URL: `{{base_url}}/api/tournament/choice?session_id={{session_id}}&task_number={{task_number}}`

5. **Choice Response**
   - Method: POST
   - URL: `{{base_url}}/api/tournament/choice-response`
   - Body: Raw JSON with ChoiceResponseIn

---

## Frequently Asked Questions

### Q: How many attributes can I define in BYO configuration?
A: There's no hard limit, but typically 3-5 attributes work best for user experience.

### Q: How many values can each attribute have?
A: Recommended 2-5 values per attribute for optimal analysis.

### Q: How many screening tasks are generated?
A: The system generates a subset of all possible combinations, typically 5-10 tasks.

### Q: Can I reuse a session ID?
A: No, each session ID should be unique. If you provide an existing ID, it will create a new session.

### Q: How many tournament tasks are there?
A: The number varies based on the adaptive algorithm, typically 10-20 tasks.

### Q: What happens if I skip a screening response?
A: All screening responses must be provided before proceeding to tournament tasks.

### Q: Can I get the final utility estimates?
A: Currently, the API focuses on the choice process. Utility estimates are used internally for adaptive learning.

### Q: Is the API stateless?
A: No, the API maintains session state in the database throughout the workflow.

---

## Support

For technical support or questions about the API:

1. Check the interactive documentation at `/docs`
2. Review the error messages for specific issues
3. Ensure all required parameters are provided
4. Verify the request format matches the expected schema

---

## Version Information

- **API Version**: 1.0.0
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **Deployment**: Heroku 
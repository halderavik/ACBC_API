# API Error Troubleshooting Guide

## Common Error Codes and Solutions

### 422 Unprocessable Entity

This error occurs when the request body doesn't match the expected schema.

#### Screening Responses Endpoint (`POST /api/screening/responses`)

**Correct Format:**
```json
{
  "session_id": "your_session_id",
  "responses": [true, false, true, false, true]
}
```

**Common Mistakes:**
1. **Missing `responses` field**
   ```json
   {
     "session_id": "test123"
     // Missing responses array
   }
   ```

2. **`responses` is not an array**
   ```json
   {
     "session_id": "test123",
     "responses": "true,false,true"  // Should be an array, not a string
   }
   ```

3. **`responses` contains non-boolean values**
   ```json
   {
     "session_id": "test123",
     "responses": ["yes", "no", "yes"]  // Should be [true, false, true]
   }
   ```

4. **Wrong number of responses**
   - The number of responses must match the number of screening tasks
   - Check the screening design first to see how many tasks exist

**How to Fix:**
1. First get the screening design:
   ```bash
   GET /api/screening/design?session_id=your_session_id
   ```
2. Count the number of tasks returned
3. Provide exactly that many boolean responses

#### BYO Config Endpoint (`POST /api/byo-config`)

**Correct Format:**
```json
{
  "session_id": "optional_session_id",
  "selected_attributes": {
    "brand": ["Nike", "Adidas", "Puma"],
    "material": ["leather", "canvas", "synthetic"],
    "style": ["casual", "athletic", "formal"]
  }
}
```

**Common Mistakes:**
1. **Missing `selected_attributes` field**
   ```json
   {
     "session_id": "test123"
     // Missing selected_attributes
   }
   ```

2. **Empty `selected_attributes`**
   ```json
   {
     "session_id": "test123",
     "selected_attributes": {}  // Must have at least one attribute
   }
   ```

3. **Empty attribute values**
   ```json
   {
     "session_id": "test123",
     "selected_attributes": {
       "brand": []  // Must have at least one value
     }
   }
   ```

### 500 Internal Server Error

#### Tournament Choice Endpoint (`GET /api/tournament/choice`)

**Common Causes:**
1. **Session not found**
   - The session ID doesn't exist in the database
   - Solution: Create a new session using BYO config first

2. **Screening responses not submitted**
   - Tournament tasks require screening responses to be submitted first
   - Solution: Submit screening responses before accessing tournament

3. **Database connection issues**
   - Temporary database connectivity problems
   - Solution: Retry the request

**How to Fix:**
1. Verify the session exists:
   ```bash
   GET /api/screening/design?session_id=your_session_id
   ```
2. If session doesn't exist, create it:
   ```bash
   POST /api/byo-config
   {
     "session_id": "your_session_id",
     "selected_attributes": {
       "attribute1": ["value1", "value2"],
       "attribute2": ["value3", "value4"]
     }
   }
   ```
3. Submit screening responses:
   ```bash
   POST /api/screening/responses
   {
     "session_id": "your_session_id",
     "responses": [true, false, true, false, true]
   }
   ```
4. Then access tournament:
   ```bash
   GET /api/tournament/choice?session_id=your_session_id&task_number=1
   ```

### 404 Not Found

**Common Causes:**
1. **Session doesn't exist**
2. **Task number doesn't exist**
3. **Endpoint URL is incorrect**

**How to Fix:**
1. Check the session ID is correct
2. Verify the session exists in the database
3. Use task_number=1 for the first tournament task

## Testing Your API Calls

### Step-by-Step Testing

1. **Health Check**
   ```bash
   GET /health
   ```
   Expected: `{"status": "healthy"}`

2. **Create Session**
   ```bash
   POST /api/byo-config
   {
     "session_id": "test_session",
     "selected_attributes": {
       "brand": ["Nike", "Adidas"],
       "material": ["leather", "canvas"]
     }
   }
   ```
   Expected: `{"session_id": "test_session"}`

3. **Get Screening Design**
   ```bash
   GET /api/screening/design?session_id=test_session
   ```
   Expected: Array of screening tasks

4. **Submit Screening Responses**
   ```bash
   POST /api/screening/responses
   {
     "session_id": "test_session",
     "responses": [true, false, true, false, true]
   }
   ```
   Expected: `{"status": "ok"}`

5. **Get Tournament Choice**
   ```bash
   GET /api/tournament/choice?session_id=test_session&task_number=1
   ```
   Expected: Tournament task with concepts

### Using curl

```bash
# Health check
curl "https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com/health"

# Create session
curl -X POST "https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com/api/byo-config" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_session",
    "selected_attributes": {
      "brand": ["Nike", "Adidas"],
      "material": ["leather", "canvas"]
    }
  }'

# Get screening design
curl "https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com/api/screening/design?session_id=test_session"

# Submit screening responses
curl -X POST "https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com/api/screening/responses" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_session",
    "responses": [true, false, true, false, true]
  }'

# Get tournament choice
curl "https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com/api/tournament/choice?session_id=test_session&task_number=1"
```

### Using PowerShell

```powershell
# Health check
Invoke-WebRequest -Uri "https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com/health" -Method GET

# Create session
$body = @{
    session_id = "test_session"
    selected_attributes = @{
        brand = @("Nike", "Adidas")
        material = @("leather", "canvas")
    }
} | ConvertTo-Json

Invoke-WebRequest -Uri "https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com/api/byo-config" -Method POST -Body $body -ContentType "application/json"

# Get screening design
Invoke-WebRequest -Uri "https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com/api/screening/design?session_id=test_session" -Method GET

# Submit screening responses
$body = @{
    session_id = "test_session"
    responses = @($true, $false, $true, $false, $true)
} | ConvertTo-Json

Invoke-WebRequest -Uri "https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com/api/screening/responses" -Method POST -Body $body -ContentType "application/json"

# Get tournament choice
Invoke-WebRequest -Uri "https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com/api/tournament/choice?session_id=test_session&task_number=1" -Method GET
```

## Debugging Tips

1. **Check the request body format**
   - Ensure all required fields are present
   - Verify data types (arrays, booleans, strings)
   - Use proper JSON syntax

2. **Verify session exists**
   - Always check if the session exists before using it
   - Create a new session if needed

3. **Follow the workflow order**
   - BYO Config → Screening Design → Screening Responses → Tournament Choice

4. **Check response details**
   - Look at the full error response for specific validation messages
   - Use the `/docs` endpoint for interactive API documentation

5. **Use the test script**
   - Run `python test_all_endpoints.py` to test all endpoints
   - Use `python test_acbc_survey_slow.ps1` for full workflow testing

## Support

If you continue to experience issues:

1. Check the API health: `GET /health`
2. Verify your request format matches the examples above
3. Test with a simple session first
4. Check the interactive documentation at `/docs`
5. Review the complete API documentation in `API.md` 
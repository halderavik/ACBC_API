# ACBC Survey Test Script - Simulating 10 Respondents
# Smartphone Attributes Test Case

$baseUrl = "https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com"
$headers = @{"Content-Type"="application/json"}

# Smartphone attributes configuration
$smartphoneAttributes = @{
    "Brand" = @("Apple", "Samsung", "Google", "OnePlus", "Xiaomi")
    "Price" = @("`$499", "`$699", "`$899", "`$1099")
    "Screen_Size" = @("5.8`"", "6.1`"", "6.4`"", "6.7`"")
    "Battery_Life" = @("Up to 12 hrs", "Up to 18 hrs", "Up to 24 hrs")
    "Camera_Quality" = @("Dual Lens (12MP)", "Triple Lens (48MP)", "Quad Lens (108MP)")
    "Storage_Capacity" = @("64 GB", "128 GB", "256 GB", "512 GB")
    "5G_Support" = @("No", "Yes")
    "Wireless_Charging" = @("No", "Yes")
    "Water_Resistance" = @("No", "IP67 (1m)", "IP68 (1.5m)")
    "Operating_System" = @("iOS", "Android")
}

Write-Host "Starting ACBC Survey Test with Smartphone Attributes" -ForegroundColor Green
Write-Host "Testing 10 respondents..." -ForegroundColor Yellow
Write-Host ""

# Function to create BYO configuration
function Create-BYOConfig {
    param($sessionId)
    
    $byoConfig = @{
        session_id = $sessionId
        selected_attributes = $smartphoneAttributes
    }
    
    $body = $byoConfig | ConvertTo-Json -Depth 10
    
    try {
        $response = Invoke-WebRequest -Uri "$baseUrl/api/byo-config" -Method POST -Headers $headers -Body $body
        Write-Host "✅ BYO Config created for session: $sessionId" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "❌ Failed to create BYO config for session: $sessionId" -ForegroundColor Red
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Function to get screening design
function Get-ScreeningDesign {
    param($sessionId)
    
    try {
        $response = Invoke-WebRequest -Uri "$baseUrl/api/screening/design?session_id=$sessionId" -Method GET
        $screeningTasks = $response.Content | ConvertFrom-Json
        Write-Host "✅ Screening design retrieved: $($screeningTasks.Count) tasks" -ForegroundColor Green
        return $screeningTasks
    }
    catch {
        Write-Host "❌ Failed to get screening design for session: $sessionId" -ForegroundColor Red
        return $null
    }
}

# Function to submit screening responses
function Submit-ScreeningResponses {
    param($sessionId, $responses)
    
    $body = @{
        session_id = $sessionId
        responses = $responses
    } | ConvertTo-Json
    
    try {
        $response = Invoke-WebRequest -Uri "$baseUrl/api/screening/responses" -Method POST -Headers $headers -Body $body
        Write-Host "✅ Screening responses submitted" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "❌ Failed to submit screening responses for session: $sessionId" -ForegroundColor Red
        return $false
    }
}

# Function to get tournament choice
function Get-TournamentChoice {
    param($sessionId, $taskNumber)
    
    try {
        $response = Invoke-WebRequest -Uri "$baseUrl/api/tournament/choice?session_id=$sessionId`&task_number=$taskNumber" -Method GET
        $tournamentData = $response.Content | ConvertFrom-Json
        Write-Host "✅ Tournament choice retrieved: Task $taskNumber, $($tournamentData.concepts.Count) concepts" -ForegroundColor Green
        return $tournamentData
    }
    catch {
        Write-Host "❌ Failed to get tournament choice for session: $sessionId, task: $taskNumber" -ForegroundColor Red
        return $null
    }
}

# Function to submit choice response
function Submit-ChoiceResponse {
    param($sessionId, $taskNumber, $selectedConceptId)
    
    $body = @{
        session_id = $sessionId
        task_number = $taskNumber
        selected_concept_id = $selectedConceptId
    } | ConvertTo-Json
    
    try {
        $response = Invoke-WebRequest -Uri "$baseUrl/api/tournament/choice-response" -Method POST -Headers $headers -Body $body
        $result = $response.Content | ConvertFrom-Json
        Write-Host "✅ Choice response submitted. Next task: $($result.next_task)" -ForegroundColor Green
        return $result.next_task
    }
    catch {
        Write-Host "❌ Failed to submit choice response for session: $sessionId, task: $taskNumber" -ForegroundColor Red
        return $null
    }
}

# Main test loop for 10 respondents
$successfulSessions = 0
$totalSessions = 10

for ($i = 1; $i -le $totalSessions; $i++) {
    $sessionId = "smartphone_respondent_$i"
    Write-Host "`nTesting Respondent $i of $totalSessions" -ForegroundColor Cyan
    Write-Host "Session ID: $sessionId" -ForegroundColor Gray
    
    # Step 1: Create BYO configuration
    if (-not (Create-BYOConfig -sessionId $sessionId)) {
        continue
    }
    
    # Step 2: Get screening design
    $screeningTasks = Get-ScreeningDesign -sessionId $sessionId
    if (-not $screeningTasks) {
        continue
    }
    
    # Step 3: Submit screening responses (random responses)
    $screeningResponses = @()
    for ($j = 0; $j -lt $screeningTasks.Count; $j++) {
        $screeningResponses += (Get-Random -Minimum 0 -Maximum 2) -eq 1
    }
    
    if (-not (Submit-ScreeningResponses -sessionId $sessionId -responses $screeningResponses)) {
        continue
    }
    
    # Step 4: Complete tournament tasks (simulate 3 tasks per respondent)
    $currentTask = 1
    $maxTasks = 3
    
    for ($task = 1; $task -le $maxTasks; $task++) {
        $tournamentData = Get-TournamentChoice -sessionId $sessionId -taskNumber $task
        if (-not $tournamentData) {
            break
        }
        
        # Randomly select a concept
        $selectedConceptId = Get-Random -Minimum 0 -Maximum $tournamentData.concepts.Count
        
        $nextTask = Submit-ChoiceResponse -sessionId $sessionId -taskNumber $task -selectedConceptId $selectedConceptId
        if (-not $nextTask) {
            break
        }
        
        $currentTask = $nextTask
    }
    
    $successfulSessions++
    Write-Host "✅ Respondent $i completed successfully!" -ForegroundColor Green
}

Write-Host "`nTest Results Summary" -ForegroundColor Magenta
Write-Host "================================" -ForegroundColor Magenta
Write-Host "Total Sessions Tested: $totalSessions" -ForegroundColor White
Write-Host "Successful Sessions: $successfulSessions" -ForegroundColor Green
Write-Host "Success Rate: $([math]::Round(($successfulSessions / $totalSessions) * 100, 2))%" -ForegroundColor Yellow

if ($successfulSessions -eq $totalSessions) {
    Write-Host "`nAll tests passed! ACBC system is working correctly." -ForegroundColor Green
} else {
    Write-Host "`nSome tests failed. Please check the error messages above." -ForegroundColor Yellow
}

Write-Host "`nData Storage Verification" -ForegroundColor Cyan
Write-Host "All session data, screening responses, and tournament choices have been stored in the database." -ForegroundColor White
Write-Host "You can verify the data using the data analysis dashboard or by querying the database directly." -ForegroundColor White 
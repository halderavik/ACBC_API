# ACBC Data Viewer Script
# View stored data from the API

$baseUrl = "https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com"

Write-Host "ACBC Data Viewer" -ForegroundColor Green
Write-Host "=================" -ForegroundColor Green
Write-Host ""

# Function to get session data
function Get-SessionData {
    param($sessionId)
    
    Write-Host "Session: $sessionId" -ForegroundColor Cyan
    Write-Host "----------------------------------------" -ForegroundColor Gray
    
    try {
        # Get screening design and responses
        $response = Invoke-WebRequest -Uri "$baseUrl/api/screening/design?session_id=$sessionId" -Method GET
        $screeningData = $response.Content | ConvertFrom-Json
        
        Write-Host "Screening Tasks:" -ForegroundColor Yellow
        foreach ($task in $screeningData) {
            $concept = $task.concept
            Write-Host "  Task $($task.position): $($concept.Brand) $($concept.Price) - Response: $($task.response)" -ForegroundColor White
        }
        
        Write-Host ""
        Write-Host "Tournament Tasks:" -ForegroundColor Yellow
        
        # Check for tournament tasks (up to 5 tasks)
        for ($taskNum = 1; $taskNum -le 5; $taskNum++) {
            try {
                $tournamentResponse = Invoke-WebRequest -Uri "$baseUrl/api/tournament/choice?session_id=$sessionId`&task_number=$taskNum" -Method GET
                $tournamentData = $tournamentResponse.Content | ConvertFrom-Json
                
                Write-Host "  Task $taskNum`: $($tournamentData.concepts.Count) concepts" -ForegroundColor White
                foreach ($concept in $tournamentData.concepts) {
                    $attrs = $concept.attributes
                    Write-Host "    Concept $($concept.id): $($attrs.Brand) $($attrs.Price)" -ForegroundColor Gray
                }
            }
            catch {
                # No more tournament tasks
                break
            }
        }
        
        Write-Host ""
        return $true
    }
    catch {
        Write-Host "Error retrieving data for session: $sessionId" -ForegroundColor Red
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# View data for all test respondents
$totalSessions = 10
$successfulViews = 0

for ($i = 1; $i -le $totalSessions; $i++) {
    $sessionId = "smartphone_respondent_$i"
    
    if (Get-SessionData -sessionId $sessionId) {
        $successfulViews++
    }
    
    Write-Host ""
}

Write-Host "Data View Summary" -ForegroundColor Magenta
Write-Host "==================" -ForegroundColor Magenta
Write-Host "Total Sessions: $totalSessions" -ForegroundColor White
Write-Host "Successfully Viewed: $successfulViews" -ForegroundColor Green

Write-Host ""
Write-Host "To view more detailed data, visit:" -ForegroundColor Cyan
Write-Host "http://localhost:5000 - Data Analysis Dashboard" -ForegroundColor Yellow
Write-Host "https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com/docs - API Documentation" -ForegroundColor Yellow 
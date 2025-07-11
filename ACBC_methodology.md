# ACBC (Adaptive Choice-Based Conjoint) Methodology

## Overview

This document describes the ACBC (Adaptive Choice-Based Conjoint) methodology implemented in our API, including the algorithmic approach, process flow, and integration with the Qualtrics survey platform.

**ACBC API Version:** 1.4.0  
**Algorithm Implementation:** Numpy-powered advanced statistical algorithms  
**Platform Integration:** Qualtrics survey platform  

---

## Table of Contents

1. [ACBC Methodology Overview](#acbc-methodology-overview)
2. [Three-Phase Process](#three-phase-process)
3. [Algorithm Details](#algorithm-details)
4. [Qualtrics Integration](#qualtrics-integration)
5. [Statistical Foundations](#statistical-foundations)
6. [Implementation Details](#implementation-details)
7. [Best Practices](#best-practices)
8. [Example Workflow](#example-workflow)

---

## ACBC Methodology Overview

Adaptive Choice-Based Conjoint (ACBC) is an advanced market research methodology that combines the efficiency of choice-based conjoint analysis with adaptive learning to create personalized product configurations. Our implementation uses sophisticated algorithms to optimize the research process and improve respondent engagement.

### Key Advantages

- **Personalized Experience**: Each respondent sees different product combinations based on their preferences
- **Efficient Data Collection**: Reduces respondent fatigue while maximizing information gain
- **Statistical Robustness**: Uses D-optimal design principles for reliable parameter estimation
- **Real-time Adaptation**: Continuously updates preference estimates during the survey
- **Qualtrics Integration**: Seamless integration with the world's leading survey platform

---

## Three-Phase Process

Our ACBC implementation follows a three-phase process that progressively refines preference estimates:

### Phase 1: BYO (Build-Your-Own) Configuration

**Purpose**: Establish the respondent's ideal product configuration

**Process**:
1. Respondent selects their preferred level for each attribute
2. System creates a "BYO profile" representing their ideal product
3. This profile serves as the foundation for subsequent phases

**Algorithm**:
```python
def generate_byo_profile(byo: Dict[str, List[Any]]) -> Dict[str, Any]:
    """
    Generate a BYO profile by selecting one level per attribute.
    This represents the respondent's ideal product.
    """
    byo_profile = {}
    for attribute, levels in byo.items():
        # Select respondent's chosen level for each attribute
        byo_profile[attribute] = respondent_choice[attribute]
    return byo_profile
```

### Phase 2: Screening Tasks

**Purpose**: Establish initial preference boundaries and acceptable/unacceptable levels

**Process**:
1. System generates 10-15 screening concepts by perturbing the BYO profile
2. Respondent rates each concept as "Like" or "Dislike"
3. System estimates initial utilities for each attribute level

**Algorithm**: BYO Perturbation Algorithm
```python
def generate_screening_matrix(byo: Dict[str, List[Any]], n_tasks: int = 10):
    """
    Generate screening concepts by perturbing the BYO profile.
    
    Algorithm:
    1. Start from BYO profile (ideal product)
    2. Generate concepts by changing 1-2 attributes from BYO
    3. Ensure every level appears at least once for testing acceptability
    4. Generate 10-15 concepts (default: 10)
    """
```

**Key Features**:
- **Perturbation Strategy**: Changes 1-2 attributes from the BYO profile
- **Level Coverage**: Ensures every attribute level is tested at least once
- **Acceptability Testing**: Identifies which levels are acceptable vs. unacceptable
- **Utility Estimation**: Calculates initial preference scores for each level

### Phase 3: Tournament Choices

**Purpose**: Refine preference estimates through adaptive choice tasks

**Process**:
1. System generates D-optimal choice sets from acceptable levels
2. Respondent makes pairwise or multiple-choice selections
3. System updates utilities adaptively after each choice
4. Process continues until sufficient precision is achieved

**Algorithm**: D-Optimal Design with Adaptive Updates
```python
def generate_tournament_set(previous_utilities, byo, task_number, n_options=3):
    """
    Generate tournament concepts using D-optimal design with filtered design space.
    
    Algorithm:
    1. Filter design space based on screening utilities
    2. Generate D-optimal choice sets
    3. Use coordinate exchange algorithm for optimization
    4. Return concepts with IDs for choice tasks
    """
```

---

## Algorithm Details

### 1. Utility Estimation Algorithm

**Purpose**: Convert screening responses into numerical preference scores

**Implementation**:
```python
def estimate_initial_utilities(responses: List[bool], tasks: List[Dict[str, Any]]):
    """
    Estimate utilities based on screening responses.
    
    Algorithm:
    1. Tally accept/reject counts by attribute-level
    2. Infer acceptable and unacceptable levels
    3. Return utilities for acceptable levels only
    """
```

**Utility Calculation Rules**:
- **Acceptable Levels**: Utility = acceptance_rate (accepted / total_appearances)
- **Unacceptable Levels**: Utility = 0.0 (if rejected in 2+ concepts)
- **Uncertain Levels**: Utility = 0.1 (if only 1 rejection)

### 2. Design Space Filtering

**Purpose**: Reduce the design space to only acceptable levels for tournament phase

**Implementation**:
```python
def filter_design_space_for_tournament(utilities, byo):
    """
    Filter the design space for the tournament based on screening utilities.
    
    Returns: Filtered BYO configuration with only acceptable levels
    """
```

**Filtering Rules**:
- Include levels with utility > 0 (acceptable levels)
- Fallback to all levels if no levels are acceptable
- Maintain statistical balance in the filtered design space

### 3. D-Optimal Design Generation

**Purpose**: Create statistically efficient choice sets for parameter estimation

**Implementation**:
```python
def generate_choice_sets(profiles, n_options=3, n_sets=1):
    """
    Generate D-optimal choice sets using coordinate exchange algorithm.
    
    Algorithm:
    1. Create design matrix using effects coding
    2. Calculate D-optimality criterion: det(X'X)
    3. Use coordinate exchange to optimize choice sets
    4. Return optimal choice sets
    """
```

**D-Optimality Criterion**:
- **Objective**: Maximize det(X'X) where X is the design matrix
- **Benefits**: Minimizes parameter estimation variance
- **Implementation**: Uses numpy for efficient matrix operations

### 4. Adaptive Utility Updates

**Purpose**: Continuously refine preference estimates based on choice behavior

**Implementation**:
```python
def adaptive_update(current_utils, choice):
    """
    Update utilities based on the chosen concept in tournament.
    
    Algorithm:
    1. Increase utility for chosen levels (+0.1)
    2. Decrease utilities for unchosen levels (-0.05)
    3. Ensure utilities remain non-negative
    """
```

**Update Rules**:
- **Chosen Levels**: +0.1 utility increase
- **Unchosen Levels**: -0.05 utility decrease (minimum 0.0)
- **Adaptive Learning**: Preferences become more precise with each choice

---

## Qualtrics Integration

### Survey Flow Architecture

```
Qualtrics Survey Flow:
├── BYO Configuration Block
│   ├── Attribute Selection Questions
│   └── BYO Profile Creation
├── API Integration Block
│   ├── BYO Config API Call
│   ├── Screening Design API Call
│   └── Tournament Choice API Calls
├── Screening Tasks Block
│   ├── Concept Rating Questions
│   └── Response Collection
├── Tournament Tasks Block
│   ├── Choice Set Questions
│   └── Choice Response Collection
└── Results Block
    ├── Preference Analysis
    └── Results Display
```

### API Integration Points

#### 1. BYO Configuration Integration

**Qualtrics Setup**:
```javascript
// Qualtrics JavaScript for BYO configuration
Qualtrics.SurveyEngine.addOnload(function() {
    // Collect BYO selections
    var byoConfig = {
        "brand": getSelectedValue("brand"),
        "price": getSelectedValue("price"),
        "features": getSelectedValue("features")
    };
    
    // Store for API call
    Qualtrics.SurveyEngine.setEmbeddedData("byoConfig", JSON.stringify(byoConfig));
});
```

**API Call**:
```javascript
// API integration for BYO configuration
async function configureBYO(byoConfig) {
    const response = await fetch('/api/byo-config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            session_id: getSessionId(),
            selected_attributes: byoConfig
        })
    });
    return response.json();
}
```

#### 2. Screening Design Integration

**API Call**:
```javascript
// Get screening design from API
async function getScreeningDesign(sessionId) {
    const response = await fetch(`/api/screening/design?session_id=${sessionId}`);
    const screeningTasks = await response.json();
    
    // Generate Qualtrics questions dynamically
    generateScreeningQuestions(screeningTasks);
}
```

**Qualtrics Question Generation**:
```javascript
function generateScreeningQuestions(tasks) {
    tasks.forEach((task, index) => {
        // Create concept display
        const conceptHtml = generateConceptDisplay(task.concept);
        
        // Create rating question
        const questionId = `screening_${index + 1}`;
        createRatingQuestion(questionId, conceptHtml);
    });
}
```

#### 3. Tournament Choice Integration

**API Call**:
```javascript
// Get tournament choice task
async function getTournamentChoice(sessionId, taskNumber) {
    const response = await fetch(
        `/api/tournament/choice?session_id=${sessionId}&task_number=${taskNumber}`
    );
    const choiceTask = await response.json();
    
    // Generate choice set question
    generateChoiceSetQuestion(choiceTask);
}
```

**Choice Response Submission**:
```javascript
// Submit choice response
async function submitChoiceResponse(sessionId, taskNumber, selectedConceptId) {
    const response = await fetch('/api/tournament/choice-response', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            session_id: sessionId,
            task_number: taskNumber,
            selected_concept_id: selectedConceptId
        })
    });
    
    const result = await response.json();
    return result.next_task;
}
```

### Qualtrics Survey Structure

#### Block 1: BYO Configuration
```
Question 1: Brand Preference
- Nike
- Adidas
- Puma

Question 2: Price Range
- $50-100
- $100-150
- $150-200

Question 3: Features
- Basic
- Advanced
- Premium
```

#### Block 2: Screening Tasks
```
Question 1: Concept Rating
[Display Concept 1]
- Like
- Dislike

Question 2: Concept Rating
[Display Concept 2]
- Like
- Dislike

... (10-15 concepts total)
```

#### Block 3: Tournament Tasks
```
Question 1: Choice Set
[Display 3 concepts]
- Concept A
- Concept B
- Concept C

Question 2: Choice Set
[Display 3 concepts]
- Concept A
- Concept B
- Concept C

... (10-20 tasks total)
```

### JavaScript Integration Code

```javascript
// Complete Qualtrics integration example
Qualtrics.SurveyEngine.addOnload(function() {
    const sessionId = generateSessionId();
    Qualtrics.SurveyEngine.setEmbeddedData("sessionId", sessionId);
    
    // Initialize API integration
    initializeACBC(sessionId);
});

async function initializeACBC(sessionId) {
    try {
        // Step 1: Configure BYO
        const byoConfig = collectBYOConfig();
        const byoResult = await configureBYO(byoConfig);
        
        // Step 2: Get screening design
        const screeningDesign = await getScreeningDesign(sessionId);
        generateScreeningBlock(screeningDesign);
        
        // Step 3: Initialize tournament
        initializeTournament(sessionId);
        
    } catch (error) {
        console.error('ACBC initialization failed:', error);
    }
}

function generateScreeningBlock(screeningTasks) {
    screeningTasks.forEach((task, index) => {
        const questionId = `screening_${index + 1}`;
        const conceptHtml = generateConceptDisplay(task.concept);
        
        // Create Qualtrics question
        createRatingQuestion(questionId, conceptHtml, "Like", "Dislike");
    });
}

async function initializeTournament(sessionId) {
    let currentTask = 1;
    
    while (currentTask <= 20) { // Maximum 20 tasks
        try {
            const choiceTask = await getTournamentChoice(sessionId, currentTask);
            generateChoiceSetQuestion(choiceTask);
            currentTask++;
        } catch (error) {
            console.error('Tournament task failed:', error);
            break;
        }
    }
}
```

---

## Statistical Foundations

### 1. Effects Coding

**Purpose**: Create statistically valid design matrices for parameter estimation

**Implementation**:
```python
def create_design_matrix(profiles):
    """
    Create a design matrix from profiles using effects coding.
    
    Effects Coding Rules:
    - For n levels, create n-1 variables
    - Reference level gets -1 for all variables
    - Each level gets 1 for its variable, 0 for others
    """
```

**Example**:
```
Attribute: Brand (3 levels)
Levels: Nike, Adidas, Puma

Effects Coding:
- Nike: [1, 0]
- Adidas: [0, 1]  
- Puma: [-1, -1] (reference level)
```

### 2. D-Optimality Criterion

**Purpose**: Maximize statistical efficiency of choice sets

**Formula**: D = det(X'X)

**Benefits**:
- Minimizes parameter estimation variance
- Ensures efficient information gain
- Optimizes statistical power

### 3. Utility Theory Foundation

**Assumption**: Respondents choose options that maximize utility

**Utility Function**: U = Σ(βᵢ × Xᵢ) + ε

Where:
- U = Total utility
- βᵢ = Parameter for attribute i
- Xᵢ = Attribute level value
- ε = Random error term

---

## Implementation Details

### 1. Numpy-Powered Algorithms

**Benefits**:
- **Efficient Matrix Operations**: Fast design matrix calculations
- **Statistical Functions**: Built-in linear algebra and optimization
- **Memory Efficiency**: Optimized for large datasets
- **Numerical Stability**: Robust handling of edge cases

**Key Functions**:
```python
import numpy as np

# Design matrix creation
X = np.array(design_matrix)

# D-optimality calculation
XtX = X.T @ X
d_optimality = np.linalg.det(XtX)

# Utility updates
utilities = np.array(utility_values)
updated_utilities = utilities + learning_rate * choice_vector
```

### 2. Adaptive Learning Parameters

**Learning Rate**: 0.1 for utility increases, 0.05 for decreases

**Convergence Criteria**:
- Maximum 20 tournament tasks
- Minimum 10 screening tasks
- Utility stability threshold

### 3. Error Handling

**Robust Implementation**:
- Graceful handling of edge cases
- Fallback algorithms for insufficient data
- Comprehensive error logging
- Automatic recovery mechanisms

---

## Best Practices

### 1. Survey Design

**Attribute Selection**:
- 3-5 attributes per study
- 2-5 levels per attribute
- Avoid highly correlated attributes
- Include price as an attribute when relevant

**Sample Size**:
- Minimum 100 respondents per segment
- 200+ respondents for reliable results
- Consider power analysis for specific objectives

### 2. Implementation Guidelines

**Qualtrics Setup**:
- Use embedded data for session management
- Implement proper error handling
- Test survey flow thoroughly
- Monitor completion rates

**API Integration**:
- Implement retry logic for API calls
- Cache responses when appropriate
- Monitor API performance
- Handle network failures gracefully

### 3. Data Quality

**Validation Checks**:
- Screen for straight-lining responses
- Check for logical inconsistencies
- Monitor completion times
- Validate utility estimates

---

## Example Workflow

### Smartphone Study Example

**Attributes and Levels**:
```
Brand: Apple, Samsung, Google
Price: $500, $800, $1200
Storage: 64GB, 128GB, 256GB
Camera: Dual, Triple, Quad
```

**Phase 1: BYO Configuration**
```
Respondent selects:
- Brand: Apple
- Price: $800
- Storage: 128GB
- Camera: Triple
```

**Phase 2: Screening Tasks**
```
Concept 1: Apple, $800, 128GB, Triple (BYO profile)
Concept 2: Apple, $500, 128GB, Triple (price change)
Concept 3: Samsung, $800, 128GB, Triple (brand change)
...
```

**Phase 3: Tournament Tasks**
```
Task 1: Choose from 3 concepts
- Concept A: Apple, $800, 128GB, Triple
- Concept B: Apple, $800, 256GB, Triple  
- Concept C: Samsung, $800, 128GB, Dual

Task 2: Choose from 3 concepts
- Concept A: Apple, $500, 128GB, Triple
- Concept B: Apple, $800, 128GB, Quad
- Concept C: Google, $800, 256GB, Triple
...
```

### Results Analysis

**Utility Estimates**:
```
Brand:
- Apple: 0.85
- Samsung: 0.45
- Google: 0.30

Price:
- $500: 0.90
- $800: 0.60
- $1200: 0.20

Storage:
- 64GB: 0.30
- 128GB: 0.70
- 256GB: 0.80

Camera:
- Dual: 0.40
- Triple: 0.75
- Quad: 0.85
```

**Market Simulation**:
- Product optimization
- Market share prediction
- Price sensitivity analysis
- Segment analysis

---

## Conclusion

Our ACBC methodology provides a sophisticated, adaptive approach to conjoint analysis that maximizes respondent engagement while ensuring statistical rigor. The integration with Qualtrics enables seamless implementation in real-world market research studies, while the numpy-powered algorithms ensure efficient and reliable results.

**Key Success Factors**:
- Robust algorithmic implementation
- Seamless Qualtrics integration
- Comprehensive error handling
- Statistical efficiency optimization
- Adaptive learning capabilities

This methodology is particularly well-suited for:
- Product development and optimization
- Pricing strategy development
- Market segmentation studies
- Competitive positioning analysis
- Customer preference research

For implementation support or technical questions, refer to the API documentation and Qualtrics integration guides. 
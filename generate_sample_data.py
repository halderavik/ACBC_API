#!/usr/bin/env python3
"""
Generate comprehensive sample data for ACBC smartphone study
Tests all dashboard components with realistic data
"""

import asyncio
import asyncpg
import json
import random
from datetime import datetime, timedelta
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:Password123!@localhost:5432/conjoint")

# Smartphone attributes and levels
ATTRIBUTES = {
    "brand": ["Apple", "Samsung", "Google", "OnePlus", "Xiaomi"],
    "price": ["$499", "$699", "$899", "$1099"],
    "screen_size": ["5.8\"", "6.1\"", "6.4\"", "6.7\""],
    "battery_life": ["Up to 12 hrs", "Up to 18 hrs", "Up to 24 hrs"],
    "camera_quality": ["Dual Lens (12MP)", "Triple Lens (48MP)", "Quad Lens (108MP)"],
    "storage_capacity": ["64 GB", "128 GB", "256 GB", "512 GB"],
    "5g_support": ["No", "Yes"],
    "wireless_charging": ["No", "Yes"],
    "water_resistance": ["No", "IP67 (1m)", "IP68 (1.5m)"],
    "operating_system": ["iOS", "Android"]
}

# Realistic BYO configurations (Build Your Own)
BYO_CONFIGS = [
    {
        "brand": ["Apple", "Samsung"],
        "price": ["$699", "$899", "$1099"],
        "screen_size": ["6.1\"", "6.4\"", "6.7\""],
        "battery_life": ["Up to 18 hrs", "Up to 24 hrs"],
        "camera_quality": ["Triple Lens (48MP)", "Quad Lens (108MP)"],
        "storage_capacity": ["128 GB", "256 GB", "512 GB"],
        "5g_support": ["Yes"],
        "wireless_charging": ["Yes"],
        "water_resistance": ["IP67 (1m)", "IP68 (1.5m)"],
        "operating_system": ["iOS", "Android"]
    },
    {
        "brand": ["Google", "OnePlus", "Xiaomi"],
        "price": ["$499", "$699", "$899"],
        "screen_size": ["5.8\"", "6.1\"", "6.4\""],
        "battery_life": ["Up to 12 hrs", "Up to 18 hrs"],
        "camera_quality": ["Dual Lens (12MP)", "Triple Lens (48MP)"],
        "storage_capacity": ["64 GB", "128 GB", "256 GB"],
        "5g_support": ["No", "Yes"],
        "wireless_charging": ["No", "Yes"],
        "water_resistance": ["No", "IP67 (1m)"],
        "operating_system": ["Android"]
    }
]

def generate_concept():
    """Generate a random smartphone concept."""
    return {
        "brand": random.choice(ATTRIBUTES["brand"]),
        "price": random.choice(ATTRIBUTES["price"]),
        "screen_size": random.choice(ATTRIBUTES["screen_size"]),
        "battery_life": random.choice(ATTRIBUTES["battery_life"]),
        "camera_quality": random.choice(ATTRIBUTES["camera_quality"]),
        "storage_capacity": random.choice(ATTRIBUTES["storage_capacity"]),
        "5g_support": random.choice(ATTRIBUTES["5g_support"]),
        "wireless_charging": random.choice(ATTRIBUTES["wireless_charging"]),
        "water_resistance": random.choice(ATTRIBUTES["water_resistance"]),
        "operating_system": random.choice(ATTRIBUTES["operating_system"])
    }

def generate_byo_config():
    """Generate a random BYO configuration."""
    return random.choice(BYO_CONFIGS)

def generate_utilities():
    """Generate realistic utility values for attributes."""
    utilities = {}
    for attr, levels in ATTRIBUTES.items():
        utilities[attr] = {}
        # Generate base utilities with some realistic preferences
        base_utilities = []
        for i, level in enumerate(levels):
            if attr == "brand":
                # Apple and Samsung preferred
                if level in ["Apple", "Samsung"]:
                    base_utilities.append(random.uniform(0.3, 0.8))
                else:
                    base_utilities.append(random.uniform(-0.2, 0.4))
            elif attr == "price":
                # Lower prices preferred
                price_val = int(level.replace("$", ""))
                base_utilities.append(random.uniform(-0.1, 0.3) - (price_val - 499) / 1000)
            elif attr == "battery_life":
                # Higher battery life preferred
                if "24" in level:
                    base_utilities.append(random.uniform(0.4, 0.8))
                elif "18" in level:
                    base_utilities.append(random.uniform(0.2, 0.6))
                else:
                    base_utilities.append(random.uniform(-0.2, 0.3))
            elif attr == "camera_quality":
                # Higher MP preferred
                if "108MP" in level:
                    base_utilities.append(random.uniform(0.3, 0.7))
                elif "48MP" in level:
                    base_utilities.append(random.uniform(0.1, 0.5))
                else:
                    base_utilities.append(random.uniform(-0.1, 0.3))
            elif attr == "storage_capacity":
                # More storage preferred
                storage_val = int(level.split()[0])
                base_utilities.append(random.uniform(-0.1, 0.3) + (storage_val - 64) / 1000)
            elif attr in ["5g_support", "wireless_charging"]:
                # Yes preferred
                if level == "Yes":
                    base_utilities.append(random.uniform(0.2, 0.6))
                else:
                    base_utilities.append(random.uniform(-0.3, 0.1))
            elif attr == "water_resistance":
                # Higher protection preferred
                if "IP68" in level:
                    base_utilities.append(random.uniform(0.3, 0.7))
                elif "IP67" in level:
                    base_utilities.append(random.uniform(0.1, 0.5))
                else:
                    base_utilities.append(random.uniform(-0.2, 0.2))
            elif attr == "operating_system":
                # Slight preference for iOS
                if level == "iOS":
                    base_utilities.append(random.uniform(0.1, 0.5))
                else:
                    base_utilities.append(random.uniform(-0.1, 0.3))
            else:
                # Random utilities for other attributes
                base_utilities.append(random.uniform(-0.2, 0.4))
        
        # Normalize utilities (sum to 0)
        mean_utility = sum(base_utilities) / len(base_utilities)
        utilities[attr] = {level: round(util - mean_utility, 3) for level, util in zip(levels, base_utilities)}
    
    return utilities

async def generate_sample_data():
    """Generate comprehensive sample data for testing."""
    # Connect to database
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        # Clear existing data
        await conn.execute("DELETE FROM tournament_tasks")
        await conn.execute("DELETE FROM screening_tasks")
        await conn.execute("DELETE FROM sessions")
        
        print("🗑️  Cleared existing data")
        
        # Generate 10 sessions with realistic data
        for session_id in range(1, 11):
            print(f"\n📱 Generating data for Respondent {session_id}...")
            
            # Generate BYO config and utilities
            byo_config = generate_byo_config()
            utilities = generate_utilities()
            
            # Create session
            await conn.execute("""
                INSERT INTO sessions (id, byo_config, utilities)
                VALUES ($1, $2, $3)
            """, session_id, json.dumps(byo_config), json.dumps(utilities))
            
            # Generate screening tasks (8 tasks per respondent)
            screening_concepts = []
            for i in range(8):
                concept = generate_concept()
                screening_concepts.append(concept)
                
                # Realistic screening responses (70% pass rate)
                response = random.choices(
                    ["accept", "reject"], 
                    weights=[0.7, 0.3]
                )[0] if random.random() < 0.9 else None  # 10% missing responses
                
                await conn.execute("""
                    INSERT INTO screening_tasks (session_id, concept, position, response)
                    VALUES ($1, $2, $3, $4)
                """, session_id, json.dumps(concept), i + 1, response)
            
            # Generate tournament tasks (12 tasks per respondent)
            for task_num in range(1, 13):
                # Generate 3 concepts for each tournament task
                concepts = []
                for _ in range(3):
                    concept = generate_concept()
                    concepts.append(concept)
                
                # Realistic choice based on utilities (with some randomness)
                if random.random() < 0.85:  # 85% completion rate
                    # Calculate utility for each concept
                    concept_utilities = []
                    for concept in concepts:
                        total_utility = 0
                        for attr, level in concept.items():
                            if attr in utilities and level in utilities[attr]:
                                total_utility += utilities[attr][level]
                        concept_utilities.append(total_utility)
                    
                    # Choose concept with highest utility (with some randomness)
                    max_utility = max(concept_utilities)
                    best_concepts = [i for i, util in enumerate(concept_utilities) if util >= max_utility - 0.1]
                    choice = random.choice(best_concepts) + 1  # 1-indexed
                else:
                    choice = None  # Missing choice
                
                await conn.execute("""
                    INSERT INTO tournament_tasks (session_id, task_number, concepts, choice)
                    VALUES ($1, $2, $3, $4)
                """, session_id, task_num, json.dumps(concepts), choice)
            
            print(f"   ✅ Generated {len(screening_concepts)} screening concepts, 12 tournament tasks")
        
        # Get summary statistics
        total_sessions = await conn.fetchval("SELECT COUNT(*) FROM sessions")
        total_screening = await conn.fetchval("SELECT COUNT(*) FROM screening_tasks")
        total_tournament = await conn.fetchval("SELECT COUNT(*) FROM tournament_tasks")
        screening_responses = await conn.fetchval("SELECT COUNT(*) FROM screening_tasks WHERE response IS NOT NULL")
        tournament_choices = await conn.fetchval("SELECT COUNT(*) FROM tournament_tasks WHERE choice IS NOT NULL")
        
        print(f"\n📊 Data Generation Complete!")
        print(f"   Sessions: {total_sessions}")
        print(f"   Screening Tasks: {total_screening} (Responses: {screening_responses})")
        print(f"   Tournament Tasks: {total_tournament} (Choices: {tournament_choices})")
        print(f"   Completion Rate: {round(tournament_choices/total_tournament*100, 1)}%")
        
        # Show some sample data
        print(f"\n🔍 Sample Data Preview:")
        
        # Sample session
        sample_session = await conn.fetchrow("""
            SELECT id, byo_config::text, utilities::text 
            FROM sessions 
            ORDER BY id 
            LIMIT 1
        """)
        print(f"   Session {sample_session['id']}:")
        print(f"     BYO Config: {sample_session['byo_config'][:100]}...")
        print(f"     Utilities: {sample_session['utilities'][:100]}...")
        
        # Sample screening task
        sample_screening = await conn.fetchrow("""
            SELECT concept::text, response 
            FROM screening_tasks 
            WHERE response IS NOT NULL 
            LIMIT 1
        """)
        print(f"   Sample Screening: {sample_screening['concept'][:80]}... → {sample_screening['response']}")
        
        # Sample tournament task
        sample_tournament = await conn.fetchrow("""
            SELECT concepts::text, choice 
            FROM tournament_tasks 
            WHERE choice IS NOT NULL 
            LIMIT 1
        """)
        print(f"   Sample Tournament: {sample_tournament['concepts'][:80]}... → Choice {sample_tournament['choice']}")
        
        print(f"\n🚀 Ready to test dashboard! Run:")
        print(f"   cd data_analysis_dashboard")
        print(f"   uvicorn app:asgi_app --host 0.0.0.0 --port 5001")
        print(f"   Then visit: http://localhost:5001")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(generate_sample_data()) 
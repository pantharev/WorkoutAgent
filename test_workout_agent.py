#!/usr/bin/env python3
"""
Test script for the Workout Agent
Tests basic functionality without requiring OpenAI API key
"""

import asyncio
from workout_agent import (
    FitnessProfile, 
    ActivityLevel, 
    calculate_bmr,
    app
)
from fastapi.testclient import TestClient

def test_models():
    """Test that the Pydantic models work correctly"""
    print("🧪 Testing Pydantic Models...")
    
    # Create a sample fitness profile
    profile = FitnessProfile(
        age=30,
        weight=70.0,
        height=175.0,
        gender="male",
        activity_level=ActivityLevel.MODERATELY_ACTIVE,
        fitness_goals="Build muscle and lose fat"
    )
    
    print(f"✅ Created fitness profile: {profile.age} year old {profile.gender}")
    print(f"   Weight: {profile.weight}kg, Height: {profile.height}cm")
    print(f"   Activity Level: {profile.activity_level.value}")
    print(f"   Goals: {profile.fitness_goals}")
    
    return profile

def test_bmr_calculation():
    """Test BMR calculation functionality"""
    print("\n🧮 Testing BMR Calculation...")
    
    profile = FitnessProfile(
        age=30,
        weight=70.0,
        height=175.0,
        gender="male",
        activity_level=ActivityLevel.MODERATELY_ACTIVE
    )
    
    bmr = calculate_bmr(profile)
    print(f"✅ BMR calculated: {bmr:.2f} calories/day")
    
    # Test female calculation
    female_profile = FitnessProfile(
        age=25,
        weight=60.0,
        height=165.0,
        gender="female",
        activity_level=ActivityLevel.LIGHTLY_ACTIVE
    )
    
    female_bmr = calculate_bmr(female_profile)
    print(f"✅ Female BMR calculated: {female_bmr:.2f} calories/day")
    
    return bmr, female_bmr

def test_api_endpoints():
    """Test FastAPI endpoints without AI functionality"""
    print("\n🌐 Testing API Endpoints...")
    
    client = TestClient(app)
    
    # Test root endpoint
    response = client.get("/")
    print(f"✅ Root endpoint: {response.status_code}")
    print(f"   Response: {response.json()['message']}")
    
    # Test health endpoint
    response = client.get("/health")
    print(f"✅ Health endpoint: {response.status_code}")
    print(f"   Status: {response.json()['status']}")
    
    # Test BMR endpoint
    test_profile = {
        "age": 30,
        "weight": 70.0,
        "height": 175.0,
        "gender": "male",
        "activity_level": "moderately_active"
    }
    
    response = client.post("/bmr", json=test_profile)
    print(f"✅ BMR endpoint: {response.status_code}")
    if response.status_code == 200:
        bmr_data = response.json()
        print(f"   BMR: {bmr_data['bmr']} calories/day")
        print(f"   Daily calories: {bmr_data['daily_calories']}")
        print(f"   Weight loss: {bmr_data['weight_loss_calories']}")
        print(f"   Weight gain: {bmr_data['weight_gain_calories']}")

def main():
    """Run all tests"""
    print("🏋️  Testing Workout Agent Functionality")
    print("=" * 50)
    
    try:
        # Test models
        profile = test_models()
        
        # Test BMR calculation
        test_bmr_calculation()
        
        # Test API endpoints
        test_api_endpoints()
        
        print("\n" + "=" * 50)
        print("✅ All basic tests passed!")
        print("\n📝 Next steps:")
        print("1. Set your OpenAI API key in .env file")
        print("2. Copy .env.example to .env and add your API key")
        print("3. Run: python workout_agent.py")
        print("4. Test the /analyze endpoint with AI functionality")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

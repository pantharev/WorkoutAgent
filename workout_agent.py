#!/usr/bin/env python3
"""
Holistic Workout Agent - A comprehensive fitness advisor application
Consolidates all fitness advisor functionality into a single file
"""

import os
import asyncio
from typing import List, Optional
from enum import Enum

# FastAPI imports
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Pydantic imports
from pydantic import BaseModel, Field

# Pydantic AI imports
from pydantic_ai import Agent, RunContext

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# =============================================================================
# ENUMS AND CONSTANTS
# =============================================================================

class ActivityLevel(str, Enum):
    SEDENTARY = "sedentary"
    LIGHTLY_ACTIVE = "lightly_active"
    MODERATELY_ACTIVE = "moderately_active"
    VERY_ACTIVE = "very_active"
    EXTREMELY_ACTIVE = "extremely_active"

# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class FitnessProfile(BaseModel):
    """User's fitness profile and personal information"""
    age: int = Field(..., description="Age in years", ge=13, le=120)
    weight: float = Field(..., description="Weight in kg", gt=0)
    height: float = Field(..., description="Height in cm", gt=0)
    gender: str = Field(..., description="Gender (male/female/other)")
    activity_level: ActivityLevel = Field(..., description="Current activity level")
    fitness_goals: Optional[str] = Field(None, description="Specific fitness goals")

class Exercise(BaseModel):
    """Individual exercise in a workout plan"""
    name: str = Field(..., description="Name of the exercise")
    sets: int = Field(..., description="Number of sets", ge=1)
    reps: int = Field(..., description="Number of repetitions per set", ge=1)
    rest_time: int = Field(..., description="Rest time in seconds between sets", ge=0)
    instructions: Optional[str] = Field(None, description="Exercise instructions")

class Meal(BaseModel):
    """Individual meal in a nutrition plan"""
    name: str = Field(..., description="Name of the meal")
    calories: int = Field(..., description="Calories per serving", ge=0)
    protein: float = Field(..., description="Protein in grams", ge=0)
    carbs: float = Field(..., description="Carbohydrates in grams", ge=0)
    fats: float = Field(..., description="Fats in grams", ge=0)
    timing: str = Field(..., description="Meal timing (breakfast, lunch, dinner, snack)")
    ingredients: Optional[List[str]] = Field(None, description="List of ingredients")

class FitnessReportResult(BaseModel):
    """Complete fitness report with workout and nutrition plans"""
    workout_plan: List[Exercise] = Field(..., description="Customized workout plan")
    nutrition_plan: List[Meal] = Field(..., description="Customized nutrition plan")
    daily_calories: int = Field(..., description="Recommended daily calories")
    motivational_quote: str = Field(..., description="Personalized motivational quote")
    recommendations: List[str] = Field(..., description="Additional fitness recommendations")

# =============================================================================
# AI AGENTS SETUP
# =============================================================================

# Global variables for agents (initialized lazily)
fitness_agent = None
motivational_agent = None

def get_fitness_agent():
    """Get or create the fitness agent (lazy initialization)"""
    global fitness_agent
    if fitness_agent is None:
        fitness_agent = Agent(
            'openai:gpt-4',
            deps_type=FitnessProfile,
            result_type=FitnessReportResult,
            result_retries=3,
            system_prompt="""
            You are an expert fitness and nutrition advisor. Create a comprehensive, personalized 
            FitnessReportResult based on the user's fitness profile. 
            
            Guidelines:
            - Create a balanced workout plan with 3-5 exercises
            - Include both strength and cardio exercises when appropriate
            - Design a nutrition plan with 3 main meals and 1-2 snacks
            - Calculate appropriate daily calories based on age, weight, height, gender, and activity level
            - Use the get_motivation tool to get motivational quotes and select the best one
            - Provide 3-5 practical recommendations
            - Consider the user's activity level and any specific fitness goals
            """
        )
        
        @fitness_agent.system_prompt
        async def add_user_fitness_data(ctx: RunContext[FitnessProfile]) -> str:
            """Add user's fitness profile data to the context"""
            fitness_data = ctx.deps
            return f"User fitness profile and goals: {fitness_data!r}"

        @fitness_agent.tool
        async def get_motivation(ctx: RunContext[FitnessProfile]) -> List[str]:
            """Get motivational quotes tailored to the user's fitness journey"""
            profile = ctx.deps
            prompt = f"""
            Generate 5 motivational quotes for someone who is:
            - {profile.age} years old
            - {profile.gender}
            - Currently {profile.activity_level.value.replace('_', ' ')}
            - Goals: {profile.fitness_goals or 'general fitness improvement'}
            
            Make the quotes personal, encouraging, and action-oriented.
            """
            
            motivational_agent = get_motivational_agent()
            result = await motivational_agent.run(prompt)
            return result.data
    
    return fitness_agent

def get_motivational_agent():
    """Get or create the motivational agent (lazy initialization)"""
    global motivational_agent
    if motivational_agent is None:
        motivational_agent = Agent(
            'openai:gpt-4',
            result_type=List[str],
            system_prompt="""
            Generate inspiring and motivational quotes specifically tailored to fitness, 
            health, and wellness. Focus on encouragement, perseverance, and positive mindset.
            Make quotes personal and actionable.
            """
        )
    return motivational_agent

# =============================================================================
# BUSINESS LOGIC
# =============================================================================

async def analyze_profile(profile: FitnessProfile) -> FitnessReportResult:
    """
    Analyze user's fitness profile and generate comprehensive fitness report
    
    Args:
        profile: User's fitness profile information
        
    Returns:
        FitnessReportResult: Complete fitness and nutrition plan
    """
    try:
        agent = get_fitness_agent()
        result = await agent.run(
            "Create a personalized fitness and nutrition plan based on the user's profile", 
            deps=profile
        )
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing profile: {str(e)}")

def calculate_bmr(profile: FitnessProfile) -> float:
    """Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation"""
    if profile.gender.lower() == 'male':
        bmr = 10 * profile.weight + 6.25 * profile.height - 5 * profile.age + 5
    else:
        bmr = 10 * profile.weight + 6.25 * profile.height - 5 * profile.age - 161
    
    # Activity multipliers
    activity_multipliers = {
        ActivityLevel.SEDENTARY: 1.2,
        ActivityLevel.LIGHTLY_ACTIVE: 1.375,
        ActivityLevel.MODERATELY_ACTIVE: 1.55,
        ActivityLevel.VERY_ACTIVE: 1.725,
        ActivityLevel.EXTREMELY_ACTIVE: 1.9
    }
    
    return bmr * activity_multipliers[profile.activity_level]

# =============================================================================
# FASTAPI APPLICATION
# =============================================================================

# Initialize FastAPI app
app = FastAPI(
    title="Workout Agent API",
    description="A comprehensive fitness advisor that provides personalized workout and nutrition plans",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# API ROUTES
# =============================================================================

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Workout Agent API",
        "version": "1.0.0",
        "endpoints": {
            "/analyze": "POST - Analyze fitness profile and get personalized plan",
            "/health": "GET - Health check endpoint",
            "/bmr": "POST - Calculate Basal Metabolic Rate"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "workout-agent"}

@app.post("/analyze", response_model=FitnessReportResult)
async def analyze_fitness(fitness_profile: FitnessProfile):
    """
    Analyze user's fitness profile and generate personalized workout and nutrition plan
    
    Args:
        fitness_profile: User's fitness information and goals
        
    Returns:
        FitnessReportResult: Comprehensive fitness report with workout plan, nutrition plan, and recommendations
    """
    try:
        result = await analyze_profile(fitness_profile)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/bmr")
async def calculate_bmr_endpoint(fitness_profile: FitnessProfile):
    """
    Calculate user's Basal Metabolic Rate and daily calorie needs
    
    Args:
        fitness_profile: User's basic fitness information
        
    Returns:
        BMR and daily calorie recommendations
    """
    try:
        bmr = calculate_bmr(fitness_profile)
        return {
            "bmr": round(bmr, 2),
            "daily_calories": round(bmr, 0),
            "weight_loss_calories": round(bmr - 500, 0),
            "weight_gain_calories": round(bmr + 500, 0),
            "activity_level": fitness_profile.activity_level.value
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating BMR: {str(e)}")

# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Main function to run the workout agent server"""
    try:
        print("🏋️  Starting Workout Agent Server...")
        print("📊 Fitness analysis powered by AI")
        print("🥗 Personalized nutrition planning")
        print("💪 Motivational coaching included")
    except UnicodeEncodeError:
        # Fallback for Windows console that doesn't support emojis
        print("Starting Workout Agent Server...")
        print("Fitness analysis powered by AI")
        print("Personalized nutrition planning")
        print("Motivational coaching included")
    
    print("-" * 50)
    
    # Check for required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        try:
            print("⚠️  Warning: OPENAI_API_KEY not found in environment variables")
        except UnicodeEncodeError:
            print("Warning: OPENAI_API_KEY not found in environment variables")
        print("   Please set your OpenAI API key in .env file or environment")
    
    # Run the server
    uvicorn.run(
        "workout_agent:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()

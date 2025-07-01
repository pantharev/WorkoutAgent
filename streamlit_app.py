#!/usr/bin/env python3
"""
Streamlit UI for Workout Agent with Embedded FastAPI Backend
A user-friendly interface for the AI-powered fitness advisor
"""

import streamlit as st
import asyncio
import os
import threading
import time
from typing import Dict, Any, List, Optional
from enum import Enum
import uvicorn
from contextlib import asynccontextmanager

# FastAPI imports
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Pydantic imports
from pydantic import BaseModel, Field

# Pydantic AI imports
from pydantic_ai import Agent, RunContext

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# =============================================================================
# PYDANTIC MODELS AND ENUMS
# =============================================================================

class ActivityLevel(str, Enum):
    SEDENTARY = "sedentary"
    LIGHTLY_ACTIVE = "lightly_active"
    MODERATELY_ACTIVE = "moderately_active"
    VERY_ACTIVE = "very_active"
    EXTREMELY_ACTIVE = "extremely_active"

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

def get_openai_api_key():
    """Get OpenAI API key from environment or Streamlit secrets"""
    # Try Streamlit secrets first (for cloud deployment)
    try:
        return st.secrets["OPENAI_API_KEY"]
    except:
        # Fall back to environment variable (for local development)
        return os.getenv("OPENAI_API_KEY")

def get_fitness_agent():
    """Get or create the fitness agent (lazy initialization)"""
    global fitness_agent
    if fitness_agent is None:
        api_key = get_openai_api_key()
        if not api_key:
            raise ValueError("OpenAI API key not found")
            
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
    """Analyze user's fitness profile and generate comprehensive fitness report"""
    try:
        agent = get_fitness_agent()
        result = await agent.run(
            "Create a personalized fitness and nutrition plan based on the user's profile", 
            deps=profile
        )
        return result.data
    except Exception as e:
        raise Exception(f"Error analyzing profile: {str(e)}")

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
# STREAMLIT UI CONFIGURATION
# =============================================================================

# Page configuration
st.set_page_config(
    page_title="🏋️ Workout Agent - AI Fitness Advisor",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #FF6B6B;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #4ECDC4;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #F0F8FF;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #4ECDC4;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #F0FFF0;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #32CD32;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #FFF0F0;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #FF6B6B;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Constants
ACTIVITY_LEVELS = {
    "Sedentary (little to no exercise)": "sedentary",
    "Lightly Active (light exercise 1-3 days/week)": "lightly_active",
    "Moderately Active (moderate exercise 3-5 days/week)": "moderately_active",
    "Very Active (hard exercise 6-7 days/week)": "very_active",
    "Extremely Active (very hard exercise, physical job)": "extremely_active"
}

# =============================================================================
# UI HELPER FUNCTIONS
# =============================================================================

def check_api_key() -> bool:
    """Check if OpenAI API key is available"""
    return get_openai_api_key() is not None

def display_workout_plan(workout_plan):
    """Display workout plan in a formatted way"""
    st.markdown('<div class="section-header">🏃 Your Personalized Workout Plan</div>', unsafe_allow_html=True)
    
    for i, exercise in enumerate(workout_plan, 1):
        with st.expander(f"Exercise {i}: {exercise.name}", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Sets", exercise.sets)
            with col2:
                st.metric("Reps", exercise.reps)
            with col3:
                st.metric("Rest Time", f"{exercise.rest_time}s")
            
            if exercise.instructions:
                st.markdown(f"**Instructions:** {exercise.instructions}")

def display_nutrition_plan(nutrition_plan):
    """Display nutrition plan in a formatted way"""
    st.markdown('<div class="section-header">🥗 Your Personalized Nutrition Plan</div>', unsafe_allow_html=True)
    
    # Group meals by timing
    meals_by_timing = {}
    for meal in nutrition_plan:
        timing = meal.timing.title()
        if timing not in meals_by_timing:
            meals_by_timing[timing] = []
        meals_by_timing[timing].append(meal)
    
    # Display meals by timing
    for timing, meals in meals_by_timing.items():
        st.markdown(f"### {timing}")
        for meal in meals:
            with st.expander(f"{meal.name} - {meal.calories} calories", expanded=False):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Calories", meal.calories)
                with col2:
                    st.metric("Protein", f"{meal.protein}g")
                with col3:
                    st.metric("Carbs", f"{meal.carbs}g")
                with col4:
                    st.metric("Fats", f"{meal.fats}g")
                
                if meal.ingredients:
                    st.markdown("**Ingredients:**")
                    for ingredient in meal.ingredients:
                        st.markdown(f"• {ingredient}")

# =============================================================================
# MAIN STREAMLIT APPLICATION
# =============================================================================

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<div class="main-header">🏋️ Workout Agent - AI Fitness Advisor</div>', unsafe_allow_html=True)
    st.markdown("Get personalized workout plans, nutrition guidance, and motivational coaching powered by AI!")
    
    # Check API key
    api_key_available = check_api_key()
    
    if not api_key_available:
        st.markdown("""
        <div class="error-box">
        ⚠️ <strong>OpenAI API Key Required</strong><br>
        Please set your OpenAI API key in the Streamlit secrets or environment variables to use AI features.
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        ### How to add your API key:
        
        **For Streamlit Cloud:**
        1. Go to your app dashboard
        2. Click "Settings" → "Secrets"
        3. Add: `OPENAI_API_KEY = "your_api_key_here"`
        
        **For local development:**
        1. Create a `.env` file
        2. Add: `OPENAI_API_KEY=your_api_key_here`
        """)
        
        # Still allow BMR calculations without API key
        st.markdown("---")
        st.markdown("### BMR Calculator (No API Key Required)")
    
    # Sidebar for user input
    with st.sidebar:
        st.header("📋 Your Fitness Profile")
        
        # Basic Information
        st.subheader("Basic Information")
        age = st.number_input("Age", min_value=13, max_value=120, value=30, help="Your age in years")
        weight = st.number_input("Weight (kg)", min_value=30.0, max_value=300.0, value=70.0, step=0.5, help="Your current weight in kilograms")
        height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=175.0, step=0.5, help="Your height in centimeters")
        
        gender = st.selectbox(
            "Gender",
            options=["male", "female", "other"],
            help="Select your gender for accurate BMR calculations"
        )
        
        # Activity Level
        st.subheader("Activity Level")
        activity_display = st.selectbox(
            "Current Activity Level",
            options=list(ACTIVITY_LEVELS.keys()),
            index=2,  # Default to "Moderately Active"
            help="Select your current activity level to get accurate calorie recommendations"
        )
        activity_level = ACTIVITY_LEVELS[activity_display]
        
        # Fitness Goals
        st.subheader("Fitness Goals")
        fitness_goals = st.text_area(
            "Specific Fitness Goals (Optional)",
            placeholder="e.g., Build muscle and lose fat, Train for a marathon, Improve overall health...",
            help="Describe your specific fitness goals to get more targeted recommendations"
        )
        
        # Action buttons
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            analyze_button = st.button("🤖 Get AI Analysis", type="primary", use_container_width=True, disabled=not api_key_available)
        
        with col2:
            bmr_button = st.button("📊 Calculate BMR", use_container_width=True)
    
    # Main content area
    if analyze_button and api_key_available:
        # Prepare data for analysis
        profile_data = FitnessProfile(
            age=age,
            weight=weight,
            height=height,
            gender=gender,
            activity_level=ActivityLevel(activity_level),
            fitness_goals=fitness_goals if fitness_goals.strip() else None
        )
        
        # Show loading spinner
        with st.spinner("🤖 AI is analyzing your profile and creating your personalized plan..."):
            try:
                result = asyncio.run(analyze_profile(profile_data))
                
                # Success message
                st.markdown("""
                <div class="success-box">
                ✅ <strong>Analysis Complete!</strong> Your personalized fitness plan is ready.
                </div>
                """, unsafe_allow_html=True)
                
                # Display results in tabs
                tab1, tab2, tab3, tab4 = st.tabs(["🏃 Workout Plan", "🥗 Nutrition Plan", "💪 Motivation", "📊 Summary"])
                
                with tab1:
                    display_workout_plan(result.workout_plan)
                
                with tab2:
                    display_nutrition_plan(result.nutrition_plan)
                
                with tab3:
                    st.markdown('<div class="section-header">💪 Your Motivational Quote</div>', unsafe_allow_html=True)
                    st.markdown(f"""
                    <div class="info-box">
                    <h3>"{result.motivational_quote}"</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown('<div class="section-header">📝 Recommendations</div>', unsafe_allow_html=True)
                    for i, recommendation in enumerate(result.recommendations, 1):
                        st.markdown(f"**{i}.** {recommendation}")
                
                with tab4:
                    st.markdown('<div class="section-header">📊 Summary</div>', unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Daily Calories", f"{result.daily_calories:,}")
                    with col2:
                        st.metric("Workout Exercises", len(result.workout_plan))
                    with col3:
                        st.metric("Meal Plans", len(result.nutrition_plan))
                    
                    # Profile summary
                    st.markdown("### Your Profile")
                    st.json({
                        "Age": age,
                        "Weight": f"{weight} kg",
                        "Height": f"{height} cm",
                        "Gender": gender.title(),
                        "Activity Level": activity_display,
                        "Goals": fitness_goals if fitness_goals.strip() else "General fitness improvement"
                    })
                    
            except Exception as e:
                st.markdown(f"""
                <div class="error-box">
                ❌ <strong>Error:</strong> {str(e)}
                </div>
                """, unsafe_allow_html=True)
    
    elif bmr_button:
        # Prepare data for BMR calculation
        profile_data = FitnessProfile(
            age=age,
            weight=weight,
            height=height,
            gender=gender,
            activity_level=ActivityLevel(activity_level)
        )
        
        with st.spinner("📊 Calculating your BMR..."):
            try:
                bmr = calculate_bmr(profile_data)
                
                st.markdown('<div class="section-header">📊 Your BMR Results</div>', unsafe_allow_html=True)
                
                # Display BMR results
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("BMR", f"{bmr:.0f} cal/day", help="Basal Metabolic Rate - calories burned at rest")
                with col2:
                    st.metric("Maintenance", f"{bmr:.0f} cal/day", help="Calories to maintain current weight")
                with col3:
                    st.metric("Weight Loss", f"{bmr - 500:.0f} cal/day", help="Calories for gradual weight loss")
                with col4:
                    st.metric("Weight Gain", f"{bmr + 500:.0f} cal/day", help="Calories for gradual weight gain")
                
                # BMR explanation
                st.markdown("""
                <div class="info-box">
                <strong>Understanding Your BMR:</strong><br>
                • <strong>BMR</strong>: The calories your body burns at complete rest<br>
                • <strong>Maintenance</strong>: Calories needed to maintain your current weight with your activity level<br>
                • <strong>Weight Loss</strong>: 500 calories below maintenance for ~1 lb/week loss<br>
                • <strong>Weight Gain</strong>: 500 calories above maintenance for ~1 lb/week gain
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.markdown(f"""
                <div class="error-box">
                ❌ <strong>Error:</strong> {str(e)}
                </div>
                """, unsafe_allow_html=True)
    
    # Instructions and tips
    if not analyze_button and not bmr_button:
        st.markdown('<div class="section-header">🚀 How to Get Started</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="info-box">
            <h4>📋 Fill Your Profile</h4>
            1. Enter your basic information (age, weight, height, gender)<br>
            2. Select your current activity level<br>
            3. Optionally describe your fitness goals<br>
            4. Click "Get AI Analysis" for a complete plan
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="info-box">
            <h4>🎯 What You'll Get</h4>
            • Personalized workout plan with exercises<br>
            • Custom nutrition plan with meals<br>
            • Motivational quotes and tips<br>
            • BMR and calorie recommendations
            </div>
            """, unsafe_allow_html=True)
        
        # Tips for best results
        st.markdown('<div class="section-header">💡 Tips for Best Results</div>', unsafe_allow_html=True)
        
        tips_col1, tips_col2 = st.columns(2)
        
        with tips_col1:
            st.markdown("""
            **🎯 Be Specific with Goals:**
            - "Build muscle and lose fat"
            - "Train for a 5K race"
            - "Improve flexibility and strength"
            - "Prepare for hiking season"
            """)
        
        with tips_col2:
            st.markdown("""
            **📊 Accurate Measurements:**
            - Use your current weight
            - Measure height without shoes
            - Be honest about activity level
            - Update profile as you progress
            """)

if __name__ == "__main__":
    main()

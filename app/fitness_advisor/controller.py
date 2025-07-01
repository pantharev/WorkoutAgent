from fastapi import APIRouter
from app.fitness_advisor.models import FitnessProfile
from app.fitness_advisor.service import analyze_profile


router = APIRouter()

@router.post("/anaylze")
async def analyze_fitness(fitness_profile: FitnessProfile)
    return await analyze_profile(fitness_profile)


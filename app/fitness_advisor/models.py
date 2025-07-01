class FitnessProfile(BaseModel):
    age: int
    weight: float
    height: float
    gender: str
    activity_level: ActivityLevel

class FitnessReportResult(BaseModel):


class Excercise(BaseModel):
    name: str
    sets: int
    reps: int
    rest_time: int = Field(..., description="Rest time in seconds")

class Meal(BaseModel):
    name: str
    calories: int
    protein: float
    carbs: float
    fats: float
    timing: str = Field(..., description="breakfast, lunch, dinner, snack")

class FitnessReportResult(BaseModel):
    workout_plan: list[Excercise] = Field(description="Customized workout plan")
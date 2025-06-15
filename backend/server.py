from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models for Enhanced Broiler Chicken Calculator
class FeedPhase(BaseModel):
    consumption_kg: float
    cost_per_kg: float

class RemovalBatch(BaseModel):
    quantity: int
    total_weight_kg: float
    age_days: int

class BroilerCalculationInput(BaseModel):
    initial_chicks: int
    chick_cost_per_unit: float
    
    # Feed phases
    pre_starter_feed: FeedPhase
    starter_feed: FeedPhase
    growth_feed: FeedPhase
    final_feed: FeedPhase
    
    # Additional costs
    medicine_costs: Optional[float] = 0.0
    miscellaneous_costs: Optional[float] = 0.0
    cost_variations: Optional[float] = 0.0
    
    # Mortality
    chicks_died: int
    
    # Removal batches (up to 15)
    removal_batches: List[RemovalBatch]

class CostBreakdown(BaseModel):
    chick_cost: float
    chick_cost_percent: float
    pre_starter_cost: float
    pre_starter_cost_percent: float
    starter_cost: float
    starter_cost_percent: float
    growth_cost: float
    growth_cost_percent: float
    final_cost: float
    final_cost_percent: float
    medicine_cost: float
    medicine_cost_percent: float
    miscellaneous_cost: float
    miscellaneous_cost_percent: float
    cost_variations: float
    cost_variations_percent: float

class BroilerCalculation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    input_data: BroilerCalculationInput
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Calculated fields
    surviving_chicks: int
    removed_chicks: int
    missing_chicks: int
    total_weight_produced_kg: float
    weighted_average_age: float
    
    # Feed metrics
    total_feed_consumed_kg: float
    feed_conversion_ratio: float
    
    # Financial metrics
    mortality_rate_percent: float
    total_cost: float
    cost_per_kg: float
    cost_breakdown: CostBreakdown
    
    # Performance insights
    average_weight_per_chick: float
    daily_weight_gain: float

class CalculationResult(BaseModel):
    calculation: BroilerCalculation
    insights: List[str]

# Business Logic Functions
def calculate_enhanced_broiler_metrics(input_data: BroilerCalculationInput) -> BroilerCalculation:
    """
    Calculate enhanced broiler chicken production metrics with detailed tracking
    """
    # Basic calculations
    surviving_chicks = input_data.initial_chicks - input_data.chicks_died
    
    # Calculate removal totals
    removed_chicks = sum(batch.quantity for batch in input_data.removal_batches)
    total_weight_produced_kg = sum(batch.total_weight_kg for batch in input_data.removal_batches)
    missing_chicks = surviving_chicks - removed_chicks
    
    # Calculate weighted average age
    total_weighted_age = sum(batch.quantity * batch.age_days for batch in input_data.removal_batches)
    weighted_average_age = total_weighted_age / removed_chicks if removed_chicks > 0 else 0
    
    # Feed calculations
    total_feed_consumed_kg = (
        input_data.pre_starter_feed.consumption_kg +
        input_data.starter_feed.consumption_kg +
        input_data.growth_feed.consumption_kg +
        input_data.final_feed.consumption_kg
    )
    
    # Feed Conversion Ratio (FCR) = Feed consumed / Weight gained
    feed_conversion_ratio = total_feed_consumed_kg / total_weight_produced_kg if total_weight_produced_kg > 0 else 0
    
    # Mortality Rate
    mortality_rate_percent = (input_data.chicks_died / input_data.initial_chicks) * 100
    
    # Cost calculations
    chick_cost = input_data.initial_chicks * input_data.chick_cost_per_unit
    pre_starter_cost = input_data.pre_starter_feed.consumption_kg * input_data.pre_starter_feed.cost_per_kg
    starter_cost = input_data.starter_feed.consumption_kg * input_data.starter_feed.cost_per_kg
    growth_cost = input_data.growth_feed.consumption_kg * input_data.growth_feed.cost_per_kg
    final_cost = input_data.final_feed.consumption_kg * input_data.final_feed.cost_per_kg
    
    total_cost = (
        chick_cost + pre_starter_cost + starter_cost + growth_cost + final_cost +
        input_data.medicine_costs + input_data.miscellaneous_costs + input_data.cost_variations
    )
    
    # Cost breakdown with percentages
    cost_breakdown = CostBreakdown(
        chick_cost=round(chick_cost, 2),
        chick_cost_percent=round((chick_cost / total_cost) * 100, 1) if total_cost > 0 else 0,
        pre_starter_cost=round(pre_starter_cost, 2),
        pre_starter_cost_percent=round((pre_starter_cost / total_cost) * 100, 1) if total_cost > 0 else 0,
        starter_cost=round(starter_cost, 2),
        starter_cost_percent=round((starter_cost / total_cost) * 100, 1) if total_cost > 0 else 0,
        growth_cost=round(growth_cost, 2),
        growth_cost_percent=round((growth_cost / total_cost) * 100, 1) if total_cost > 0 else 0,
        final_cost=round(final_cost, 2),
        final_cost_percent=round((final_cost / total_cost) * 100, 1) if total_cost > 0 else 0,
        medicine_cost=round(input_data.medicine_costs, 2),
        medicine_cost_percent=round((input_data.medicine_costs / total_cost) * 100, 1) if total_cost > 0 else 0,
        miscellaneous_cost=round(input_data.miscellaneous_costs, 2),
        miscellaneous_cost_percent=round((input_data.miscellaneous_costs / total_cost) * 100, 1) if total_cost > 0 else 0,
        cost_variations=round(input_data.cost_variations, 2),
        cost_variations_percent=round((input_data.cost_variations / total_cost) * 100, 1) if total_cost > 0 else 0
    )
    
    # Cost per kg
    cost_per_kg = total_cost / total_weight_produced_kg if total_weight_produced_kg > 0 else 0
    
    # Performance metrics
    average_weight_per_chick = total_weight_produced_kg / removed_chicks if removed_chicks > 0 else 0
    daily_weight_gain = average_weight_per_chick / weighted_average_age if weighted_average_age > 0 else 0
    
    # Create calculation object
    calculation = BroilerCalculation(
        input_data=input_data,
        surviving_chicks=surviving_chicks,
        removed_chicks=removed_chicks,
        missing_chicks=missing_chicks,
        total_weight_produced_kg=round(total_weight_produced_kg, 2),
        weighted_average_age=round(weighted_average_age, 1),
        total_feed_consumed_kg=round(total_feed_consumed_kg, 2),
        feed_conversion_ratio=round(feed_conversion_ratio, 2),
        mortality_rate_percent=round(mortality_rate_percent, 2),
        total_cost=round(total_cost, 2),
        cost_per_kg=round(cost_per_kg, 2),
        cost_breakdown=cost_breakdown,
        average_weight_per_chick=round(average_weight_per_chick, 2),
        daily_weight_gain=round(daily_weight_gain, 3)
    )
    
    return calculation

def generate_enhanced_insights(calculation: BroilerCalculation) -> List[str]:
    """
    Generate enhanced business insights based on the calculation results
    """
    insights = []
    
    # FCR insights
    if calculation.feed_conversion_ratio <= 1.6:
        insights.append("🎉 Outstanding feed conversion ratio! Your feeding efficiency is exceptional.")
    elif calculation.feed_conversion_ratio <= 1.9:
        insights.append("✅ Excellent feed conversion ratio. Very efficient feeding management.")
    elif calculation.feed_conversion_ratio <= 2.2:
        insights.append("✅ Good feed conversion ratio. You're managing feed efficiently.")
    elif calculation.feed_conversion_ratio <= 2.8:
        insights.append("⚠️ Average feed conversion ratio. Consider optimizing feed quality or management.")
    else:
        insights.append("❌ Poor feed conversion ratio. Review your feeding strategy and management practices.")
    
    # Mortality insights
    if calculation.mortality_rate_percent <= 3:
        insights.append("🎉 Excellent mortality rate! Your flock management is outstanding.")
    elif calculation.mortality_rate_percent <= 7:
        insights.append("✅ Good mortality rate. Your management practices are effective.")
    elif calculation.mortality_rate_percent <= 12:
        insights.append("⚠️ Average mortality rate. Consider reviewing health management protocols.")
    else:
        insights.append("❌ High mortality rate. Urgent review of housing, health, and management needed.")
    
    # Age insights
    if calculation.weighted_average_age <= 42:
        insights.append("⚡ Early processing age. Good for lighter weight market or cost optimization.")
    elif calculation.weighted_average_age <= 45:
        insights.append("📈 Optimal processing age range. Good balance of weight and efficiency.")
    else:
        insights.append("⏰ Later processing age. Higher weights but potentially lower efficiency.")
    
    # Daily weight gain insights
    if calculation.daily_weight_gain >= 0.065:
        insights.append("🚀 Excellent daily weight gain! Superior genetic performance and management.")
    elif calculation.daily_weight_gain >= 0.055:
        insights.append("✅ Good daily weight gain. Solid performance.")
    elif calculation.daily_weight_gain >= 0.045:
        insights.append("⚠️ Average daily weight gain. Room for improvement in nutrition or genetics.")
    else:
        insights.append("❌ Low daily weight gain. Review feed quality, genetics, and management.")
    
    # Missing chicks insight
    if calculation.missing_chicks > 0:
        missing_percent = (calculation.missing_chicks / calculation.input_data.initial_chicks) * 100
        if missing_percent > 5:
            insights.append(f"⚠️ High number of missing chicks ({calculation.missing_chicks}, {missing_percent:.1f}%). Check counting accuracy and potential losses.")
        else:
            insights.append(f"📝 {calculation.missing_chicks} missing chicks ({missing_percent:.1f}%) - normal variance range.")
    
    # Cost structure insights
    feed_total_percent = (
        calculation.cost_breakdown.pre_starter_cost_percent +
        calculation.cost_breakdown.starter_cost_percent +
        calculation.cost_breakdown.growth_cost_percent +
        calculation.cost_breakdown.final_cost_percent
    )
    
    if feed_total_percent > 70:
        insights.append("💰 Feed costs are high (>70% of total). Consider feed sourcing optimization.")
    elif feed_total_percent < 50:
        insights.append("💰 Feed costs are low relative to total. Good feed cost management.")
    
    return insights

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Enhanced Broiler Chicken Cost Calculator API"}

@api_router.post("/calculate", response_model=CalculationResult)
async def calculate_broiler_costs(input_data: BroilerCalculationInput):
    """
    Calculate enhanced broiler chicken production costs and metrics
    """
    # Validate input
    if input_data.initial_chicks <= 0:
        raise HTTPException(status_code=400, detail="Initial chicks must be greater than 0")
    if input_data.chicks_died > input_data.initial_chicks:
        raise HTTPException(status_code=400, detail="Chicks died cannot be more than initial chicks")
    if not input_data.removal_batches:
        raise HTTPException(status_code=400, detail="At least one removal batch is required")
    
    # Validate removal batches
    total_removed = sum(batch.quantity for batch in input_data.removal_batches)
    surviving_chicks = input_data.initial_chicks - input_data.chicks_died
    if total_removed > surviving_chicks:
        raise HTTPException(status_code=400, detail="Total removed chicks cannot exceed surviving chicks")
    
    # Validate ages
    for i, batch in enumerate(input_data.removal_batches):
        if batch.age_days < 35 or batch.age_days > 60:
            raise HTTPException(status_code=400, detail=f"Batch {i+1}: Age must be between 35-60 days")
        if batch.quantity <= 0:
            raise HTTPException(status_code=400, detail=f"Batch {i+1}: Quantity must be greater than 0")
        if batch.total_weight_kg <= 0:
            raise HTTPException(status_code=400, detail=f"Batch {i+1}: Weight must be greater than 0")
    
    try:
        # Calculate metrics
        calculation = calculate_enhanced_broiler_metrics(input_data)
        
        # Generate insights
        insights = generate_enhanced_insights(calculation)
        
        # Save to database
        await db.broiler_calculations.insert_one(calculation.dict())
        
        return CalculationResult(calculation=calculation, insights=insights)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")

@api_router.get("/calculations", response_model=List[BroilerCalculation])
async def get_calculations():
    """
    Get all saved calculations
    """
    calculations = await db.broiler_calculations.find().sort("created_at", -1).limit(20).to_list(20)
    return [BroilerCalculation(**calc) for calc in calculations]

@api_router.delete("/calculations/{calculation_id}")
async def delete_calculation(calculation_id: str):
    """
    Delete a specific calculation
    """
    result = await db.broiler_calculations.delete_one({"id": calculation_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return {"message": "Calculation deleted successfully"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
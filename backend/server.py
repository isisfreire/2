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


# Define Models for Broiler Chicken Calculator
class BroilerCalculation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    initial_chicks: int
    chick_cost_per_unit: float
    total_feed_consumed_kg: float
    feed_cost_per_kg: float
    chicks_died: int
    final_weight_per_chick_kg: float
    other_costs: Optional[float] = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Calculated fields
    surviving_chicks: Optional[int] = None
    total_weight_produced_kg: Optional[float] = None
    feed_conversion_ratio: Optional[float] = None
    mortality_rate_percent: Optional[float] = None
    total_cost: Optional[float] = None
    cost_per_kg: Optional[float] = None
    revenue_per_kg: Optional[float] = None
    total_revenue: Optional[float] = None
    profit_loss: Optional[float] = None

class BroilerCalculationInput(BaseModel):
    initial_chicks: int
    chick_cost_per_unit: float
    total_feed_consumed_kg: float
    feed_cost_per_kg: float
    chicks_died: int
    final_weight_per_chick_kg: float
    other_costs: Optional[float] = 0.0
    revenue_per_kg: Optional[float] = 0.0

class CalculationResult(BaseModel):
    calculation: BroilerCalculation
    insights: List[str]

# Business Logic Functions
def calculate_broiler_metrics(input_data: BroilerCalculationInput) -> BroilerCalculation:
    """
    Calculate all broiler chicken production metrics
    """
    # Basic calculations
    surviving_chicks = input_data.initial_chicks - input_data.chicks_died
    total_weight_produced_kg = surviving_chicks * input_data.final_weight_per_chick_kg
    
    # Feed Conversion Ratio (FCR) = Feed consumed / Weight gained
    feed_conversion_ratio = input_data.total_feed_consumed_kg / total_weight_produced_kg if total_weight_produced_kg > 0 else 0
    
    # Mortality Rate
    mortality_rate_percent = (input_data.chicks_died / input_data.initial_chicks) * 100
    
    # Cost calculations
    total_chick_cost = input_data.initial_chicks * input_data.chick_cost_per_unit
    total_feed_cost = input_data.total_feed_consumed_kg * input_data.feed_cost_per_kg
    total_cost = total_chick_cost + total_feed_cost + input_data.other_costs
    
    # Cost per kg
    cost_per_kg = total_cost / total_weight_produced_kg if total_weight_produced_kg > 0 else 0
    
    # Revenue and profit calculations
    total_revenue = total_weight_produced_kg * input_data.revenue_per_kg if input_data.revenue_per_kg else 0
    profit_loss = total_revenue - total_cost
    
    # Create calculation object
    calculation = BroilerCalculation(
        **input_data.dict(),
        surviving_chicks=surviving_chicks,
        total_weight_produced_kg=round(total_weight_produced_kg, 2),
        feed_conversion_ratio=round(feed_conversion_ratio, 2),
        mortality_rate_percent=round(mortality_rate_percent, 2),
        total_cost=round(total_cost, 2),
        cost_per_kg=round(cost_per_kg, 2),
        total_revenue=round(total_revenue, 2),
        profit_loss=round(profit_loss, 2)
    )
    
    return calculation

def generate_insights(calculation: BroilerCalculation) -> List[str]:
    """
    Generate business insights based on the calculation results
    """
    insights = []
    
    # FCR insights
    if calculation.feed_conversion_ratio <= 1.8:
        insights.append("🎉 Excellent feed conversion ratio! Your feeding efficiency is very good.")
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
    
    # Profitability insights
    if calculation.profit_loss > 0:
        roi = (calculation.profit_loss / calculation.total_cost) * 100
        insights.append(f"💰 Profitable operation! ROI: {roi:.1f}%")
    elif calculation.profit_loss == 0:
        insights.append("💰 Break-even operation. Consider ways to improve profitability.")
    else:
        loss_percent = abs(calculation.profit_loss / calculation.total_cost) * 100
        insights.append(f"📉 Loss-making operation. Loss: {loss_percent:.1f}% of total cost.")
    
    # Cost efficiency insights
    if calculation.cost_per_kg <= 2.5:
        insights.append("💵 Low production cost per kg. Very competitive!")
    elif calculation.cost_per_kg <= 3.5:
        insights.append("💵 Moderate production cost per kg. Room for improvement.")
    else:
        insights.append("💵 High production cost per kg. Focus on cost reduction strategies.")
    
    return insights

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Broiler Chicken Cost Calculator API"}

@api_router.post("/calculate", response_model=CalculationResult)
async def calculate_broiler_costs(input_data: BroilerCalculationInput):
    """
    Calculate broiler chicken production costs and metrics
    """
    try:
        # Validate input
        if input_data.initial_chicks <= 0:
            raise HTTPException(status_code=400, detail="Initial chicks must be greater than 0")
        if input_data.chicks_died > input_data.initial_chicks:
            raise HTTPException(status_code=400, detail="Chicks died cannot be more than initial chicks")
        if input_data.total_feed_consumed_kg <= 0:
            raise HTTPException(status_code=400, detail="Feed consumed must be greater than 0")
        if input_data.final_weight_per_chick_kg <= 0:
            raise HTTPException(status_code=400, detail="Final weight per chick must be greater than 0")
        
        # Calculate metrics
        calculation = calculate_broiler_metrics(input_data)
        
        # Generate insights
        insights = generate_insights(calculation)
        
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
from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import uuid
from datetime import datetime
import json
import statistics

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Create exports directory
EXPORTS_DIR = ROOT_DIR / "exports"
EXPORTS_DIR.mkdir(exist_ok=True)

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
    # Batch identification
    batch_id: str
    shed_number: str
    handler_name: str
    
    # Basic data
    initial_chicks: int
    chick_cost_per_unit: float
    
    # Feed phases
    pre_starter_feed: FeedPhase
    starter_feed: FeedPhase
    growth_feed: FeedPhase
    final_feed: FeedPhase
    
    # Enhanced costs
    medicine_costs: Optional[float] = 0.0
    miscellaneous_costs: Optional[float] = 0.0
    cost_variations: Optional[float] = 0.0
    sawdust_bedding_cost: Optional[float] = 0.0
    chicken_bedding_sale_revenue: Optional[float] = 0.0
    
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
    sawdust_bedding_cost: float
    sawdust_bedding_cost_percent: float

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
    total_revenue: float
    net_cost_per_kg: float  # After bedding revenue
    cost_breakdown: CostBreakdown
    
    # Performance insights
    average_weight_per_chick: float
    daily_weight_gain: float

class Handler(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class HandlerPerformance(BaseModel):
    handler_name: str
    total_batches: int
    avg_feed_conversion_ratio: float
    avg_mortality_rate: float
    avg_daily_weight_gain: float
    avg_cost_per_kg: float
    total_chicks_processed: int
    performance_score: float

class CalculationResult(BaseModel):
    calculation: BroilerCalculation
    insights: List[str]

class BatchSummary(BaseModel):
    batch_id: str
    shed_number: str
    handler_name: str
    date: datetime
    initial_chicks: int
    fcr: float
    mortality_percent: float
    cost_per_kg: float

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
        input_data.medicine_costs + input_data.miscellaneous_costs + 
        input_data.cost_variations + input_data.sawdust_bedding_cost
    )
    
    # Revenue from chicken bedding sale
    total_revenue = input_data.chicken_bedding_sale_revenue
    
    # Net cost after bedding revenue
    net_cost = total_cost - total_revenue
    net_cost_per_kg = net_cost / total_weight_produced_kg if total_weight_produced_kg > 0 else 0
    
    # Cost breakdown with percentages (based on gross cost)
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
        cost_variations_percent=round((input_data.cost_variations / total_cost) * 100, 1) if total_cost > 0 else 0,
        sawdust_bedding_cost=round(input_data.sawdust_bedding_cost, 2),
        sawdust_bedding_cost_percent=round((input_data.sawdust_bedding_cost / total_cost) * 100, 1) if total_cost > 0 else 0
    )
    
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
        total_revenue=round(total_revenue, 2),
        net_cost_per_kg=round(net_cost_per_kg, 2),
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
    
    # Bedding revenue insight
    if calculation.total_revenue > 0:
        revenue_impact = (calculation.total_revenue / calculation.total_cost) * 100
        insights.append(f"💰 Bedding sale revenue reduces cost per kg by {revenue_impact:.1f}% - excellent waste monetization!")
    
    # Handler performance context will be added separately
    
    return insights

async def calculate_handler_performance(handler_name: str) -> Optional[HandlerPerformance]:
    """
    Calculate performance metrics for a specific handler based on all their batches
    """
    # Get all calculations for this handler
    calculations = await db.broiler_calculations.find({"input_data.handler_name": handler_name}).to_list(1000)
    
    if not calculations:
        return None
    
    # Calculate averages
    fcr_values = [calc["feed_conversion_ratio"] for calc in calculations]
    mortality_values = [calc["mortality_rate_percent"] for calc in calculations]
    daily_gain_values = [calc["daily_weight_gain"] for calc in calculations]
    cost_per_kg_values = [calc["net_cost_per_kg"] for calc in calculations]
    total_chicks = sum(calc["input_data"]["initial_chicks"] for calc in calculations)
    
    avg_fcr = statistics.mean(fcr_values)
    avg_mortality = statistics.mean(mortality_values)
    avg_daily_gain = statistics.mean(daily_gain_values)
    avg_cost_per_kg = statistics.mean(cost_per_kg_values)
    
    # Calculate performance score (0-100, higher is better)
    # FCR: lower is better (excellent: 1.6, poor: 2.8)
    fcr_score = max(0, min(100, (2.8 - avg_fcr) / (2.8 - 1.6) * 100))
    
    # Mortality: lower is better (excellent: 3%, poor: 12%)
    mortality_score = max(0, min(100, (12 - avg_mortality) / (12 - 3) * 100))
    
    # Daily gain: higher is better (excellent: 0.065, poor: 0.045)
    gain_score = max(0, min(100, (avg_daily_gain - 0.045) / (0.065 - 0.045) * 100))
    
    # Cost per kg: lower is better (this is context-dependent, using 25% weight)
    performance_score = (fcr_score * 0.35 + mortality_score * 0.35 + gain_score * 0.30)
    
    return HandlerPerformance(
        handler_name=handler_name,
        total_batches=len(calculations),
        avg_feed_conversion_ratio=round(avg_fcr, 2),
        avg_mortality_rate=round(avg_mortality, 2),
        avg_daily_weight_gain=round(avg_daily_gain, 3),
        avg_cost_per_kg=round(avg_cost_per_kg, 2),
        total_chicks_processed=total_chicks,
        performance_score=round(performance_score, 1)
    )

async def export_batch_report(calculation: BroilerCalculation) -> str:
    """
    Export batch calculation to a JSON file
    """
    filename = f"batch_{calculation.input_data.batch_id}_{calculation.input_data.shed_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = EXPORTS_DIR / filename
    
    # Create export data
    export_data = {
        "batch_info": {
            "batch_id": calculation.input_data.batch_id,
            "shed_number": calculation.input_data.shed_number,
            "handler_name": calculation.input_data.handler_name,
            "date": calculation.created_at.isoformat()
        },
        "performance_metrics": {
            "feed_conversion_ratio": calculation.feed_conversion_ratio,
            "mortality_rate_percent": calculation.mortality_rate_percent,
            "weighted_average_age": calculation.weighted_average_age,
            "daily_weight_gain": calculation.daily_weight_gain,
            "cost_per_kg": calculation.net_cost_per_kg
        },
        "production_data": {
            "initial_chicks": calculation.input_data.initial_chicks,
            "surviving_chicks": calculation.surviving_chicks,
            "removed_chicks": calculation.removed_chicks,
            "missing_chicks": calculation.missing_chicks,
            "total_weight_produced_kg": calculation.total_weight_produced_kg,
            "total_feed_consumed_kg": calculation.total_feed_consumed_kg
        },
        "financial_summary": {
            "total_cost": calculation.total_cost,
            "total_revenue": calculation.total_revenue,
            "net_cost_per_kg": calculation.net_cost_per_kg,
            "cost_breakdown": calculation.cost_breakdown.dict()
        },
        "removal_batches": [batch.dict() for batch in calculation.input_data.removal_batches]
    }
    
    # Write to file
    with open(filepath, 'w') as f:
        json.dump(export_data, f, indent=2, default=str)
    
    return filename

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Enhanced Broiler Farm Management System API"}

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
    
    # Check if batch ID already exists
    existing_batch = await db.broiler_calculations.find_one({"input_data.batch_id": input_data.batch_id})
    if existing_batch:
        raise HTTPException(status_code=400, detail=f"Batch ID '{input_data.batch_id}' already exists")
    
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
        
        # Add handler to database if not exists
        existing_handler = await db.handlers.find_one({"name": input_data.handler_name})
        if not existing_handler:
            handler = Handler(name=input_data.handler_name)
            await db.handlers.insert_one(handler.dict())
        
        # Save calculation to database
        await db.broiler_calculations.insert_one(calculation.dict())
        
        # Export batch report
        filename = await export_batch_report(calculation)
        
        # Add export info to insights
        insights.append(f"📄 Batch report exported as: {filename}")
        
        return CalculationResult(calculation=calculation, insights=insights)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")

@api_router.get("/calculations", response_model=List[BatchSummary])
async def get_calculations():
    """
    Get all saved calculations summary
    """
    calculations = await db.broiler_calculations.find().sort("created_at", -1).to_list(50)
    summaries = []
    
    for calc in calculations:
        summary = BatchSummary(
            batch_id=calc["input_data"]["batch_id"],
            shed_number=calc["input_data"]["shed_number"],
            handler_name=calc["input_data"]["handler_name"],
            date=calc["created_at"],
            initial_chicks=calc["input_data"]["initial_chicks"],
            fcr=calc["feed_conversion_ratio"],
            mortality_percent=calc["mortality_rate_percent"],
            cost_per_kg=calc["net_cost_per_kg"]
        )
        summaries.append(summary)
    
    return summaries

@api_router.get("/handlers")
async def get_handlers():
    """
    Get all handlers
    """
    handlers = await db.handlers.find().sort("name", 1).to_list(100)
    return [handler["name"] for handler in handlers]

@api_router.get("/handlers/performance")
async def get_handlers_performance():
    """
    Get performance analysis for all handlers
    """
    handlers = await db.handlers.find().to_list(100)
    performances = []
    
    for handler in handlers:
        performance = await calculate_handler_performance(handler["name"])
        if performance:
            performances.append(performance)
    
    # Sort by performance score (descending)
    performances.sort(key=lambda x: x.performance_score, reverse=True)
    
    return performances

@api_router.get("/handlers/{handler_name}/performance")
async def get_handler_performance(handler_name: str):
    """
    Get performance analysis for a specific handler
    """
    performance = await calculate_handler_performance(handler_name)
    if not performance:
        raise HTTPException(status_code=404, detail="Handler not found or no batches recorded")
    
    return performance

@api_router.get("/batches/{batch_id}")
async def get_batch_details(batch_id: str):
    """
    Get detailed information for a specific batch
    """
    calculation = await db.broiler_calculations.find_one({"input_data.batch_id": batch_id})
    if not calculation:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    return BroilerCalculation(**calculation)

@api_router.get("/export/{filename}")
async def download_export(filename: str):
    """
    Download exported batch report
    """
    filepath = EXPORTS_DIR / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Export file not found")
    
    return FileResponse(filepath, filename=filename)

@api_router.get("/sheds")
async def get_sheds():
    """
    Get all shed numbers
    """
    calculations = await db.broiler_calculations.find().to_list(1000)
    sheds = list(set(calc["input_data"]["shed_number"] for calc in calculations))
    return sorted(sheds)

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
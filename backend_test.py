import requests
import json
import unittest
import os
from dotenv import load_dotenv
import sys

# Load environment variables from frontend .env file to get the backend URL
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

class EnhancedBroilerCalculatorAPITest(unittest.TestCase):
    """Test suite for the Enhanced Broiler Chicken Cost Calculator API"""

    def setUp(self):
        """Set up test case - verify API is accessible"""
        try:
            response = requests.get(f"{API_URL}/")
            if response.status_code != 200:
                print(f"API is not accessible. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                sys.exit(1)
        except Exception as e:
            print(f"Error connecting to API: {str(e)}")
            sys.exit(1)

    def test_api_health(self):
        """Test API health check endpoint"""
        response = requests.get(f"{API_URL}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["message"], "Enhanced Broiler Chicken Cost Calculator API")

    def test_professional_scenario(self):
        """
        Test professional scenario with 10,000 chicks, $0.45/chick, 4 feed phases,
        medicine costs, miscellaneous costs, cost variations, and multiple removal batches
        """
        payload = {
            "initial_chicks": 10000,
            "chick_cost_per_unit": 0.45,
            
            # 4 feed phases
            "pre_starter_feed": {
                "consumption_kg": 500,
                "cost_per_kg": 0.65
            },
            "starter_feed": {
                "consumption_kg": 2500,
                "cost_per_kg": 0.45
            },
            "growth_feed": {
                "consumption_kg": 8000,
                "cost_per_kg": 0.40
            },
            "final_feed": {
                "consumption_kg": 12000,
                "cost_per_kg": 0.35
            },
            
            # Additional costs
            "medicine_costs": 800,
            "miscellaneous_costs": 500,
            "cost_variations": 300,
            
            # Mortality
            "chicks_died": 250,
            
            # Removal batches with different ages
            "removal_batches": [
                {"quantity": 2000, "total_weight_kg": 4600, "age_days": 35},
                {"quantity": 3000, "total_weight_kg": 7500, "age_days": 42},
                {"quantity": 4000, "total_weight_kg": 11200, "age_days": 50},
                {"quantity": 500, "total_weight_kg": 1500, "age_days": 45}
            ]
        }
        
        response = requests.post(f"{API_URL}/calculate", json=payload)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        calculation = data["calculation"]
        insights = data["insights"]
        
        # Verify basic calculations
        self.assertEqual(calculation["surviving_chicks"], 9750)
        self.assertEqual(calculation["removed_chicks"], 9500)
        self.assertEqual(calculation["missing_chicks"], 250)
        self.assertEqual(calculation["total_weight_produced_kg"], 24800.0)
        
        # Verify feed calculations
        total_feed = 500 + 2500 + 8000 + 12000
        self.assertEqual(calculation["total_feed_consumed_kg"], total_feed)
        
        # FCR should be around 0.93 (23000 / 24800)
        self.assertAlmostEqual(calculation["feed_conversion_ratio"], 0.93, delta=0.01)
        
        # Mortality rate should be 2.5%
        self.assertAlmostEqual(calculation["mortality_rate_percent"], 2.5, delta=0.01)
        
        # Weighted average age calculation
        # (2000*35 + 3000*42 + 4000*50 + 500*45) / 9500 = 44.05
        self.assertAlmostEqual(calculation["weighted_average_age"], 44.1, delta=0.1)
        
        # Verify cost breakdown
        cost_breakdown = calculation["cost_breakdown"]
        
        # Chick cost = 10000 * 0.45 = $4500
        self.assertAlmostEqual(cost_breakdown["chick_cost"], 4500.0, delta=0.01)
        
        # Pre-starter feed cost = 500 * 0.65 = $325
        self.assertAlmostEqual(cost_breakdown["pre_starter_cost"], 325.0, delta=0.01)
        
        # Starter feed cost = 2500 * 0.45 = $1125
        self.assertAlmostEqual(cost_breakdown["starter_cost"], 1125.0, delta=0.01)
        
        # Growth feed cost = 8000 * 0.40 = $3200
        self.assertAlmostEqual(cost_breakdown["growth_cost"], 3200.0, delta=0.01)
        
        # Final feed cost = 12000 * 0.35 = $4200
        self.assertAlmostEqual(cost_breakdown["final_cost"], 4200.0, delta=0.01)
        
        # Medicine cost = $800
        self.assertAlmostEqual(cost_breakdown["medicine_cost"], 800.0, delta=0.01)
        
        # Miscellaneous cost = $500
        self.assertAlmostEqual(cost_breakdown["miscellaneous_cost"], 500.0, delta=0.01)
        
        # Cost variations = $300
        self.assertAlmostEqual(cost_breakdown["cost_variations"], 300.0, delta=0.01)
        
        # Total cost = 4500 + 325 + 1125 + 3200 + 4200 + 800 + 500 + 300 = $14950
        self.assertAlmostEqual(calculation["total_cost"], 14950.0, delta=0.01)
        
        # Cost per kg = 14950 / 24800 = $0.60
        self.assertAlmostEqual(calculation["cost_per_kg"], 0.60, delta=0.01)
        
        # Verify percentages sum to 100%
        total_percentage = (
            cost_breakdown["chick_cost_percent"] +
            cost_breakdown["pre_starter_cost_percent"] +
            cost_breakdown["starter_cost_percent"] +
            cost_breakdown["growth_cost_percent"] +
            cost_breakdown["final_cost_percent"] +
            cost_breakdown["medicine_cost_percent"] +
            cost_breakdown["miscellaneous_cost_percent"] +
            cost_breakdown["cost_variations_percent"]
        )
        self.assertAlmostEqual(total_percentage, 100.0, delta=0.1)
        
        # Verify daily weight gain calculation
        # Average weight per chick = 24800 / 9500 = 2.61 kg
        # Daily weight gain = 2.61 / 44.1 = 0.059 kg/day
        self.assertAlmostEqual(calculation["average_weight_per_chick"], 2.61, delta=0.01)
        self.assertAlmostEqual(calculation["daily_weight_gain"], 0.059, delta=0.001)
        
        # Verify insights are generated
        self.assertTrue(len(insights) >= 5)
        
        # Check for specific insights
        fcr_insight = next((i for i in insights if "feed conversion ratio" in i.lower()), None)
        self.assertIsNotNone(fcr_insight)
        self.assertTrue("outstanding" in fcr_insight.lower())
        
        mortality_insight = next((i for i in insights if "mortality rate" in i.lower()), None)
        self.assertIsNotNone(mortality_insight)
        self.assertTrue("excellent" in mortality_insight.lower())
        
        missing_insight = next((i for i in insights if "missing chicks" in i.lower()), None)
        self.assertIsNotNone(missing_insight)

    def test_weighted_average_age_calculation(self):
        """Test weighted average age calculation with multiple batches at different ages"""
        payload = {
            "initial_chicks": 5000,
            "chick_cost_per_unit": 0.45,
            
            # 4 feed phases
            "pre_starter_feed": {
                "consumption_kg": 250,
                "cost_per_kg": 0.65
            },
            "starter_feed": {
                "consumption_kg": 1250,
                "cost_per_kg": 0.45
            },
            "growth_feed": {
                "consumption_kg": 4000,
                "cost_per_kg": 0.40
            },
            "final_feed": {
                "consumption_kg": 6000,
                "cost_per_kg": 0.35
            },
            
            # Additional costs
            "medicine_costs": 400,
            "miscellaneous_costs": 250,
            "cost_variations": 150,
            
            # Mortality
            "chicks_died": 125,
            
            # Removal batches with very different ages to test weighted average
            "removal_batches": [
                {"quantity": 1000, "total_weight_kg": 2000, "age_days": 35},
                {"quantity": 500, "total_weight_kg": 1250, "age_days": 40},
                {"quantity": 2000, "total_weight_kg": 6000, "age_days": 50},
                {"quantity": 1000, "total_weight_kg": 3500, "age_days": 60}
            ]
        }
        
        response = requests.post(f"{API_URL}/calculate", json=payload)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        calculation = data["calculation"]
        
        # Weighted average age calculation
        # (1000*35 + 500*40 + 2000*50 + 1000*60) / 4500 = 48.33
        self.assertAlmostEqual(calculation["weighted_average_age"], 48.3, delta=0.1)
        
        # Verify daily weight gain calculation based on weighted average age
        # Average weight per chick = 12750 / 4500 = 2.83 kg
        # Daily weight gain = 2.83 / 48.3 = 0.059 kg/day
        self.assertAlmostEqual(calculation["average_weight_per_chick"], 2.83, delta=0.01)
        self.assertAlmostEqual(calculation["daily_weight_gain"], 0.059, delta=0.001)

    def test_missing_chicks_tracking(self):
        """Test missing chicks tracking (surviving - removed = missing)"""
        payload = {
            "initial_chicks": 5000,
            "chick_cost_per_unit": 0.45,
            
            # 4 feed phases
            "pre_starter_feed": {
                "consumption_kg": 250,
                "cost_per_kg": 0.65
            },
            "starter_feed": {
                "consumption_kg": 1250,
                "cost_per_kg": 0.45
            },
            "growth_feed": {
                "consumption_kg": 4000,
                "cost_per_kg": 0.40
            },
            "final_feed": {
                "consumption_kg": 6000,
                "cost_per_kg": 0.35
            },
            
            # Additional costs
            "medicine_costs": 400,
            "miscellaneous_costs": 250,
            "cost_variations": 150,
            
            # Mortality
            "chicks_died": 200,
            
            # Removal batches with significant missing chicks
            "removal_batches": [
                {"quantity": 1000, "total_weight_kg": 2000, "age_days": 35},
                {"quantity": 1500, "total_weight_kg": 3750, "age_days": 40},
                {"quantity": 2000, "total_weight_kg": 6000, "age_days": 50}
            ]
        }
        
        response = requests.post(f"{API_URL}/calculate", json=payload)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        calculation = data["calculation"]
        insights = data["insights"]
        
        # Surviving chicks = 5000 - 200 = 4800
        self.assertEqual(calculation["surviving_chicks"], 4800)
        
        # Removed chicks = 1000 + 1500 + 2000 = 4500
        self.assertEqual(calculation["removed_chicks"], 4500)
        
        # Missing chicks = 4800 - 4500 = 300
        self.assertEqual(calculation["missing_chicks"], 300)
        
        # Check for missing chicks insight
        missing_insight = next((i for i in insights if "missing chicks" in i.lower()), None)
        self.assertIsNotNone(missing_insight)
        
        # Missing percentage = 300 / 5000 * 100 = 6%
        # Should trigger a warning since it's > 5%
        self.assertTrue("high number of missing chicks" in missing_insight.lower())

    def test_cost_breakdown_percentages(self):
        """Test cost breakdown percentages sum to 100%"""
        payload = {
            "initial_chicks": 5000,
            "chick_cost_per_unit": 0.45,
            
            # 4 feed phases with varying costs
            "pre_starter_feed": {
                "consumption_kg": 250,
                "cost_per_kg": 0.65
            },
            "starter_feed": {
                "consumption_kg": 1250,
                "cost_per_kg": 0.45
            },
            "growth_feed": {
                "consumption_kg": 4000,
                "cost_per_kg": 0.40
            },
            "final_feed": {
                "consumption_kg": 6000,
                "cost_per_kg": 0.35
            },
            
            # Additional costs
            "medicine_costs": 400,
            "miscellaneous_costs": 250,
            "cost_variations": 150,
            
            # Mortality
            "chicks_died": 125,
            
            # Removal batches
            "removal_batches": [
                {"quantity": 4500, "total_weight_kg": 11250, "age_days": 45}
            ]
        }
        
        response = requests.post(f"{API_URL}/calculate", json=payload)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        calculation = data["calculation"]
        cost_breakdown = calculation["cost_breakdown"]
        
        # Calculate expected costs
        chick_cost = 5000 * 0.45  # $2250
        pre_starter_cost = 250 * 0.65  # $162.5
        starter_cost = 1250 * 0.45  # $562.5
        growth_cost = 4000 * 0.40  # $1600
        final_cost = 6000 * 0.35  # $2100
        medicine_cost = 400
        misc_cost = 250
        cost_variations = 150
        
        total_cost = chick_cost + pre_starter_cost + starter_cost + growth_cost + final_cost + medicine_cost + misc_cost + cost_variations
        
        # Verify individual costs
        self.assertAlmostEqual(cost_breakdown["chick_cost"], chick_cost, delta=0.01)
        self.assertAlmostEqual(cost_breakdown["pre_starter_cost"], pre_starter_cost, delta=0.01)
        self.assertAlmostEqual(cost_breakdown["starter_cost"], starter_cost, delta=0.01)
        self.assertAlmostEqual(cost_breakdown["growth_cost"], growth_cost, delta=0.01)
        self.assertAlmostEqual(cost_breakdown["final_cost"], final_cost, delta=0.01)
        self.assertAlmostEqual(cost_breakdown["medicine_cost"], medicine_cost, delta=0.01)
        self.assertAlmostEqual(cost_breakdown["miscellaneous_cost"], misc_cost, delta=0.01)
        self.assertAlmostEqual(cost_breakdown["cost_variations"], cost_variations, delta=0.01)
        
        # Verify percentages
        self.assertAlmostEqual(cost_breakdown["chick_cost_percent"], (chick_cost / total_cost) * 100, delta=0.1)
        self.assertAlmostEqual(cost_breakdown["pre_starter_cost_percent"], (pre_starter_cost / total_cost) * 100, delta=0.1)
        self.assertAlmostEqual(cost_breakdown["starter_cost_percent"], (starter_cost / total_cost) * 100, delta=0.1)
        self.assertAlmostEqual(cost_breakdown["growth_cost_percent"], (growth_cost / total_cost) * 100, delta=0.1)
        self.assertAlmostEqual(cost_breakdown["final_cost_percent"], (final_cost / total_cost) * 100, delta=0.1)
        self.assertAlmostEqual(cost_breakdown["medicine_cost_percent"], (medicine_cost / total_cost) * 100, delta=0.1)
        self.assertAlmostEqual(cost_breakdown["miscellaneous_cost_percent"], (misc_cost / total_cost) * 100, delta=0.1)
        self.assertAlmostEqual(cost_breakdown["cost_variations_percent"], (cost_variations / total_cost) * 100, delta=0.1)
        
        # Verify percentages sum to 100%
        total_percentage = (
            cost_breakdown["chick_cost_percent"] +
            cost_breakdown["pre_starter_cost_percent"] +
            cost_breakdown["starter_cost_percent"] +
            cost_breakdown["growth_cost_percent"] +
            cost_breakdown["final_cost_percent"] +
            cost_breakdown["medicine_cost_percent"] +
            cost_breakdown["miscellaneous_cost_percent"] +
            cost_breakdown["cost_variations_percent"]
        )
        self.assertAlmostEqual(total_percentage, 100.0, delta=0.1)

    def test_feed_phase_validation(self):
        """Test feed phase validation with zero or negative values"""
        # Test with negative pre-starter feed consumption
        payload = {
            "initial_chicks": 5000,
            "chick_cost_per_unit": 0.45,
            
            # Negative pre-starter feed consumption
            "pre_starter_feed": {
                "consumption_kg": -10,
                "cost_per_kg": 0.65
            },
            "starter_feed": {
                "consumption_kg": 1250,
                "cost_per_kg": 0.45
            },
            "growth_feed": {
                "consumption_kg": 4000,
                "cost_per_kg": 0.40
            },
            "final_feed": {
                "consumption_kg": 6000,
                "cost_per_kg": 0.35
            },
            
            "medicine_costs": 400,
            "miscellaneous_costs": 250,
            "cost_variations": 150,
            "chicks_died": 125,
            "removal_batches": [
                {"quantity": 4500, "total_weight_kg": 11250, "age_days": 45}
            ]
        }
        
        response = requests.post(f"{API_URL}/calculate", json=payload)
        self.assertEqual(response.status_code, 400)
        
        # Test with negative feed cost
        payload = {
            "initial_chicks": 5000,
            "chick_cost_per_unit": 0.45,
            
            "pre_starter_feed": {
                "consumption_kg": 250,
                "cost_per_kg": 0.65
            },
            "starter_feed": {
                "consumption_kg": 1250,
                "cost_per_kg": -0.45  # Negative cost
            },
            "growth_feed": {
                "consumption_kg": 4000,
                "cost_per_kg": 0.40
            },
            "final_feed": {
                "consumption_kg": 6000,
                "cost_per_kg": 0.35
            },
            
            "medicine_costs": 400,
            "miscellaneous_costs": 250,
            "cost_variations": 150,
            "chicks_died": 125,
            "removal_batches": [
                {"quantity": 4500, "total_weight_kg": 11250, "age_days": 45}
            ]
        }
        
        response = requests.post(f"{API_URL}/calculate", json=payload)
        self.assertEqual(response.status_code, 400)

    def test_age_validation(self):
        """Test age validation (reject ages outside 35-60 range)"""
        # Test with age below 35 days
        payload = {
            "initial_chicks": 5000,
            "chick_cost_per_unit": 0.45,
            
            "pre_starter_feed": {
                "consumption_kg": 250,
                "cost_per_kg": 0.65
            },
            "starter_feed": {
                "consumption_kg": 1250,
                "cost_per_kg": 0.45
            },
            "growth_feed": {
                "consumption_kg": 4000,
                "cost_per_kg": 0.40
            },
            "final_feed": {
                "consumption_kg": 6000,
                "cost_per_kg": 0.35
            },
            
            "medicine_costs": 400,
            "miscellaneous_costs": 250,
            "cost_variations": 150,
            "chicks_died": 125,
            "removal_batches": [
                {"quantity": 4500, "total_weight_kg": 11250, "age_days": 30}  # Age below 35
            ]
        }
        
        response = requests.post(f"{API_URL}/calculate", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Age must be between 35-60 days", response.text)
        
        # Test with age above 60 days
        payload = {
            "initial_chicks": 5000,
            "chick_cost_per_unit": 0.45,
            
            "pre_starter_feed": {
                "consumption_kg": 250,
                "cost_per_kg": 0.65
            },
            "starter_feed": {
                "consumption_kg": 1250,
                "cost_per_kg": 0.45
            },
            "growth_feed": {
                "consumption_kg": 4000,
                "cost_per_kg": 0.40
            },
            "final_feed": {
                "consumption_kg": 6000,
                "cost_per_kg": 0.35
            },
            
            "medicine_costs": 400,
            "miscellaneous_costs": 250,
            "cost_variations": 150,
            "chicks_died": 125,
            "removal_batches": [
                {"quantity": 4500, "total_weight_kg": 11250, "age_days": 65}  # Age above 60
            ]
        }
        
        response = requests.post(f"{API_URL}/calculate", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Age must be between 35-60 days", response.text)

    def test_get_calculations(self):
        """Test retrieving calculation history"""
        # First, create a calculation to ensure there's at least one in the database
        payload = {
            "initial_chicks": 5000,
            "chick_cost_per_unit": 0.45,
            
            "pre_starter_feed": {
                "consumption_kg": 250,
                "cost_per_kg": 0.65
            },
            "starter_feed": {
                "consumption_kg": 1250,
                "cost_per_kg": 0.45
            },
            "growth_feed": {
                "consumption_kg": 4000,
                "cost_per_kg": 0.40
            },
            "final_feed": {
                "consumption_kg": 6000,
                "cost_per_kg": 0.35
            },
            
            "medicine_costs": 400,
            "miscellaneous_costs": 250,
            "cost_variations": 150,
            "chicks_died": 125,
            "removal_batches": [
                {"quantity": 4500, "total_weight_kg": 11250, "age_days": 45}
            ]
        }
        
        # Create a calculation
        requests.post(f"{API_URL}/calculate", json=payload)
        
        # Now retrieve calculations
        response = requests.get(f"{API_URL}/calculations")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIsInstance(data, list)
        
        # If there are calculations, verify the structure
        if data:
            calculation = data[0]
            self.assertIn("id", calculation)
            self.assertIn("input_data", calculation)
            self.assertIn("feed_conversion_ratio", calculation)
            self.assertIn("mortality_rate_percent", calculation)
            self.assertIn("cost_per_kg", calculation)
            self.assertIn("cost_breakdown", calculation)
            self.assertIn("weighted_average_age", calculation)
            self.assertIn("missing_chicks", calculation)

if __name__ == "__main__":
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
import requests
import json
import unittest
import os
from dotenv import load_dotenv
import sys
import time
import uuid

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
            
        # Generate unique batch ID for tests
        self.unique_batch_id = f"BATCH-TEST-{uuid.uuid4().hex[:8]}"
        
        # Generate unique handler name for performance tests
        self.unique_handler_name = f"Handler-{uuid.uuid4().hex[:8]}"

    def test_api_health(self):
        """Test API health check endpoint"""
        response = requests.get(f"{API_URL}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["message"], "Enhanced Broiler Farm Management System API")

    def test_complete_farm_scenario(self):
        """
        Test complete farm scenario with batch identification, enhanced costs, and multiple removal batches
        as specified in the test case:
        - Batch: "BATCH-2024-001", Shed: "SHED-A1", Handler: "John Smith"
        - 10,000 chicks, $0.45/chick, 4 feed phases, sawdust bedding: $400, bedding sale: $600
        - Medicine: $800, misc: $500, variations: $300, 250 died
        - Multiple removal batches with different ages
        """
        payload = {
            # Batch identification
            "batch_id": self.unique_batch_id,
            "shed_number": "SHED-A1",
            "handler_name": "John Smith",
            
            # Basic data
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
            
            # Enhanced costs
            "medicine_costs": 800,
            "miscellaneous_costs": 500,
            "cost_variations": 300,
            "sawdust_bedding_cost": 400,
            "chicken_bedding_sale_revenue": 600,
            
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
        
        # Verify batch identification
        self.assertEqual(calculation["input_data"]["batch_id"], self.unique_batch_id)
        self.assertEqual(calculation["input_data"]["shed_number"], "SHED-A1")
        self.assertEqual(calculation["input_data"]["handler_name"], "John Smith")
        
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
        
        # Sawdust bedding cost = $400
        self.assertAlmostEqual(cost_breakdown["sawdust_bedding_cost"], 400.0, delta=0.01)
        
        # Total cost = 4500 + 325 + 1125 + 3200 + 4200 + 800 + 500 + 300 + 400 = $15350
        self.assertAlmostEqual(calculation["total_cost"], 15350.0, delta=0.01)
        
        # Total revenue (bedding sale) = $600
        self.assertAlmostEqual(calculation["total_revenue"], 600.0, delta=0.01)
        
        # Net cost = 15350 - 600 = $14750
        # Net cost per kg = 14750 / 24800 = $0.59
        self.assertAlmostEqual(calculation["net_cost_per_kg"], 0.59, delta=0.01)
        
        # Verify percentages sum to 100%
        total_percentage = (
            cost_breakdown["chick_cost_percent"] +
            cost_breakdown["pre_starter_cost_percent"] +
            cost_breakdown["starter_cost_percent"] +
            cost_breakdown["growth_cost_percent"] +
            cost_breakdown["final_cost_percent"] +
            cost_breakdown["medicine_cost_percent"] +
            cost_breakdown["miscellaneous_cost_percent"] +
            cost_breakdown["cost_variations_percent"] +
            cost_breakdown["sawdust_bedding_cost_percent"]
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
        
        # Check for bedding revenue insight
        bedding_insight = next((i for i in insights if "bedding sale revenue" in i.lower()), None)
        self.assertIsNotNone(bedding_insight)
        
        # Check for export file insight
        export_insight = next((i for i in insights if "batch report exported" in i.lower()), None)
        self.assertIsNotNone(export_insight)
        
        # Extract filename from export insight for later tests
        self.export_filename = export_insight.split("as: ")[1].strip()
        
        # Verify handler was created
        response = requests.get(f"{API_URL}/handlers")
        self.assertEqual(response.status_code, 200)
        handlers = response.json()
        self.assertIn("John Smith", handlers)

    def test_duplicate_batch_id_prevention(self):
        """Test that duplicate batch IDs are prevented"""
        # Create a batch with a specific ID
        payload = {
            "batch_id": "BATCH-DUPLICATE-TEST",
            "shed_number": "SHED-B2",
            "handler_name": "Jane Doe",
            "initial_chicks": 5000,
            "chick_cost_per_unit": 0.45,
            "pre_starter_feed": {"consumption_kg": 250, "cost_per_kg": 0.65},
            "starter_feed": {"consumption_kg": 1250, "cost_per_kg": 0.45},
            "growth_feed": {"consumption_kg": 4000, "cost_per_kg": 0.40},
            "final_feed": {"consumption_kg": 6000, "cost_per_kg": 0.35},
            "medicine_costs": 400,
            "miscellaneous_costs": 250,
            "cost_variations": 150,
            "sawdust_bedding_cost": 200,
            "chicken_bedding_sale_revenue": 300,
            "chicks_died": 125,
            "removal_batches": [
                {"quantity": 4500, "total_weight_kg": 11250, "age_days": 45}
            ]
        }
        
        # First submission should succeed
        response = requests.post(f"{API_URL}/calculate", json=payload)
        self.assertEqual(response.status_code, 200)
        
        # Second submission with same batch_id should fail
        response = requests.post(f"{API_URL}/calculate", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("already exists", response.text)
        
    def test_handler_performance_calculation(self):
        """Test handler performance calculation with multiple batches"""
        # Create first batch for handler
        handler_name = f"Test Handler {uuid.uuid4().hex[:8]}"
        
        # First batch with good performance
        payload1 = {
            "batch_id": f"BATCH-PERF-1-{uuid.uuid4().hex[:8]}",
            "shed_number": "SHED-P1",
            "handler_name": handler_name,
            "initial_chicks": 10000,
            "chick_cost_per_unit": 0.45,
            "pre_starter_feed": {"consumption_kg": 500, "cost_per_kg": 0.65},
            "starter_feed": {"consumption_kg": 2500, "cost_per_kg": 0.45},
            "growth_feed": {"consumption_kg": 8000, "cost_per_kg": 0.40},
            "final_feed": {"consumption_kg": 12000, "cost_per_kg": 0.35},
            "medicine_costs": 800,
            "miscellaneous_costs": 500,
            "cost_variations": 300,
            "sawdust_bedding_cost": 400,
            "chicken_bedding_sale_revenue": 600,
            "chicks_died": 250,  # 2.5% mortality
            "removal_batches": [
                {"quantity": 9500, "total_weight_kg": 24800, "age_days": 45}
            ]
        }
        
        # Second batch with different performance
        payload2 = {
            "batch_id": f"BATCH-PERF-2-{uuid.uuid4().hex[:8]}",
            "shed_number": "SHED-P2",
            "handler_name": handler_name,
            "initial_chicks": 8000,
            "chick_cost_per_unit": 0.45,
            "pre_starter_feed": {"consumption_kg": 400, "cost_per_kg": 0.65},
            "starter_feed": {"consumption_kg": 2000, "cost_per_kg": 0.45},
            "growth_feed": {"consumption_kg": 6400, "cost_per_kg": 0.40},
            "final_feed": {"consumption_kg": 9600, "cost_per_kg": 0.35},
            "medicine_costs": 640,
            "miscellaneous_costs": 400,
            "cost_variations": 240,
            "sawdust_bedding_cost": 320,
            "chicken_bedding_sale_revenue": 480,
            "chicks_died": 400,  # 5% mortality
            "removal_batches": [
                {"quantity": 7400, "total_weight_kg": 18500, "age_days": 48}
            ]
        }
        
        # Submit both batches
        response1 = requests.post(f"{API_URL}/calculate", json=payload1)
        self.assertEqual(response1.status_code, 200)
        
        response2 = requests.post(f"{API_URL}/calculate", json=payload2)
        self.assertEqual(response2.status_code, 200)
        
        # Get handler performance
        response = requests.get(f"{API_URL}/handlers/{handler_name}/performance")
        self.assertEqual(response.status_code, 200)
        
        performance = response.json()
        
        # Verify handler performance data
        self.assertEqual(performance["handler_name"], handler_name)
        self.assertEqual(performance["total_batches"], 2)
        self.assertEqual(performance["total_chicks_processed"], 18000)  # 10000 + 8000
        
        # Verify averages
        # FCR: (0.93 + 1.0) / 2 = 0.965
        # Mortality: (2.5 + 5.0) / 2 = 3.75
        # Daily gain: (0.059 + 0.054) / 2 = 0.0565
        # Cost per kg: (0.59 + 0.64) / 2 = 0.615
        self.assertAlmostEqual(performance["avg_feed_conversion_ratio"], 0.97, delta=0.1)
        self.assertAlmostEqual(performance["avg_mortality_rate"], 3.75, delta=0.1)
        self.assertAlmostEqual(performance["avg_daily_weight_gain"], 0.057, delta=0.01)
        
        # Verify performance score calculation
        # FCR score: (2.8 - 0.97) / (2.8 - 1.6) * 100 = 152.5 (capped at 100)
        # Mortality score: (12 - 3.75) / (12 - 3) * 100 = 91.7
        # Daily gain score: (0.057 - 0.045) / (0.065 - 0.045) * 100 = 60
        # Performance score = 100 * 0.35 + 91.7 * 0.35 + 60 * 0.30 = 85.1
        self.assertGreaterEqual(performance["performance_score"], 80)
        
        # Test handlers ranking endpoint
        response = requests.get(f"{API_URL}/handlers/performance")
        self.assertEqual(response.status_code, 200)
        
        performances = response.json()
        self.assertGreater(len(performances), 0)
        
        # Verify our handler is in the list
        handler_in_list = any(p["handler_name"] == handler_name for p in performances)
        self.assertTrue(handler_in_list)
        
    def test_net_cost_calculation(self):
        """Test net cost calculation with bedding revenue"""
        # Create a batch with significant bedding revenue
        payload = {
            "batch_id": f"BATCH-COST-{uuid.uuid4().hex[:8]}",
            "shed_number": "SHED-C1",
            "handler_name": "Cost Tester",
            "initial_chicks": 10000,
            "chick_cost_per_unit": 0.45,
            "pre_starter_feed": {"consumption_kg": 500, "cost_per_kg": 0.65},
            "starter_feed": {"consumption_kg": 2500, "cost_per_kg": 0.45},
            "growth_feed": {"consumption_kg": 8000, "cost_per_kg": 0.40},
            "final_feed": {"consumption_kg": 12000, "cost_per_kg": 0.35},
            "medicine_costs": 800,
            "miscellaneous_costs": 500,
            "cost_variations": 300,
            "sawdust_bedding_cost": 400,
            "chicken_bedding_sale_revenue": 1500,  # Significant revenue
            "chicks_died": 250,
            "removal_batches": [
                {"quantity": 9500, "total_weight_kg": 24800, "age_days": 45}
            ]
        }
        
        response = requests.post(f"{API_URL}/calculate", json=payload)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        calculation = data["calculation"]
        
        # Total cost = 4500 + 325 + 1125 + 3200 + 4200 + 800 + 500 + 300 + 400 = $15350
        self.assertAlmostEqual(calculation["total_cost"], 15350.0, delta=0.01)
        
        # Total revenue = $1500
        self.assertAlmostEqual(calculation["total_revenue"], 1500.0, delta=0.01)
        
        # Net cost = 15350 - 1500 = $13850
        # Net cost per kg = 13850 / 24800 = $0.56
        self.assertAlmostEqual(calculation["net_cost_per_kg"], 0.56, delta=0.01)
        
        # Verify bedding revenue insight
        insights = data["insights"]
        bedding_insight = next((i for i in insights if "bedding sale revenue" in i.lower()), None)
        self.assertIsNotNone(bedding_insight)
        
        # Revenue impact = (1500 / 15350) * 100 = 9.8%
        self.assertIn("9.8%", bedding_insight)
        
    def test_export_file_generation(self):
        """Test export file generation and download"""
        # Use the export filename from the complete farm scenario test
        if hasattr(self, 'export_filename'):
            response = requests.get(f"{API_URL}/export/{self.export_filename}")
            self.assertEqual(response.status_code, 200)
            
            # Verify content type is JSON
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            
            # Verify file content
            data = response.json()
            self.assertIn("batch_info", data)
            self.assertIn("performance_metrics", data)
            self.assertIn("production_data", data)
            self.assertIn("financial_summary", data)
            self.assertIn("removal_batches", data)
            
            # Verify batch info
            self.assertEqual(data["batch_info"]["batch_id"], self.unique_batch_id)
            self.assertEqual(data["batch_info"]["shed_number"], "SHED-A1")
            self.assertEqual(data["batch_info"]["handler_name"], "John Smith")
            
            # Verify performance metrics
            self.assertAlmostEqual(data["performance_metrics"]["feed_conversion_ratio"], 0.93, delta=0.01)
            self.assertAlmostEqual(data["performance_metrics"]["mortality_rate_percent"], 2.5, delta=0.01)
            
            # Verify financial summary
            self.assertAlmostEqual(data["financial_summary"]["total_cost"], 15350.0, delta=0.01)
            self.assertAlmostEqual(data["financial_summary"]["total_revenue"], 600.0, delta=0.01)
            self.assertAlmostEqual(data["financial_summary"]["net_cost_per_kg"], 0.59, delta=0.01)
        else:
            self.skipTest("Export filename not available from previous test")
            
    def test_sheds_endpoint(self):
        """Test the sheds endpoint"""
        response = requests.get(f"{API_URL}/sheds")
        self.assertEqual(response.status_code, 200)
        
        sheds = response.json()
        self.assertIsInstance(sheds, list)
        
        # Verify our test sheds are in the list
        self.assertIn("SHED-A1", sheds)
        
    def test_batch_details_endpoint(self):
        """Test the batch details endpoint"""
        # Get details for our test batch
        response = requests.get(f"{API_URL}/batches/{self.unique_batch_id}")
        self.assertEqual(response.status_code, 200)
        
        batch = response.json()
        self.assertEqual(batch["input_data"]["batch_id"], self.unique_batch_id)
        self.assertEqual(batch["input_data"]["shed_number"], "SHED-A1")
        self.assertEqual(batch["input_data"]["handler_name"], "John Smith")
        
        # Test with non-existent batch ID
        response = requests.get(f"{API_URL}/batches/non-existent-batch")
        self.assertEqual(response.status_code, 404)

if __name__ == "__main__":
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
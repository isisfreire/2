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

class BroilerCalculatorAPITest(unittest.TestCase):
    """Test suite for the Broiler Chicken Cost Calculator API"""

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
        self.assertEqual(data["message"], "Broiler Chicken Cost Calculator API")

    def test_normal_scenario(self):
        """Test normal calculation scenario with standard values"""
        # Normal scenario: 1000 chicks, $0.45/chick, 3500kg feed, $0.35/kg feed, 
        # 50 died, 2.5kg final weight, $200 other costs, $4.50 revenue/kg
        payload = {
            "initial_chicks": 1000,
            "chick_cost_per_unit": 0.45,
            "total_feed_consumed_kg": 3500,
            "feed_cost_per_kg": 0.35,
            "chicks_died": 50,
            "final_weight_per_chick_kg": 2.5,
            "other_costs": 200,
            "revenue_per_kg": 4.50
        }
        
        response = requests.post(f"{API_URL}/calculate", json=payload)
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        calculation = data["calculation"]
        insights = data["insights"]
        
        # Verify calculations
        self.assertEqual(calculation["surviving_chicks"], 950)
        self.assertEqual(calculation["total_weight_produced_kg"], 2375.0)
        
        # FCR should be around 1.47 (3500 / 2375)
        self.assertAlmostEqual(calculation["feed_conversion_ratio"], 1.47, delta=0.01)
        
        # Mortality rate should be 5%
        self.assertAlmostEqual(calculation["mortality_rate_percent"], 5.0, delta=0.01)
        
        # Total cost = (1000 * 0.45) + (3500 * 0.35) + 200 = $1675
        self.assertAlmostEqual(calculation["total_cost"], 1675.0, delta=0.01)
        
        # Cost per kg = 1675 / 2375 = $0.705
        self.assertAlmostEqual(calculation["cost_per_kg"], 0.71, delta=0.01)
        
        # Total revenue = 2375 * 4.50 = $10,687.50
        self.assertAlmostEqual(calculation["total_revenue"], 10687.5, delta=0.01)
        
        # Profit = 10687.50 - 1675 = $9,012.50
        self.assertAlmostEqual(calculation["profit_loss"], 9012.5, delta=0.01)
        
        # Verify insights are generated
        self.assertTrue(len(insights) >= 4)
        
        # Check for specific insights based on the values
        fcr_insight = next((i for i in insights if "feed conversion ratio" in i.lower()), None)
        self.assertIsNotNone(fcr_insight)
        self.assertTrue("excellent" in fcr_insight.lower())
        
        mortality_insight = next((i for i in insights if "mortality rate" in i.lower()), None)
        self.assertIsNotNone(mortality_insight)
        self.assertTrue("good" in mortality_insight.lower())

    def test_zero_mortality(self):
        """Test edge case with zero mortality"""
        payload = {
            "initial_chicks": 1000,
            "chick_cost_per_unit": 0.45,
            "total_feed_consumed_kg": 3500,
            "feed_cost_per_kg": 0.35,
            "chicks_died": 0,
            "final_weight_per_chick_kg": 2.5,
            "other_costs": 200,
            "revenue_per_kg": 4.50
        }
        
        response = requests.post(f"{API_URL}/calculate", json=payload)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        calculation = data["calculation"]
        insights = data["insights"]
        
        # Verify calculations with zero mortality
        self.assertEqual(calculation["surviving_chicks"], 1000)
        self.assertEqual(calculation["mortality_rate_percent"], 0.0)
        
        # Check for specific insights based on zero mortality
        mortality_insight = next((i for i in insights if "mortality rate" in i.lower()), None)
        self.assertIsNotNone(mortality_insight)
        self.assertTrue("excellent" in mortality_insight.lower())

    def test_high_mortality(self):
        """Test edge case with high mortality (>20%)"""
        payload = {
            "initial_chicks": 1000,
            "chick_cost_per_unit": 0.45,
            "total_feed_consumed_kg": 3500,
            "feed_cost_per_kg": 0.35,
            "chicks_died": 250,  # 25% mortality
            "final_weight_per_chick_kg": 2.5,
            "other_costs": 200,
            "revenue_per_kg": 4.50
        }
        
        response = requests.post(f"{API_URL}/calculate", json=payload)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        calculation = data["calculation"]
        insights = data["insights"]
        
        # Verify calculations with high mortality
        self.assertEqual(calculation["surviving_chicks"], 750)
        self.assertEqual(calculation["mortality_rate_percent"], 25.0)
        
        # Check for specific insights based on high mortality
        mortality_insight = next((i for i in insights if "mortality rate" in i.lower()), None)
        self.assertIsNotNone(mortality_insight)
        self.assertTrue("high" in mortality_insight.lower())

    def test_good_fcr(self):
        """Test edge case with very good FCR (<1.5)"""
        payload = {
            "initial_chicks": 1000,
            "chick_cost_per_unit": 0.45,
            "total_feed_consumed_kg": 1500,  # Lower feed consumption
            "feed_cost_per_kg": 0.35,
            "chicks_died": 50,
            "final_weight_per_chick_kg": 2.5,
            "other_costs": 200,
            "revenue_per_kg": 4.50
        }
        
        response = requests.post(f"{API_URL}/calculate", json=payload)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        calculation = data["calculation"]
        insights = data["insights"]
        
        # FCR should be around 0.63 (1500 / 2375)
        self.assertLess(calculation["feed_conversion_ratio"], 1.5)
        
        # Check for specific insights based on good FCR
        fcr_insight = next((i for i in insights if "feed conversion ratio" in i.lower()), None)
        self.assertIsNotNone(fcr_insight)
        self.assertTrue("excellent" in fcr_insight.lower())

    def test_poor_fcr(self):
        """Test edge case with poor FCR (>3.0)"""
        payload = {
            "initial_chicks": 1000,
            "chick_cost_per_unit": 0.45,
            "total_feed_consumed_kg": 7500,  # Higher feed consumption
            "feed_cost_per_kg": 0.35,
            "chicks_died": 50,
            "final_weight_per_chick_kg": 2.5,
            "other_costs": 200,
            "revenue_per_kg": 4.50
        }
        
        response = requests.post(f"{API_URL}/calculate", json=payload)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        calculation = data["calculation"]
        insights = data["insights"]
        
        # FCR should be around 3.16 (7500 / 2375)
        self.assertGreater(calculation["feed_conversion_ratio"], 3.0)
        
        # Check for specific insights based on poor FCR
        fcr_insight = next((i for i in insights if "feed conversion ratio" in i.lower()), None)
        self.assertIsNotNone(fcr_insight)
        self.assertTrue("poor" in fcr_insight.lower())

    def test_validation_negative_values(self):
        """Test validation for negative values"""
        # Test negative initial chicks
        payload = {
            "initial_chicks": -100,
            "chick_cost_per_unit": 0.45,
            "total_feed_consumed_kg": 3500,
            "feed_cost_per_kg": 0.35,
            "chicks_died": 50,
            "final_weight_per_chick_kg": 2.5,
            "other_costs": 200,
            "revenue_per_kg": 4.50
        }
        
        response = requests.post(f"{API_URL}/calculate", json=payload)
        self.assertEqual(response.status_code, 400)
        
        # Test negative feed consumption
        payload = {
            "initial_chicks": 1000,
            "chick_cost_per_unit": 0.45,
            "total_feed_consumed_kg": -100,
            "feed_cost_per_kg": 0.35,
            "chicks_died": 50,
            "final_weight_per_chick_kg": 2.5,
            "other_costs": 200,
            "revenue_per_kg": 4.50
        }
        
        response = requests.post(f"{API_URL}/calculate", json=payload)
        self.assertEqual(response.status_code, 400)
        
        # Test negative final weight
        payload = {
            "initial_chicks": 1000,
            "chick_cost_per_unit": 0.45,
            "total_feed_consumed_kg": 3500,
            "feed_cost_per_kg": 0.35,
            "chicks_died": 50,
            "final_weight_per_chick_kg": -1.5,
            "other_costs": 200,
            "revenue_per_kg": 4.50
        }
        
        response = requests.post(f"{API_URL}/calculate", json=payload)
        self.assertEqual(response.status_code, 400)

    def test_validation_chicks_died_greater_than_initial(self):
        """Test validation for chicks died > initial chicks"""
        payload = {
            "initial_chicks": 1000,
            "chick_cost_per_unit": 0.45,
            "total_feed_consumed_kg": 3500,
            "feed_cost_per_kg": 0.35,
            "chicks_died": 1200,  # More than initial
            "final_weight_per_chick_kg": 2.5,
            "other_costs": 200,
            "revenue_per_kg": 4.50
        }
        
        response = requests.post(f"{API_URL}/calculate", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Chicks died cannot be more than initial chicks", response.text)

    def test_validation_zero_feed_consumption(self):
        """Test validation for zero feed consumption"""
        payload = {
            "initial_chicks": 1000,
            "chick_cost_per_unit": 0.45,
            "total_feed_consumed_kg": 0,  # Zero feed
            "feed_cost_per_kg": 0.35,
            "chicks_died": 50,
            "final_weight_per_chick_kg": 2.5,
            "other_costs": 200,
            "revenue_per_kg": 4.50
        }
        
        response = requests.post(f"{API_URL}/calculate", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Feed consumed must be greater than 0", response.text)

    def test_get_calculations(self):
        """Test retrieving calculation history"""
        # First, create a calculation to ensure there's at least one in the database
        payload = {
            "initial_chicks": 1000,
            "chick_cost_per_unit": 0.45,
            "total_feed_consumed_kg": 3500,
            "feed_cost_per_kg": 0.35,
            "chicks_died": 50,
            "final_weight_per_chick_kg": 2.5,
            "other_costs": 200,
            "revenue_per_kg": 4.50
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
            self.assertIn("initial_chicks", calculation)
            self.assertIn("feed_conversion_ratio", calculation)
            self.assertIn("mortality_rate_percent", calculation)
            self.assertIn("cost_per_kg", calculation)
            self.assertIn("profit_loss", calculation)

if __name__ == "__main__":
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
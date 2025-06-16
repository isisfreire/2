import requests
import json
import unittest
import os
from dotenv import load_dotenv
import sys
import time
import uuid
from datetime import datetime

# Load environment variables from frontend .env file to get the backend URL
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

class AgeRestrictionRemovalTest(unittest.TestCase):
    """Test suite for verifying the removal of age restrictions in the broiler chicken application"""

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
        self.unique_batch_id = f"AGE-TEST-{uuid.uuid4().hex[:8]}"
        
    def create_test_batch(self, age_days):
        """Helper method to create a test batch with a specific age"""
        test_batch_id = f"AGE-TEST-{age_days}-{uuid.uuid4().hex[:8]}"
        
        payload = {
            # Batch identification
            "batch_id": test_batch_id,
            "shed_number": "TEST-SHED",
            "handler_name": "Test Handler",
            
            # Batch dates
            "entry_date": "2024-01-01T00:00:00Z",
            "exit_date": "2024-03-01T00:00:00Z",
            
            # Basic data
            "initial_chicks": 5000,
            "chick_cost_per_unit": 0.50,
            
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
            
            # Enhanced costs
            "medicine_costs": 400,
            "miscellaneous_costs": 250,
            "cost_variations": 150,
            "sawdust_bedding_cost": 200,
            "chicken_bedding_sale_revenue": 300,
            
            # Mortality
            "chicks_died": 100,
            
            # Removal batches with the specified age
            "removal_batches": [
                {"quantity": 4900, "total_weight_kg": 9800, "age_days": age_days}
            ]
        }
        
        return test_batch_id, payload

    def test_low_age_acceptance(self):
        """Test that ages below the previous 35-day minimum are now accepted"""
        # Test with age = 20 days
        test_batch_id, payload = self.create_test_batch(20)
        
        # Submit the calculation
        response = requests.post(f"{API_URL}/calculate", json=payload)
        self.assertEqual(response.status_code, 200, f"Failed to accept age of 20 days: {response.text}")
        
        data = response.json()
        calculation = data["calculation"]
        
        # Verify batch was created with the correct age
        self.assertEqual(calculation["input_data"]["removal_batches"][0]["age_days"], 20)
        
        # Test with age = 30 days
        test_batch_id, payload = self.create_test_batch(30)
        
        # Submit the calculation
        response = requests.post(f"{API_URL}/calculate", json=payload)
        self.assertEqual(response.status_code, 200, f"Failed to accept age of 30 days: {response.text}")
        
        data = response.json()
        calculation = data["calculation"]
        
        # Verify batch was created with the correct age
        self.assertEqual(calculation["input_data"]["removal_batches"][0]["age_days"], 30)

    def test_high_age_acceptance(self):
        """Test that ages above the previous 60-day maximum are now accepted"""
        # Test with age = 70 days
        test_batch_id, payload = self.create_test_batch(70)
        
        # Submit the calculation
        response = requests.post(f"{API_URL}/calculate", json=payload)
        self.assertEqual(response.status_code, 200, f"Failed to accept age of 70 days: {response.text}")
        
        data = response.json()
        calculation = data["calculation"]
        
        # Verify batch was created with the correct age
        self.assertEqual(calculation["input_data"]["removal_batches"][0]["age_days"], 70)
        
        # Test with age = 80 days
        test_batch_id, payload = self.create_test_batch(80)
        
        # Submit the calculation
        response = requests.post(f"{API_URL}/calculate", json=payload)
        self.assertEqual(response.status_code, 200, f"Failed to accept age of 80 days: {response.text}")
        
        data = response.json()
        calculation = data["calculation"]
        
        # Verify batch was created with the correct age
        self.assertEqual(calculation["input_data"]["removal_batches"][0]["age_days"], 80)

    def test_edge_cases(self):
        """Test edge cases for age validation"""
        # Test with age = 1 day
        test_batch_id, payload = self.create_test_batch(1)
        
        # Submit the calculation
        response = requests.post(f"{API_URL}/calculate", json=payload)
        self.assertEqual(response.status_code, 200, f"Failed to accept age of 1 day: {response.text}")
        
        data = response.json()
        calculation = data["calculation"]
        
        # Verify batch was created with the correct age
        self.assertEqual(calculation["input_data"]["removal_batches"][0]["age_days"], 1)
        
        # Test with age = 100 days
        test_batch_id, payload = self.create_test_batch(100)
        
        # Submit the calculation
        response = requests.post(f"{API_URL}/calculate", json=payload)
        self.assertEqual(response.status_code, 200, f"Failed to accept age of 100 days: {response.text}")
        
        data = response.json()
        calculation = data["calculation"]
        
        # Verify batch was created with the correct age
        self.assertEqual(calculation["input_data"]["removal_batches"][0]["age_days"], 100)
        
        # Test with age = 365 days (extreme case)
        test_batch_id, payload = self.create_test_batch(365)
        
        # Submit the calculation
        response = requests.post(f"{API_URL}/calculate", json=payload)
        self.assertEqual(response.status_code, 200, f"Failed to accept age of 365 days: {response.text}")
        
        data = response.json()
        calculation = data["calculation"]
        
        # Verify batch was created with the correct age
        self.assertEqual(calculation["input_data"]["removal_batches"][0]["age_days"], 365)

    def test_multiple_removal_batches_with_varied_ages(self):
        """Test that multiple removal batches with varied ages are accepted"""
        test_batch_id = f"MULTI-AGE-TEST-{uuid.uuid4().hex[:8]}"
        
        payload = {
            # Batch identification
            "batch_id": test_batch_id,
            "shed_number": "TEST-SHED",
            "handler_name": "Test Handler",
            
            # Batch dates
            "entry_date": "2024-01-01T00:00:00Z",
            "exit_date": "2024-03-01T00:00:00Z",
            
            # Basic data
            "initial_chicks": 5000,
            "chick_cost_per_unit": 0.50,
            
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
            
            # Enhanced costs
            "medicine_costs": 400,
            "miscellaneous_costs": 250,
            "cost_variations": 150,
            "sawdust_bedding_cost": 200,
            "chicken_bedding_sale_revenue": 300,
            
            # Mortality
            "chicks_died": 100,
            
            # Multiple removal batches with varied ages
            "removal_batches": [
                {"quantity": 1000, "total_weight_kg": 1500, "age_days": 20},
                {"quantity": 1000, "total_weight_kg": 2000, "age_days": 30},
                {"quantity": 1000, "total_weight_kg": 2500, "age_days": 45},
                {"quantity": 1000, "total_weight_kg": 3000, "age_days": 70},
                {"quantity": 900, "total_weight_kg": 3000, "age_days": 100}
            ]
        }
        
        # Submit the calculation
        response = requests.post(f"{API_URL}/calculate", json=payload)
        self.assertEqual(response.status_code, 200, f"Failed to accept multiple removal batches with varied ages: {response.text}")
        
        data = response.json()
        calculation = data["calculation"]
        
        # Verify all removal batches were created with the correct ages
        removal_batches = calculation["input_data"]["removal_batches"]
        self.assertEqual(len(removal_batches), 5)
        self.assertEqual(removal_batches[0]["age_days"], 20)
        self.assertEqual(removal_batches[1]["age_days"], 30)
        self.assertEqual(removal_batches[2]["age_days"], 45)
        self.assertEqual(removal_batches[3]["age_days"], 70)
        self.assertEqual(removal_batches[4]["age_days"], 100)
        
        # Verify weighted average age calculation
        # (1000*20 + 1000*30 + 1000*45 + 1000*70 + 900*100) / 4900 = 51.84
        expected_weighted_avg_age = (1000*20 + 1000*30 + 1000*45 + 1000*70 + 900*100) / 4900
        self.assertAlmostEqual(calculation["weighted_average_age"], expected_weighted_avg_age, delta=0.1)

    def test_negative_age_rejection(self):
        """Test that negative ages are still rejected"""
        test_batch_id, payload = self.create_test_batch(-10)
        
        # Submit the calculation
        response = requests.post(f"{API_URL}/calculate", json=payload)
        self.assertEqual(response.status_code, 400, "Negative age should be rejected")
        
    def test_zero_age_rejection(self):
        """Test that zero age is still rejected"""
        test_batch_id, payload = self.create_test_batch(0)
        
        # Submit the calculation
        response = requests.post(f"{API_URL}/calculate", json=payload)
        self.assertEqual(response.status_code, 400, "Zero age should be rejected")

if __name__ == "__main__":
    # Run the tests
    print("Starting Age Restriction Removal Tests...")
    print(f"API URL: {API_URL}")
    
    # Run the tests
    unittest.main()
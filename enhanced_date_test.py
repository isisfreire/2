import requests
import json
import unittest
import os
from dotenv import load_dotenv
import sys
import time
import uuid
from datetime import datetime, timedelta
import re

# Load environment variables from frontend .env file to get the backend URL
load_dotenv('/app/frontend/.env')
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
API_URL = f"{BACKEND_URL}/api"

class EnhancedDateHandlingTest(unittest.TestCase):
    """Test suite for the Enhanced Date Handling and PDF Generation features"""

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
        self.unique_batch_id = f"TEST-BATCH-{uuid.uuid4().hex[:8]}"
        
    def test_enhanced_batch_creation_with_dates(self):
        """
        Test creating a new batch calculation with dates:
        - Batch ID: "TEST-BATCH-2024-001" 
        - Shed: "SHED-A1"
        - Handler: "John Smith"
        - Entry date: "2024-01-15"
        - Exit date: "2024-03-01" 
        - Initial chicks: 10000
        - Chick cost: $0.45
        - Feed data for all phases
        - Mortality: 500 chicks
        - Multiple removal batches with different ages and weights
        """
        # Create a unique batch ID for this test
        test_batch_id = self.unique_batch_id
        
        # Calculate dates
        entry_date = "2024-01-15T00:00:00Z"
        exit_date = "2024-03-01T00:00:00Z"
        
        payload = {
            # Batch identification
            "batch_id": test_batch_id,
            "shed_number": "SHED-A1",
            "handler_name": "John Smith",
            
            # Batch dates
            "entry_date": entry_date,
            "exit_date": exit_date,
            
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
            "chicks_died": 500,
            
            # Removal batches with different ages
            "removal_batches": [
                {"quantity": 3000, "total_weight_kg": 6900, "age_days": 35},
                {"quantity": 6500, "total_weight_kg": 18200, "age_days": 50}
            ]
        }
        
        # Submit the calculation
        response = requests.post(f"{API_URL}/calculate", json=payload)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        calculation = data["calculation"]
        
        # Verify batch identification
        self.assertEqual(calculation["input_data"]["batch_id"], test_batch_id)
        self.assertEqual(calculation["input_data"]["shed_number"], "SHED-A1")
        self.assertEqual(calculation["input_data"]["handler_name"], "John Smith")
        
        # Verify dates were stored correctly
        self.assertEqual(calculation["input_data"]["entry_date"], entry_date)
        self.assertEqual(calculation["input_data"]["exit_date"], exit_date)
        
        # Verify viability calculation
        self.assertEqual(calculation["viability"], 9500)  # Sum of removal batch quantities
        self.assertEqual(calculation["surviving_chicks"], 9500)  # initial_chicks - chicks_died
        self.assertEqual(calculation["removed_chicks"], 9500)  # Sum of removal batch quantities
        self.assertEqual(calculation["missing_chicks"], 0)  # surviving_chicks - removed_chicks
        
        # Extract PDF filename from insights for later tests
        pdf_insight = next((i for i in data["insights"] if "PDF report exported" in i), None)
        self.assertIsNotNone(pdf_insight)
        self.pdf_filename = pdf_insight.split("as: ")[1].strip()
        
        return test_batch_id

    def test_date_validation(self):
        """
        Test that the backend properly handles:
        - Date formatting and parsing
        - Batch duration calculation
        - Date fields in the response
        """
        # Test with various date formats
        test_cases = [
            # ISO format
            {
                "entry_date": "2024-01-15T00:00:00Z",
                "exit_date": "2024-03-01T00:00:00Z",
                "expected_days": 46  # Jan 15 to Mar 1 = 46 days
            },
            # ISO format without time
            {
                "entry_date": "2024-01-15",
                "exit_date": "2024-03-01",
                "expected_days": 46
            },
            # Short date range
            {
                "entry_date": "2024-02-15T00:00:00Z",
                "exit_date": "2024-02-25T00:00:00Z",
                "expected_days": 10
            },
            # Long date range
            {
                "entry_date": "2024-01-01T00:00:00Z",
                "exit_date": "2024-04-30T00:00:00Z",
                "expected_days": 120
            }
        ]
        
        for i, test_case in enumerate(test_cases):
            # Create a unique batch ID for each test case
            test_batch_id = f"DATE-TEST-{i+1}-{uuid.uuid4().hex[:8]}"
            
            payload = {
                # Batch identification
                "batch_id": test_batch_id,
                "shed_number": "SHED-A1",
                "handler_name": "John Smith",
                
                # Batch dates
                "entry_date": test_case["entry_date"],
                "exit_date": test_case["exit_date"],
                
                # Basic data
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
                
                # Enhanced costs
                "medicine_costs": 400,
                "miscellaneous_costs": 250,
                "cost_variations": 150,
                "sawdust_bedding_cost": 200,
                "chicken_bedding_sale_revenue": 300,
                
                # Mortality
                "chicks_died": 250,
                
                # Removal batches
                "removal_batches": [
                    {"quantity": 4750, "total_weight_kg": 11875, "age_days": 45}
                ]
            }
            
            # Submit the calculation
            response = requests.post(f"{API_URL}/calculate", json=payload)
            self.assertEqual(response.status_code, 200, f"Failed for test case {i+1}")
            
            data = response.json()
            calculation = data["calculation"]
            
            # Verify dates were stored correctly
            self.assertIn(test_case["entry_date"].split("T")[0], calculation["input_data"]["entry_date"])
            self.assertIn(test_case["exit_date"].split("T")[0], calculation["input_data"]["exit_date"])
            
            # Get PDF filename from insights
            pdf_insight = next((i for i in data["insights"] if "PDF report exported" in i), None)
            self.assertIsNotNone(pdf_insight)
            pdf_filename = pdf_insight.split("as: ")[1].strip()
            
            # Download PDF file
            response = requests.get(f"{API_URL}/export/{pdf_filename}")
            self.assertEqual(response.status_code, 200)
            
            # Verify content type is PDF
            self.assertEqual(response.headers['Content-Type'], 'application/pdf')
            
            # Get batch details to verify duration calculation
            response = requests.get(f"{API_URL}/batches/{test_batch_id}")
            self.assertEqual(response.status_code, 200)
            
            batch = response.json()
            
            # Verify entry and exit dates
            self.assertIn(test_case["entry_date"].split("T")[0], batch["input_data"]["entry_date"])
            self.assertIn(test_case["exit_date"].split("T")[0], batch["input_data"]["exit_date"])

    def test_pdf_generation_with_dates(self):
        """
        Test that regenerated PDF reports include:
        - Entry and exit dates
        - Viability information
        - Batch duration calculation
        """
        # First create a batch to test with
        test_batch_id = f"PDF-TEST-{uuid.uuid4().hex[:8]}"
        
        payload = {
            "batch_id": test_batch_id,
            "shed_number": "SHED-PDF",
            "handler_name": "PDF Tester",
            "entry_date": "2024-02-01T00:00:00Z",
            "exit_date": "2024-03-15T00:00:00Z",
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
            "chicks_died": 400,
            "removal_batches": [
                {"quantity": 7600, "total_weight_kg": 19000, "age_days": 45}
            ]
        }
        
        # Submit the calculation
        response = requests.post(f"{API_URL}/calculate", json=payload)
        self.assertEqual(response.status_code, 200)
        
        # Regenerate PDF for the batch
        response = requests.get(f"{API_URL}/batches/{test_batch_id}/export-pdf")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        pdf_filename = data["filename"]
        
        # Download the PDF file
        response = requests.get(f"{API_URL}/export/{pdf_filename}")
        self.assertEqual(response.status_code, 200)
        
        # Verify content type is PDF
        self.assertEqual(response.headers['Content-Type'], 'application/pdf')
        
        # Get batch details to verify data
        response = requests.get(f"{API_URL}/batches/{test_batch_id}")
        self.assertEqual(response.status_code, 200)
        
        batch = response.json()
        
        # Verify entry and exit dates
        self.assertIn("2024-02-01", batch["input_data"]["entry_date"])
        self.assertIn("2024-03-15", batch["input_data"]["exit_date"])
        
        # Verify viability
        viability = batch["viability"]
        self.assertEqual(viability, 7600)  # Sum of removal batch quantities
        
        # Verify viability equals sum of removal batch quantities
        total_removed = sum(batch["quantity"] for batch in batch["input_data"]["removal_batches"])
        self.assertEqual(viability, total_removed)
        
        # Verify viability rate calculation
        viability_rate = (viability / batch["input_data"]["initial_chicks"]) * 100
        self.assertAlmostEqual(viability_rate, 95.0, delta=0.1)

    def test_data_retrieval_with_dates(self):
        """
        Test getting batch details and verify all new fields are present
        """
        # First create a batch to test with
        test_batch_id = f"RETRIEVAL-TEST-{uuid.uuid4().hex[:8]}"
        
        payload = {
            "batch_id": test_batch_id,
            "shed_number": "SHED-RETRIEVE",
            "handler_name": "Retrieval Tester",
            "entry_date": "2024-03-01T00:00:00Z",
            "exit_date": "2024-04-15T00:00:00Z",
            "initial_chicks": 6000,
            "chick_cost_per_unit": 0.45,
            "pre_starter_feed": {"consumption_kg": 300, "cost_per_kg": 0.65},
            "starter_feed": {"consumption_kg": 1500, "cost_per_kg": 0.45},
            "growth_feed": {"consumption_kg": 4800, "cost_per_kg": 0.40},
            "final_feed": {"consumption_kg": 7200, "cost_per_kg": 0.35},
            "medicine_costs": 480,
            "miscellaneous_costs": 300,
            "cost_variations": 180,
            "sawdust_bedding_cost": 240,
            "chicken_bedding_sale_revenue": 360,
            "chicks_died": 300,
            "removal_batches": [
                {"quantity": 5700, "total_weight_kg": 14250, "age_days": 45}
            ]
        }
        
        # Submit the calculation
        response = requests.post(f"{API_URL}/calculate", json=payload)
        self.assertEqual(response.status_code, 200)
        
        # Get batch details
        response = requests.get(f"{API_URL}/batches/{test_batch_id}")
        self.assertEqual(response.status_code, 200)
        
        batch = response.json()
        
        # Verify all required fields are present
        self.assertIn("entry_date", batch["input_data"])
        self.assertIn("exit_date", batch["input_data"])
        self.assertIn("viability", batch)
        
        # Verify dates
        self.assertIn("2024-03-01", batch["input_data"]["entry_date"])
        self.assertIn("2024-04-15", batch["input_data"]["exit_date"])
        
        # Verify viability calculation
        self.assertEqual(batch["viability"], 5700)
        
        # Verify all calculations are correct
        self.assertEqual(batch["surviving_chicks"], 5700)  # 6000 - 300
        self.assertEqual(batch["removed_chicks"], 5700)  # Sum of removal batch quantities
        self.assertEqual(batch["missing_chicks"], 0)  # 5700 - 5700
        
        # Verify weighted average age calculation
        self.assertAlmostEqual(batch["weighted_average_age"], 45.0, delta=0.1)

    def test_calculations_verification(self):
        """
        Verify that viability equals the sum of removal batch quantities
        """
        # Create a new batch with multiple removal batches
        test_batch_id = f"VIABILITY-TEST-{uuid.uuid4().hex[:8]}"
        
        entry_date = "2024-02-01T00:00:00Z"
        exit_date = "2024-03-15T00:00:00Z"
        
        payload = {
            # Batch identification
            "batch_id": test_batch_id,
            "shed_number": "SHED-V1",
            "handler_name": "Viability Tester",
            
            # Batch dates
            "entry_date": entry_date,
            "exit_date": exit_date,
            
            # Basic data
            "initial_chicks": 12000,
            "chick_cost_per_unit": 0.45,
            
            # 4 feed phases
            "pre_starter_feed": {
                "consumption_kg": 600,
                "cost_per_kg": 0.65
            },
            "starter_feed": {
                "consumption_kg": 3000,
                "cost_per_kg": 0.45
            },
            "growth_feed": {
                "consumption_kg": 9600,
                "cost_per_kg": 0.40
            },
            "final_feed": {
                "consumption_kg": 14400,
                "cost_per_kg": 0.35
            },
            
            # Enhanced costs
            "medicine_costs": 960,
            "miscellaneous_costs": 600,
            "cost_variations": 360,
            "sawdust_bedding_cost": 480,
            "chicken_bedding_sale_revenue": 720,
            
            # Mortality
            "chicks_died": 600,
            
            # Multiple removal batches with different ages
            "removal_batches": [
                {"quantity": 2000, "total_weight_kg": 4600, "age_days": 35},
                {"quantity": 3000, "total_weight_kg": 7500, "age_days": 42},
                {"quantity": 4000, "total_weight_kg": 11200, "age_days": 50},
                {"quantity": 2400, "total_weight_kg": 7200, "age_days": 55}
            ]
        }
        
        # Submit the calculation
        response = requests.post(f"{API_URL}/calculate", json=payload)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        calculation = data["calculation"]
        
        # Calculate expected values
        expected_surviving_chicks = 12000 - 600  # initial_chicks - chicks_died
        expected_removed_chicks = 2000 + 3000 + 4000 + 2400  # Sum of removal batch quantities
        expected_missing_chicks = expected_surviving_chicks - expected_removed_chicks
        
        # Verify calculations
        self.assertEqual(calculation["surviving_chicks"], expected_surviving_chicks)
        self.assertEqual(calculation["removed_chicks"], expected_removed_chicks)
        self.assertEqual(calculation["viability"], expected_removed_chicks)
        self.assertEqual(calculation["missing_chicks"], expected_missing_chicks)
        
        # Verify weighted average age calculation
        # (2000*35 + 3000*42 + 4000*50 + 2400*55) / 11400 = 46.18
        expected_weighted_avg_age = (2000*35 + 3000*42 + 4000*50 + 2400*55) / 11400
        self.assertAlmostEqual(calculation["weighted_average_age"], expected_weighted_avg_age, delta=0.1)
        
        # Verify viability rate
        viability_rate = (calculation["viability"] / calculation["input_data"]["initial_chicks"]) * 100
        expected_viability_rate = (expected_removed_chicks / 12000) * 100
        self.assertAlmostEqual(viability_rate, expected_viability_rate, delta=0.1)

if __name__ == "__main__":
    # Run the tests
    print("Starting Enhanced Date Handling and PDF Generation Tests...")
    print(f"API URL: {API_URL}")
    
    # Run the tests
    unittest.main()
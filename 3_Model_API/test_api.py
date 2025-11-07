"""
Test script for Fraud Detection API
Run this after starting the server to verify all endpoints work correctly.
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_root():
    """Test the root endpoint"""
    print("\n1️⃣  Testing GET / (root endpoint)...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200, "Root endpoint failed"
    print("✅ Root endpoint works!")


def test_predict_legitimate():
    """Test prediction with a legitimate transaction"""
    print("\n2️⃣  Testing POST /predict (legitimate transaction)...")
    transaction = {
        "transaction_id": "txn_test_001",
        "time_ind": datetime.now().isoformat(),
        "src_acc": "acc_alice",
        "dst_acc": "acc_bob",
        "amount": 150.0  # Low amount - should be legitimate
    }
    
    response = requests.post(f"{BASE_URL}/predict", json=transaction)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    
    assert response.status_code == 200, "Predict endpoint failed"
    assert "is_fraud" in result, "Missing is_fraud field"
    assert "fraud_probability" in result, "Missing fraud_probability field"
    print(f"✅ Prediction: {'FRAUD' if result['is_fraud'] else 'LEGITIMATE'} (prob: {result['fraud_probability']:.4f})")


def test_predict_fraudulent():
    """Test prediction with a suspicious transaction"""
    print("\n3️⃣  Testing POST /predict (suspicious transaction)...")
    transaction = {
        "transaction_id": "txn_test_002",
        "time_ind": datetime.now().isoformat(),
        "src_acc": "acc_charlie",
        "dst_acc": "acc_unknown",
        "amount": 15000.0  # High amount - likely fraud with mock model
    }
    
    response = requests.post(f"{BASE_URL}/predict", json=transaction)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    
    assert response.status_code == 200, "Predict endpoint failed"
    print(f"✅ Prediction: {'FRAUD' if result['is_fraud'] else 'LEGITIMATE'} (prob: {result['fraud_probability']:.4f})")


def test_get_frauds():
    """Test retrieving fraudulent transactions"""
    print("\n4️⃣  Testing GET /frauds...")
    response = requests.get(f"{BASE_URL}/frauds")
    print(f"Status: {response.status_code}")
    frauds = response.json()
    print(f"Found {len(frauds)} fraudulent transaction(s)")
    
    if frauds:
        print(f"Latest fraud: {json.dumps(frauds[-1], indent=2)}")
    
    assert response.status_code == 200, "Get frauds endpoint failed"
    print("✅ Get frauds endpoint works!")


def test_clear_frauds():
    """Test clearing fraud records"""
    print("\n5️⃣  Testing DELETE /frauds (clear all records)...")
    response = requests.delete(f"{BASE_URL}/frauds")
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    
    assert response.status_code == 200, "Clear frauds endpoint failed"
    print("✅ Clear frauds endpoint works!")


def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 Fraud Detection API Test Suite")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}")
    print("Make sure the server is running (python server.py)")
    print("=" * 60)
    
    try:
        test_root()
        test_predict_legitimate()
        test_predict_fraudulent()
        test_get_frauds()
        test_clear_frauds()
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to the API server.")
        print("Make sure the server is running: python server.py")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")


if __name__ == "__main__":
    main()

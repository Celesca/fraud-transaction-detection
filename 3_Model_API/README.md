# Fraud Detection REST API Service

A FastAPI-based REST API service for real-time fraud detection in financial transactions.

## 📋 Features

- **POST /predict**: Accept a transaction and return fraud prediction with probability score
- **GET /frauds**: Retrieve all transactions previously predicted as fraudulent
- **DELETE /frauds**: Clear all fraud records (useful for testing)
- **SQLite database**: Persistent storage for fraudulent transactions
- **Interactive API docs**: Auto-generated Swagger UI at `/docs`

---

## 🚀 Setup Instructions

Follow these step-by-step instructions to set up and run the fraud detection API service.

### Prerequisites

- Python 3.11 (recommended) or Python 3.9+
- pip (Python package installer)
- Virtual environment (`.venv` already created in project root)

---

### Step 1: Activate Virtual Environment

Navigate to the project root directory and activate the virtual environment:

**Windows (Command Prompt):**
```cmd
.venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

You should see `(.venv)` prefix in your terminal prompt.

---

### Step 2: Install Dependencies

Navigate to the `3_Model_Serving` directory and install required packages:

```cmd
cd 3_Model_Serving
pip install -r requirements.txt
```

Expected output: FastAPI, uvicorn, pydantic, and other dependencies installed successfully.

---

### Step 3: Run the API Server

Start the FastAPI development server:

```cmd
python server.py
```

Or using uvicorn directly:

```cmd
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
⚠️  Mock model loaded. Replace with actual trained model.
✅ Database initialized
📂 Database path: C:\Users\...\3_Model_Serving\frauds.db
```

The server is now running! 🎉

---

## 🧪 Testing the API

### Option 1: Interactive API Documentation (Recommended)

Open your browser and navigate to:

```
http://localhost:8000/docs
```

This opens the **Swagger UI** where you can:
- View all endpoints and their schemas
- Test endpoints directly in the browser
- See request/response examples

### Option 2: Using cURL (Command Line)

**Test the root endpoint:**
```cmd
curl http://localhost:8000/
```

**Predict fraud for a transaction:**
```cmd
curl -X POST "http://localhost:8000/predict" ^
  -H "Content-Type: application/json" ^
    -d "{\"time_ind\": \"2025-11-07T10:30:00\", \"src_acc\": \"acc_123\", \"dst_acc\": \"acc_456\", \"amount\": 7500.0}"
```

**Retrieve all fraudulent transactions:**
```cmd
curl http://localhost:8000/frauds
```

**Clear all fraud records:**
```cmd
curl -X DELETE http://localhost:8000/frauds
```

### Option 3: Using Python `requests` library

```python
import requests

# Predict endpoint
transaction = {
    "time_ind": "2025-11-07T14:20:00",
    "src_acc": "acc_789",
    "dst_acc": "acc_999",
    "amount": 12000.0
}

response = requests.post("http://localhost:8000/predict", json=transaction)
print(response.json())

# Get frauds endpoint
response = requests.get("http://localhost:8000/frauds")
print(response.json())
```

---

## 🔧 Integrating Your Trained Model

The current implementation uses a **mock model** that flags transactions with `amount > 5000` as fraud.

### To replace with your actual model:

1. **Train and save your model** (e.g., in the `2_Model_Training` directory):
   ```python
   import joblib
   # After training your model (e.g., sklearn, XGBoost, etc.)
   joblib.dump(model, '3_Model_Serving/fraud_model.pkl')
   ```

2. **Update the `FraudDetectionModel` class in `server.py`**:

   ```python
   import joblib
   import numpy as np
   
   class FraudDetectionModel:
       def __init__(self):
           # Load your trained model
           self.model = joblib.load('fraud_model.pkl')
           print("✅ Trained model loaded successfully")
       
       def predict(self, transaction: Transaction) -> tuple[bool, float]:
           # Extract features
           features = self._extract_features(transaction)
           
           # Get prediction
           probability = self.model.predict_proba(features)[0][1]
           is_fraud = probability >= 0.5
           
           return is_fraud, probability
       
       def _extract_features(self, transaction: Transaction):
           # Implement your feature engineering pipeline
           # Example: parse time, encode categoricals, scale, etc.
           features = [
               # Extract hour from time_ind
               # Encode src_acc, dst_acc
               transaction.amount,
               # ... other features
           ]
           return np.array(features).reshape(1, -1)
   ```

3. **Update the `Transaction` schema** to include all features your model requires.

4. **Restart the server** and test with real predictions.

---

## 📂 Project Structure

```
3_Model_Serving/
├── server.py              # Main FastAPI application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── frauds.db             # SQLite database (auto-created)
└── fraud_model.pkl       # Your trained model (add this)
```

---

## 📊 Database Schema

The SQLite database (`frauds.db`) stores fraudulent transactions with the following schema:

| Column             | Type    | Description                              |
|--------------------|---------|------------------------------------------|
| id                 | INTEGER | Primary key (auto-increment)             |
| transaction_data   | TEXT    | Full transaction JSON                    |
| fraud_probability  | REAL    | Fraud probability score (0.0 to 1.0)     |
| prediction_time    | TEXT    | ISO timestamp of prediction              |

---

## 🛠️ Advanced Configuration

### Change Server Port

Edit `server.py` at the bottom:
```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True)  # Changed to 8080
```

### Production Deployment

For production, use a production-grade ASGI server:

```cmd
pip install gunicorn
gunicorn server:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Environment Variables

For sensitive configuration (DB paths, model paths), use environment variables:

```python
import os
DB_PATH = os.getenv("DB_PATH", "frauds.db")
MODEL_PATH = os.getenv("MODEL_PATH", "fraud_model.pkl")
```

---

## ✅ Troubleshooting

**Issue: Port 8000 already in use**
- Solution: Change the port in `server.py` or kill the process using port 8000

**Issue: ModuleNotFoundError**
- Solution: Ensure virtual environment is activated and dependencies are installed

**Issue: Database locked**
- Solution: Close any other connections to `frauds.db` or delete the file to reset

**Issue: Model file not found**
- Solution: Ensure your trained model file is in the `3_Model_Serving` directory

---

## 📝 Next Steps

1. ✅ Run the server and test with mock predictions
2. 🔄 Train your fraud detection model (in `2_Model_Training`)
3. 🔧 Replace the mock model with your trained model
4. 🧪 Test with realistic transaction data
5. 🚀 Deploy to production environment
6. 📊 Monitor fraud predictions and retrain periodically

---

## 📞 Support

For issues or questions, refer to:
- FastAPI documentation: https://fastapi.tiangolo.com/
- SQLite documentation: https://www.sqlite.org/docs.html
- Project repository issues

---

**Happy fraud detecting! 🚨**

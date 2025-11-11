# Part 3: Fraud Detection REST API Service

A FastAPI-based REST API service for real-time fraud detection in financial transactions.


## Installation (with Docker) 🐳

The easiest way to run the API is using Docker, which packages all dependencies and the application into a container.

#### Prerequisites
- Docker Desktop installed ([Download here](https://www.docker.com/products/docker-desktop/))
- Docker Compose (included with Docker Desktop)

#### Using Docker Compose (Recommended)

**Step 1: Navigate to the API directory**
```bash
cd 3_Model_API
```

**Step 2: Build and start the container**
```bash
docker-compose up --build
```

The API will be available at http://localhost:8000

To run in detached mode (background):
```bash
docker-compose up -d --build
```

**Step 3: View logs**
```bash
docker-compose logs -f
```

**Step 4: Stop the container**
```bash
docker-compose down
```

Then your server should be ready to use now at port 8000 (localhost:8000)

### ⚠️ Important: Model Artifacts Required

The API requires pre-trained model files to run predictions. These files must be present in the `models/` directory:

```
models/
├── xgb_model.joblib                # Trained XGBoost model
├── preprocessing_artifacts.joblib  # Feature scaler and metadata
├── train_cols.json                 # Training column order
└── xgb_model.json                  # XGBoost metadata
```

**If model files are missing**, you'll see this error:
```
FileNotFoundError: [Errno 2] No such file or directory: 'models/xgb_model.joblib'
```

**To generate model artifacts:**

1. Ensure the training notebook has been run:
   ```bash
   cd scb-fraud-detection
   jupyter notebook 2_Model_Training.ipynb
   ```

2. The notebook will automatically save artifacts to `3_Model_API/models/`

3. Rebuild and restart Docker:
   ```bash
   cd 3_Model_API
   docker-compose down
   docker-compose up --build
   ```

**To test without a trained model** (development only):
- Skip Docker and run locally with `python server.py`
- The API will fail gracefully with "No model loaded" error for predictions
- Use this to verify API infrastructure while training your model

---

## 📋 Features

### API Endpoints
- **POST /predict** - Real-time fraud detection with ML model inference
  - Accepts transaction details (amount, type, account balances)
  - Returns fraud prediction with probability score (0.0 - 1.0)
  - Smart routing: Auto-marks low-risk types (PAYMENT, CASH_IN, DEBIT) as non-fraud
  - ML prediction for high-risk types (CASH_OUT, TRANSFER)
  - Automatic fraud record persistence for detected frauds

- **GET /frauds** - Retrieve fraud history
  - Returns all transactions previously flagged as fraudulent
  - Includes transaction data, fraud probability, and prediction timestamp
  - Sortable by database ID (auto-increment)

- **DELETE /frauds** - Clear fraud database
  - Deletes all fraud records from the database
  - Returns count of deleted records
  - Useful for testing and maintenance

- **GET /** - API health check
  - Returns API version and available endpoints
  - Quick status verification

- **GET /docs** - Interactive API documentation
  - Auto-generated Swagger UI
  - Live API testing interface
  - Schema exploration and examples

### Machine Learning
- **XGBoost Classifier** - Production-ready fraud detection model
  - Trained on historical transaction patterns
  - Binary classification (fraud/legitimate)
  - Probability scores for risk assessment

### Data Management
- **SQLite Database** - Lightweight persistent storage
  - Auto-created on startup
  - No configuration required
  - Fraud transaction logging with full payload
  - Timestamp tracking for audit trails

- **Pydantic Validation** - Request/response data integrity
  - Type-safe transaction models
  - Automatic validation with clear error messages
  - Enum support for transaction types
  - Optional fields for flexible integration

### Infrastructure
- **Docker Support** - Containerized deployment
  - Pre-configured Dockerfile and docker-compose
  - Consistent environment across development/production
  - Easy scaling and orchestration

- **Logging System** - Comprehensive request/response tracking
  - Structured logging with timestamps and severity levels
  - Request logging (transaction details)
  - Prediction logging (fraud decisions and probabilities)
  - Error tracking and debugging support

- **Load Testing Ready** - Performance validation
  - Locust integration with realistic CSV data
  - Concurrent user simulation
  - Performance metrics and bottleneck identification

---

## 📂 Project Structure

```
3_Model_API/
├── server.py                           # Main FastAPI application entry point
├── requirements.txt                    # Python dependencies
├── README.md                           # This documentation
├── Dockerfile                          # Docker image configuration
├── docker-compose.yml                  # Docker Compose orchestration
├── .dockerignore                       # Docker build exclusions
│
├── model_serving/                      # Core application modules
│   ├── schemas.py                      # Pydantic models (Transaction, Response schemas)
│   ├── model.py                        # ML model wrapper and inference logic
│   ├── preprocessing.py                # Feature engineering and transformation
│   ├── db.py                           # SQLite database operations
│   └── frauds.db                       # SQLite database (auto-created)
│
├── models/                             # Trained ML artifacts
│   ├── xgb_model.joblib                # Serialized XGBoost model
│   ├── xgb_model.json                  # XGBoost model metadata
│   ├── preprocessing_artifacts.joblib  # Feature scaler and metadata
│   └── train_cols.json                 # Training column order for inference
│
└── tests/                              # Testing utilities
    ├── locustfile.py                   # Load testing script (Locust)
    └── test.md                         # Test examples and documentation
```

### Key Files Explained

**`server.py`**
- FastAPI application initialization
- API endpoint definitions (predict, frauds, docs)
- Startup event handlers (DB init, model loading)
- Request/response logging configuration
- Business logic for transaction type routing

**`model_serving/schemas.py`**
- `Transaction` - Input model with validation
- `PredictionResponse` - Prediction output format
- `FraudTransaction` - Database record schema
- `TRANSAC_TYPE` - Transaction type enum
- OpenAPI examples for documentation

**`model_serving/model.py`**
- `FraudDetectionModel` class
- Model loading from joblib artifacts
- Prediction logic (XGBoost Booster and sklearn interfaces)
- Error handling and logging
- No fallback heuristics (model required)

**`model_serving/preprocessing.py`**
- `transform_transaction()` - Feature engineering pipeline
- `load_preprocessing_artifacts()` - Load scaler and metadata
- One-hot encoding for categorical features
- Feature scaling and column alignment
- Handles enum values from Pydantic

**`model_serving/db.py`**
- `init_db()` - Create frauds table
- `save_fraud_to_db()` - Insert fraud record
- `get_all_frauds()` - Retrieve all frauds
- `clear_frauds()` - Delete all records

**`models/` Directory**
- Generated by the training notebook (`2_Model_Training.ipynb`)
- Contains all artifacts needed for inference
- Must be present for model-based predictions

**`tests/locustfile.py`**
- Load testing configuration
- CSV data loading from `data/fraud_mock.csv`
- Realistic transaction payload generation
- Error logging and debugging hooks

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

## Load Testing with Locust

Locust is a scalable load testing tool that simulates concurrent users sending requests to your API.

#### Prerequisites
Install Locust in your virtual environment:
```bash
pip install locust
```

#### Running Locust Tests

**Navigate to the project root:**
```bash
cd scb-fraud-detection
```

**Start Locust with the test file:**
```bash
locust -f 3_Model_API/tests/locustfile.py --host=http://localhost:8000
```

**Open the Locust Web UI:**
- Open your browser and go to http://localhost:8089
- You'll see the Locust interface where you can configure:
  - **Number of users**: Total concurrent users to simulate
  - **Spawn rate**: How many users to start per second
  - **Host**: The target API (already set to http://localhost:8000)

**Example Configuration:**
- Number of users: `100`
- Spawn rate: `10` (ramps up 10 users/second)
- Host: `http://localhost:8000`

Click **Start Swarming** to begin the test.

#### Locust Test Details

The `locustfile.py` includes:
- **CSV Data Loading**: Loads transactions from `data/fraud_mock.csv`
- **Realistic Payloads**: Sends actual transaction data to `/predict`
- **Automatic Type Normalization**: Handles transaction type enums correctly
- **Random Sampling**: Each simulated user picks random transactions
- **Error Logging**: Logs first 5 payloads and all failed requests for debugging

#### Interpreting Results

In the Locust UI, monitor:
- **RPS (Requests Per Second)**: Throughput of your API
- **Response Time**: 50th, 95th, 99th percentiles
- **Failures**: Any 4xx/5xx errors
- **Number of Users**: Current active simulated users

---
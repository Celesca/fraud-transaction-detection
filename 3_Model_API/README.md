# Part 3: Fraud Detection REST API Service

A FastAPI-based REST API service for real-time fraud detection in financial transactions.


## Installation (with Docker) 🐳

The easiest way to run the API is using Docker, which packages all dependencies and the application into a container.

#### Prerequisites
- Docker Desktop installed ([Download here](https://www.docker.com/products/docker-desktop/))
- Docker Compose (included with Docker Desktop)

#### Option 1: Using Docker Compose (Recommended)

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

---

## 📋 Features

- **POST /predict**: Accept a transaction and return fraud prediction with probability score
- **GET /frauds**: Retrieve all transactions previously predicted as fraudulent
- **DELETE /frauds**: Clear all fraud records (useful for testing)
- **SQLite database**: Persistent storage for fraudulent transactions
- **Interactive API docs**: Auto-generated Swagger UI at `/docs`

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

## 🧪 Testing

### Unit Tests
Run the API test suite:
```bash
cd 3_Model_API
python test_api.py
```

### Load Testing with Locust

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

**Healthy API Performance:**
- 95th percentile response time < 500ms
- Failure rate < 1%
- Consistent RPS without degradation

---
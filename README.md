# SCB Cooperative Internship 2026 Take-Home Test: Fraudulent Transaction Detection

<div class="display: flex; justify-content: center;">
  <img height="100" alt="image" src="https://github.com/user-attachments/assets/a852942c-55f5-44dd-8a7f-a192c28173eb" />
</div>

by Sawit Koseeyaumporn

## Project Overview

This fraud detection system provides end-to-end capabilities for:

- **Part 1 : Data exploration and analysis (EDA)** of financial transaction patterns
- **Part 2 : Training machine learning models** to detect fraudulent transactions
- **Part 3 : Model Serving predictions** via a FastAPI REST API with real-time inference
- **Part 4 : System Architecture Design**

---


## 📂 Project Structure

```
scb-fraud-detection/
├── 1_Exploratory_Data_Analysis_EDA.ipynb   # Data exploration and visualization
├── 2_Model_Training.ipynb                   # Model training and evaluation
├── requirements.txt                         # Python dependencies for notebooks
├── references.md                            # Project references and resources
├── data/
│   └── fraud_mock.csv                       # Transaction dataset (50MB+)
├── 3_Model_API/                             # FastAPI service
│   ├── server.py                            # Main API application
│   ├── requirements.txt                     # API dependencies
│   ├── README.md                            # API-specific documentation
│   ├── model_serving/
│   │   ├── schemas.py                       # Pydantic models
│   │   ├── model.py                         # Model wrapper
│   │   ├── preprocessing.py                 # Feature engineering
│   │   └── db.py                            # Database operations
│   ├── models/
│   │   ├── xgb_model.joblib                 # Trained XGBoost model
│   │   ├── preprocessing_artifacts.joblib   # Scaler and feature metadata
│   │   └── train_cols.json                  # Training column order
│   └── tests/
│       ├── locustfile.py                    # Load testing script
│       └── test.md                          # Test examples
└── 4_System_Architecture_Design.png         # Architecture diagram
```

---

## 🚀 Getting Started (For Part 1, 2)

In the part 3 you can folllow instructions inside the folder `3_Model_API` instead.

### Prerequisites

- **Python 3.11** (recommended)
- **pip** (Python package installer)
- **Google Colab** (recommended)
- **Virtual environment** support

### Step 1: Clone the Repository

```bash
git clone https://github.com/Celesca/fraud-transaction-detection.git
cd fraud-transaction-detection
```

### Step 2 : Download the datasets

GitHub cannot includes the data because the file is too large. So we need to download manually and place it in `data/fraud_mock.csv` instead

Dataset Link : https://scbpocseasta001stdsbx.z23.web.core.windows.net/


### Step 2.5 (Optional): Download the `jupyter notebook (Part1, 2)`, datasets and `requirements.txt` then upload to Google Colab session or Kaggle session (Python 3.11 to run PyCaret)

I encouraged you to use the Google Colab or Kaggle to run the jupyter notebook because it's easy to handles with the environments but you can also use the local computer to run.

### Step 3: Set Up Python Virtual Environment

**Windows (Command Prompt):**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

You should see `(.venv)` prefix in your terminal.

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs all packages needed for the Jupyter notebooks (pandas, scikit-learn, xgboost, matplotlib, seaborn, etc.).

---



## 📊 Workflow

### 1. Exploratory Data Analysis (EDA)

**Notebook:** `1_Exploratory_Data_Analysis_EDA.ipynb`

Open and run this notebook to:
- Load and inspect the transaction dataset
- Perform statistical analysis and visualization
- Identify patterns in fraudulent vs. legitimate transactions
- Understand feature distributions and correlations
- Generate insights for feature engineering

**To run:**
```bash
jupyter notebook 1_Exploratory_Data_Analysis_EDA.ipynb
```

Or open it in VS Code with the Jupyter extension.

---

### 2. Model Training

**Notebook:** `2_Model_Training.ipynb`

This notebook covers:
- Feature engineering and preprocessing
- Train/test split and data preparation
- Model training (XGBoost classifier)
- Model evaluation (accuracy, precision, recall, F1-score, ROC-AUC)
- Saving trained models and preprocessing artifacts

**To run:**
```bash
jupyter notebook 2_Model_Training.ipynb
```

**Outputs:**
- `3_Model_API/models/xgb_model.joblib` - Trained XGBoost model
- `3_Model_API/models/preprocessing_artifacts.joblib` - Feature scaler and metadata
- `3_Model_API/models/train_cols.json` - Column order for inference

---

### 3. Model Serving (API)

**Directory:** `3_Model_API/`

Navigate to the API folder and follow the detailed setup instructions:

```bash
cd 3_Model_API
```

### 4. System Architecture Design

<img width="773" height="610" alt="kafka_architecture drawio" src="https://github.com/user-attachments/assets/dd7bc13c-97eb-4555-ab72-cc30824391d3" />

This document outlines the system architecture for a high-availability, real-time fraud detection platform. The system is designed to ingest a high volume of financial transactions, score them for fraud using a machine learning model, and provide a dedicated interface for auditors to review and update flagged cases.

The architecture is broken into three primary, interconnected services that operate in parallel:

* Real-Time Fraud Detection System: A low-latency "hot path" that scores every transaction in milliseconds.

* Audit Web App System: A "warm path" for human-in-the-loop review and investigation.

* Offline Model Training System: A "cold path" (batch) that acts as a feedback loop to continuously improve the ML model.

#### 1. Real-Time Fraud Detection System (Hot Path)

This service is responsible for ingesting, processing, and scoring transactions as they happen.

Kafka Transactions: The system's entry point. All financial transactions are streamed to this Kafka topic.

Fraud Detection Service (Consumer Group): A group of FDS (Fraud Detection Service) instances that subscribe to the Kafka topic. Using a Consumer Group allows the service to be horizontally scaled to handle any transaction volume.

Async Log: The FDS instances immediately log all incoming data to the Data Lake / Warehouse. This is an asynchronous "fire-and-forget" operation, ensuring that logging does not add latency to the real-time detection path.

Model Serving Load Balancer: Distributes the prediction workload evenly across the available Model instances. This prevents any single model server from becoming a bottleneck and allows for horizontal scaling of the ML model itself.

Model Endpoints: A pool of Model instances, each serving the same fraud detection model. They receive transaction data and return a fraud score.

Fraud Case DB Primary (Write): If a model flags a transaction ("only fraud"), the FDS writes the case details to this primary database. This database is optimized for high-speed writes to avoid blocking the real-time service.

#### 2. Audit Web App System (Warm Path)

This service provides the user interface for human auditors to review flagged cases.

Auditor (User): The end-user who investigates fraud.

Auditor Dashboard (Web App): The front-end application (e.g., React, Angular, Vue) that the auditor uses.

Auditor Web API: The back-end service that provides data to the dashboard and handles updates from the auditor.

Fraud Case DB Replica (Read): A read-only copy of the primary database. The Auditor Web API connects only to this replica for all read operations (e.g., fetching case lists, searching). This is a critical design choice to ensure that heavy, complex audit queries do not slow down or lock the Primary (Write) database, which is vital for the real-time system. Updates from the auditor (e.g., changing a case status) are sent via the API to the Primary DB.

#### 3. Offline Model Training System (Cold Path)

This service is the feedback loop that retrains and improves the fraud detection model over time.

ML Training Pipeline (Spark Batch): A scheduled batch job (e.g., running nightly) that:

Pulls Historical Data (e.g., "CASH_OUT or TRANSFER" types) from the Data Lake / Warehouse.

Pulls the Ground Truth (the final auditor-verified decisions) from the Fraud Case DB Replica.

Model Registry (MLFlow): The training pipeline pushes the new, improved model version to the Model Registry. This registry versions the models and manages their lifecycle.

Model Deployment: The Model Registry deploys the new model to all active Model instances, replacing the old model with zero downtime for the real-time service.

Model Monitoring: A service that watches the performance (e.g., latency, accuracy, data drift) of the live models by pulling data from the Data Lake.

## 📝 Additional Resources

- **[API Documentation](3_Model_API/README.md)** - Detailed API setup and usage
- **[References](references.md)** - Project references and citations
- **[Test Examples](3_Model_API/tests/test.md)** - Sample payloads for testing

---

## 📄 License

This project is part of an SCB Cooperative Internship 2026 assignment. Please contact the repository owner for usage permissions.

---

## 👥 Authors

- **Celesca** - [GitHub Profile](https://github.com/Celesca)

---

## 🙏 Acknowledgments

- SCB (Siam Commercial Bank) for the internship opportunity
- Dataset source and domain expertise providers
- Open-source community for the amazing tools and libraries


**Last Updated:** November 7, 2025

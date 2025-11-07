# Fraud Detection System

A comprehensive machine learning solution for detecting fraudulent financial transactions in real-time. This project includes exploratory data analysis, model training, and a production-ready REST API service.

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [System Architecture](#system-architecture)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Workflow](#workflow)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Contributing](#contributing)

---

## 🎯 Project Overview

This fraud detection system provides end-to-end capabilities for:

- **Data exploration and analysis** of financial transaction patterns
- **Training machine learning models** to detect fraudulent transactions
- **Serving predictions** via a FastAPI REST API with real-time inference
- **Persistent storage** of detected fraud cases for audit and analysis

The system focuses on high-risk transaction types (CASH_OUT and TRANSFER) and uses XGBoost for fraud classification.

---

## 🏗️ System Architecture

![System Architecture](system_architecture.png)

The architecture consists of three main components:

1. **Data Analysis Layer** - Jupyter notebooks for EDA and feature engineering
2. **Model Training Layer** - ML pipeline for training and evaluating fraud detection models
3. **API Serving Layer** - FastAPI service for real-time predictions with SQLite persistence

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
└── system_architecture.png                  # Architecture diagram
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11** (recommended)
- **pip** (Python package installer)
- **Virtual environment** support

### Step 1: Clone the Repository

```bash
git clone https://github.com/Celesca/fraud-transaction-detection.git
cd fraud-transaction-detection
```

### Step 2: Set Up Python Virtual Environment

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

### Step 3: Install Dependencies

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

Refer to the **[API README](3_Model_API/README.md)** for:
- Installing API dependencies (`requirements.txt`)
- Running the FastAPI server
- Testing endpoints
- Load testing with Locust
- Production deployment

**Quick start:**
```bash
cd 3_Model_API
pip install -r requirements.txt
python server.py
```

The API will be available at http://localhost:8000 with interactive docs at http://localhost:8000/docs

---

## ✨ Features

### Data Analysis
- Comprehensive EDA with visualizations
- Statistical analysis of fraud patterns
- Feature correlation and importance analysis

### Machine Learning
- XGBoost classification model
- Custom preprocessing pipeline
- Artifact persistence for reproducibility

### API Service
- **POST /predict** - Real-time fraud detection
- **GET /frauds** - Retrieve all detected fraud cases
- **DELETE /frauds** - Clear fraud records
- **Interactive API docs** - Swagger UI at `/docs`
- **Business logic** - Automatic non-fraud classification for low-risk transaction types (PAYMENT, CASH_IN, DEBIT)
- **Model-based prediction** - Uses trained XGBoost for high-risk types (CASH_OUT, TRANSFER)
- **Database persistence** - SQLite storage for fraud records
- **Load testing** - Locust-based performance testing

---

## 🛠️ Technologies Used

### Data Science & ML
- **Python 3.11**
- **Pandas** - Data manipulation
- **NumPy** - Numerical computing
- **Scikit-learn** - Preprocessing and evaluation
- **XGBoost** - Gradient boosting classifier
- **Matplotlib / Seaborn** - Data visualization
- **Jupyter Notebook** - Interactive development

### API & Infrastructure
- **FastAPI** - Modern web framework
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server
- **SQLite** - Lightweight database
- **Joblib** - Model serialization
- **Locust** - Load testing

---

## 📝 Additional Resources

- **[API Documentation](3_Model_API/README.md)** - Detailed API setup and usage
- **[References](references.md)** - Project references and citations
- **[Test Examples](3_Model_API/tests/test.md)** - Sample payloads for testing

---

## 🧪 Testing

### Unit Tests
Run the API test suite:
```bash
cd 3_Model_API
python test_api.py
```

### Load Testing
Run Locust to simulate concurrent users:
```bash
cd scb-fraud-detection
locust -f 3_Model_API/tests/locustfile.py --host=http://localhost:8000
```

Open http://localhost:8089 to configure and start the load test.

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is part of an internship assignment. Please contact the repository owner for usage permissions.

---

## 👥 Authors

- **Celesca** - [GitHub Profile](https://github.com/Celesca)

---

## 🙏 Acknowledgments

- SCB (Siam Commercial Bank) for the internship opportunity
- Dataset source and domain expertise providers
- Open-source community for the amazing tools and libraries

---

## 📞 Support

For questions or issues:
- Open an issue on GitHub
- Contact the development team

---

**Last Updated:** November 7, 2025

# SCB Cooperative Internship 2026 Take-Home Test: Fraudulent Transaction Detection

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

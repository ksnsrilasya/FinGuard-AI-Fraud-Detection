# 🛡️ FinGuard

## AI-Powered Financial Fraud Detection Platform

FinGuard is a full-stack web application that detects potentially fraudulent financial transactions using Machine Learning. The platform analyzes transaction details, predicts fraud risk, and provides a confidence score through an interactive dashboard. It demonstrates the integration of Machine Learning with modern backend development to solve a real-world financial security problem.

---

## 📌 Project Overview

Financial institutions process thousands of transactions every minute, making manual fraud detection inefficient and time-consuming.

FinGuard automates this process by analyzing transaction patterns and classifying transactions into Low, Medium, or High Risk using a trained Machine Learning model. The application also provides transaction history, fraud analytics, and an intuitive dashboard for monitoring suspicious activity.

---

## ✨ Features

- AI-powered fraud prediction using Machine Learning
- Real-time fraud risk analysis
- Confidence score for every prediction
- Interactive dashboard with transaction statistics
- Search and filter transaction history
- Export transaction history as CSV
- RESTful APIs built using FastAPI
- Responsive web interface
- Model evaluation using ROC Curve and Confusion Matrix

---

## 🖥️ Application Preview

### Dashboard

> *(Add dashboard screenshot here)*

```
screenshots/dashboard.png
```

---

### Fraud Prediction

> *(Add prediction page screenshot here)*

```
screenshots/prediction.png
```

---

### ROC Curve

> *(Add ROC Curve screenshot here)*

```
screenshots/roc_curve.png
```

---

### Confusion Matrix

> *(Add Confusion Matrix screenshot here)*

```
screenshots/confusion_matrix.png
```

---

## 🏗️ Project Structure

```
FinGuard-AI-Fraud-Detection
│
├── backend
├── frontend
├── models
├── screenshots
│
├── app.py
├── README.md
├── requirements.txt
└── .gitignore
```

---

## 🛠️ Technology Stack

### Backend
- Python
- FastAPI

### Frontend
- HTML5
- CSS3
- JavaScript

### Machine Learning
- Scikit-learn
- Pandas
- NumPy

### Database
- SQLite

### Data Visualization
- Matplotlib

---

## 🤖 Machine Learning Model

The fraud detection model is trained using transaction data and predicts whether a transaction is fraudulent based on multiple transaction attributes.

### Input Features

- Transaction Amount
- Merchant Category
- Transaction Type
- Device Type
- Location
- Transaction Time
- Previous Fraud History
- Customer Age
- Payment Method

### Prediction Output

- Low Risk
- Medium Risk
- High Risk

The application also displays the fraud probability and confidence score for each prediction.

---

## 📊 Model Performance

| Metric | Value |
|---------|--------|
| ROC-AUC Score | **0.96** |
| Fraud Recall | **0.74** |
| Fraud Precision | **0.44** |

The trained model was evaluated using a Confusion Matrix and ROC Curve to assess classification performance.

---

## 🔗 REST API Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/predict` | Predict fraud risk |
| GET | `/api/dashboard` | Dashboard statistics |
| GET | `/api/transactions` | View transaction history |
| DELETE | `/api/transactions/{id}` | Delete a transaction |
| GET | `/api/transactions/export` | Export transactions |
| POST | `/api/feedback` | Submit prediction feedback |

Interactive API documentation is available through FastAPI Swagger UI after running the application.

---

## 🚀 Installation

Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/FinGuard-AI-Fraud-Detection.git
```

Navigate to the project

```bash
cd FinGuard-AI-Fraud-Detection
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
uvicorn app:app --reload
```

Open your browser

```
http://127.0.0.1:8000
```

Swagger Documentation

```
http://127.0.0.1:8000/docs
```

---

## 📈 Future Enhancements

- User authentication and role-based access
- Email alerts for high-risk transactions
- PostgreSQL integration
- Docker deployment
- Cloud deployment using Render or Railway

---

## 👩‍💻 Author

**K S N Sri Lasya**

Computer Science (AI & ML) Undergraduate

GitHub: https://github.com/ksnsrilasya

LinkedIn: https://www.linkedin.com/in/k-s-n-sri-lasya-a887113b3

---

## 📄 License

This project is developed for educational purposes and portfolio demonstration.
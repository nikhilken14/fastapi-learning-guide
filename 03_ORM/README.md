# Product & Order API (FastAPI + SQLAlchemy ORM)

A minimal RESTful API built with **FastAPI**, **SQLAlchemy ORM**, and **PostgreSQL** demonstrating core Object-Relational Mapping (ORM) concepts, One-to-Many entity relationships, and DTO (Data Transfer Object) patterns using Pydantic schemas.

---

## 📁 Project Structure

```text
product-api/
│
├── app/
│   ├── main.py              # Application entry point & FastAPI setup
│   ├── database
│   │   └── db.py           # Database connection, SessionLocal & Base declaration
│   ├── models/
│   │   └── product.py       # SQLAlchemy ORM Models (Products & Orders)
│   ├── schemas/
│   │   └── product.py       # Pydantic Schemas / DTOs
│   └── routers/
│       └── product.py       # API Endpoint Routes
│
├── data.py                  # Script to populate initial sample data
│   
├── Dockerfile           
├── docker-compose.yml        
├── .env                     # Environment variables (Database connection string)
├── requirements.txt         # Project dependencies
└── README.md                # Documentation
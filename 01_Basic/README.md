# Module 01: Simple Product Service (FastAPI Basics)

A lightweight FastAPI service demonstrating basic REST API endpoints, application lifespan event handlers (data seeding), path/query parameters, custom HTTP exception handling, and full CRUD operations for products and sales.

---

## 🛠️ Features
- **Lifespan Manager:** Automatic database/sample data seeding on startup using `@asynccontextmanager`.
- **Health Checks:** Basic API root and health check endpoints.
- **Product Management:** Full CRUD operations (Get list, Get by ID, Add, Update Price, Delete).
- **Sales Analytics:** Endpoints to record sales, calculate total revenue, and aggregate sales/quantities by product.

---

## 📁 Suggested Folder Structure

01_Basic/
├── app/
│   ├── main.py
│   ├── product.py
│   ├── seed.py
│   ├── sells.py
│   └── service.py
├── Dockerfile
├── requirements.txt
└── README.md

---

## 🚀 How to Run Locally

- **Prerequisites** : Python 3.9+ installed

- **Navigate to the module directory:**

cd 01_Basic

- **Create and activate a virtual environment:**

python -m venv venv
venv\Scripts\activate

- **Install dependencies:**

pip install fastapi uvicorn

- **Start the application:**

uvicorn app.main:app --reload --port 8000

- **Access the Application:**

API Base URL: http://localhost:8000

Interactive Swagger UI Docs: http://localhost:8000/docs

ReDoc Documentation: http://localhost:8000/redoc

---

## 🐳 How to Run using Docker

- **Build the Docker Image:**

docker build -t fastapi-basic-app .

- **Run the Container:**

docker run -d -p 8000:8000 --name fastapi-basic fastapi-basic-app

- **Verify running container:**

docker ps

- **Access the application:**
Open http://localhost:8000/docs in your browser.

- **Stop and Remove Container:**

docker stop fastapi-basic
docker rm fastapi-basic

---
from contextlib import asynccontextmanager
from fastapi import FastAPI
from kafka.producers import kafka_producer_service
from api import orders  


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect producer to Kafka
    await kafka_producer_service.start()
    yield
    # Shutdown: Close producer connection
    await kafka_producer_service.stop()


app = FastAPI(title="Order API Service", lifespan=lifespan)

app.include_router(orders.router)

@app.get("/")
def home():
    return {"status" : "producer service is running"}

@app.get("/health")
def health_check():
    return {"status" : 200}
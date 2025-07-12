from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import products, categories
from app.db.database import engine
from app.models import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Product Service", description="Product Service for E-Store Microservices")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(products.router, prefix="/api", tags=["products"])
app.include_router(categories.router, prefix="/api", tags=["categories"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Product Service"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

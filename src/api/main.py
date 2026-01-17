from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="USFraudWatch API",
    description="Fraud monitoring and detection system",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "USFraudWatch API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

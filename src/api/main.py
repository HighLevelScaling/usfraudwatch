from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import articles_router
from src.api.routes.subscriptions import router as subscriptions_router
from src.api.routes.foia import router as foia_router
from src.api.routes.documents import router as documents_router
from src.api.routes.support import router as support_router

app = FastAPI(
    title="Federal Fraud Watch API",
    description="Conservative watchdog platform for immigration policy accountability",
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

# Include routers
app.include_router(articles_router, prefix="/api")
app.include_router(subscriptions_router, prefix="/api")
app.include_router(foia_router, prefix="/api")
app.include_router(documents_router, prefix="/api")
app.include_router(support_router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Federal Fraud Watch API", "status": "running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

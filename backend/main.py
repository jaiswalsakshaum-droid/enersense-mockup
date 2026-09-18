import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.orders import router as orders_router
from app.routers.process_twin import router as process_twin_router
from app.routers.optimization import router as optimization_router
from app.routers.plans import router as plans_router
from app.routers.plans_get import router as plans_get_router
from app.routers import (
    machines_router,
    dashboard_router,
    alerts_router,
    recommendations_router,
    simulate_router,
    schemes_router,
    stream_router,
    
)

app = FastAPI(
    title="EnerSense Industrial Energy Intelligence API",
    description="Backend microservice for plant telemetry, energy audits, what-if simulations, and live streams.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS for local frontend Vite development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://localhost:4000",
        "*",  # Permissive for hackathon demo
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers under /api
app.include_router(machines_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(alerts_router, prefix="/api")
app.include_router(recommendations_router, prefix="/api")
app.include_router(simulate_router, prefix="/api")
app.include_router(schemes_router, prefix="/api")
app.include_router(stream_router, prefix="/api")
app.include_router(orders_router)
app.include_router(process_twin_router)
app.include_router(optimization_router)
app.include_router(plans_router)
app.include_router(plans_get_router)

@app.get("/")
async def root():
    return {
        "service": "EnerSense Backend API",
        "status": "healthy",
        "documentation": "/docs",
        "version": "1.0.0",
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=4000, reload=True)

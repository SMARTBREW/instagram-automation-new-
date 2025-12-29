from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.config.settings import settings
from app.config.database import connect_to_mongo, close_mongo_connection
from app.config.logger import logger
from app.api.v1.router import router as v1_router
from app.core.exceptions import HTTPException as CustomHTTPException
import logging

# Logging is configured in app.config.logger
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Instagram DM Automation API",
    description="FastAPI backend for Instagram DM automation",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(CustomHTTPException)
async def custom_http_exception_handler(request: Request, exc: CustomHTTPException):
    """Handle custom HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.status_code, "message": exc.detail}},
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.status_code, "message": exc.detail}},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": {"code": 400, "message": "Validation error", "details": exc.errors()}},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": {"code": 500, "message": "Internal server error"}},
    )


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    await connect_to_mongo()
    logger.info("Application started")


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    await close_mongo_connection()
    logger.info("Application shutdown")


# Health check endpoints
@app.get("/health-check")
async def health_check():
    """Health check endpoint"""
    return PlainTextResponse("OK")


@app.get("/running")
async def running():
    """Running status endpoint"""
    return JSONResponse({"status": "running"})


@app.get("/")
async def root():
    """Root endpoint"""
    return PlainTextResponse("Service running")


@app.head("/")
async def root_head():
    """Root HEAD endpoint"""
    return JSONResponse({"status": "ok"})


@app.get("/privacy-policy")
async def privacy_policy():
    """Privacy policy endpoint"""
    # Return a simple HTML response or redirect to actual policy
    return PlainTextResponse("Privacy Policy - Add your policy content here")


# Include API routers
app.include_router(v1_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.NODE_ENV == "development",
    )


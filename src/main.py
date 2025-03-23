
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pydantic import BaseModel
from typing import List
from src.routers import attendees, categories, events, registrations

# DEFINE PYDANTIC MODELS FOR STRUCTURED RESPONSES
class EndpointInfo(BaseModel):
    """Model for endpoint information."""
    name: str
    url: str

class RootResponse(BaseModel):
    """Model for the root endpoint response."""
    message: str
    version: str
    endpoints: List[EndpointInfo]

# LIFECYCLE EVENT HANDLER
@asynccontextmanager
async def life_span(app: FastAPI):
  
    print(f"Starting the server ...")
    yield
    print(f"Stopping the server ...")


version = "1.0.0"

app = FastAPI(
    title="EVENTITLY",
    description="API for Event Management",
    version=version,
    lifespan=life_span
)


static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get(
    "/", 
    tags=["root"],
    response_model=RootResponse,
    summary="API Overview",
    description="Welcome to the Eventilly API! This endpoint provides an overview of the available endpoints and the API version."
)
async def root():
    return {
        "message": "Eventilly API",
        "version": version,
        "endpoints": [
            {"name": "Categories", "url": "/categories"},
            {"name": "Events", "url": "/events"},
            {"name": "Attendees", "url": "/attendees"},
            {"name": "Registrations", "url": "/registrations"},
            {"name": "Documentation", "url": "/docs"}
        ]
    }

# HEALTH CHECK ENDPOINT: PROVIDES STATUS CHECK (WHY - ENSURES THE API IS RUNNING)
@app.get("/health", tags=["root"])
async def health_check():
    """
    Health check endpoint to verify that the API is running.
    """
    return {"status": "healthy"}

# INCLUDE ROUTERS
app.include_router(categories.router, prefix="/categories", tags=["categories"])
app.include_router(events.router, prefix="/events", tags=["events"])
app.include_router(attendees.router, prefix="/attendees", tags=["attendees"])
app.include_router(registrations.router, prefix="/registrations", tags=["registrations"])

# CORS MIDDLEWARE - ENABLES CROSS-ORIGIN REQUESTS FOR ALL ROUTES.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ADD ERROR HANDLING FOR VALIDATION ERRORS
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors and return a formatted response.
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "body": exc.body,
            "message": "Validation error: Please check your request data"
        }
    )

# GLOBAL EXCEPTION HANDLER FOR UNEXPECTED ERRORS
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Handle any unhandled exceptions and return a formatted response.
    """
    # LOG ERROR IN PRODUCTION (WHY: FOR POST-MORTEM ANALYSIS)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": "An unexpected error occurred",
            "detail": str(exc)
        }
    )
if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 10000))
    uvicorn.run("src.main:app", host="0.0.0.0", port=port)
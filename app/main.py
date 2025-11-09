from fastapi import FastAPI

from app.core import errors
from app.routers import health, wishes

app = FastAPI(title="SecDev Course App", version="0.1.0")

app.include_router(health.router)
app.include_router(wishes.router)

app.add_exception_handler(errors.ApiError, errors.api_error_handler)
app.add_exception_handler(errors.HTTPException, errors.http_exception_handler)
app.add_exception_handler(
    errors.RequestValidationError, errors.request_validation_error_handler
)

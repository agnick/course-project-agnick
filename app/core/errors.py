from uuid import uuid4

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class ApiError(Exception):
    def __init__(self, code: str, message: str, status: int = 400):
        self.code = code
        self.message = message
        self.status = status


class AppValidationError(ApiError):
    def __init__(self, message: str = "validation error", status: int = 422):
        super().__init__(code="validation_error", message=message, status=status)


class NotFoundError(ApiError):
    def __init__(self, message: str = "resource not found"):
        super().__init__(code="not_found", message=message, status=404)


def problem(status: int, title: str, detail: str, type_: str = "about:blank"):
    cid = str(uuid4())
    payload = {
        "type": type_,
        "title": title,
        "status": status,
        "detail": detail,
        "correlation_id": cid,
    }
    return JSONResponse(payload, status_code=status)


def _wants_problem(request: Request) -> bool:
    accept = request.headers.get("accept", "")
    return "application/problem+json" in accept.lower()


async def api_error_handler(request: Request, exc: ApiError):
    if _wants_problem(request):
        return problem(
            status=exc.status,
            title=exc.code,
            detail=exc.message,
            type_=f"urn:secdev:error:{exc.code}",
        )
    return JSONResponse(
        status_code=exc.status,
        content={"error": {"code": exc.code, "message": exc.message}},
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail if isinstance(exc.detail, str) else "http_error"
    if _wants_problem(request):
        return problem(status=exc.status_code, title="HTTP Error", detail=detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": "http_error", "message": detail}},
    )


async def request_validation_error_handler(
    request: Request, exc: RequestValidationError
):
    if _wants_problem(request):
        return problem(
            status=422,
            title="Validation Error",
            detail="validation error",
            type_="urn:secdev:error:validation_error",
        )
    return JSONResponse(
        status_code=422,
        content={"error": {"code": "validation_error", "message": "validation error"}},
    )

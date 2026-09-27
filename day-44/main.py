"""AURONIX MVP REST API.

Provides the single primary endpoint POST /ask to interact with the core AI loop.
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from core_ai import core_ai_loop

app = FastAPI(
    title="AURONIX Private AI Workbench - Core MVP API",
    description="Day 44 MVP Core AI Interaction Endpoint",
    version="1.0.0",
)


class AskRequest(BaseModel):
    """Schema for employee query submission."""

    user_input: str = Field(
        ...,
        min_length=1,
        description="The employee question or prompt",
        examples=["What is AURONIX designed to do?"],
    )

    @field_validator("user_input")
    @classmethod
    def validate_not_whitespace(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("user_input cannot be empty or contain only whitespace.")
        return value.strip()


class AskResponse(BaseModel):
    """Schema for successful query response."""

    success: bool = True
    answer: str


class ErrorResponse(BaseModel):
    """Schema for error response."""

    success: bool = False
    error: str


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    """Formats Pydantic validation failures into the required error schema."""
    error_messages = []
    for err in exc.errors():
        field_loc = " -> ".join(str(loc) for loc in err.get("loc", []))
        msg = err.get("msg", "Invalid input")
        error_messages.append(f"{field_loc}: {msg}")
    combined_msg = "; ".join(error_messages)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"success": False, "error": f"Validation failed: {combined_msg}"},
    )


@app.get("/", tags=["Health"])
async def root():
    """Root info endpoint."""
    return {
        "product": "AURONIX",
        "day": 44,
        "status": "online",
        "endpoint": "POST /ask",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Service health check."""
    return {"status": "healthy"}


@app.post(
    "/ask",
    response_model=AskResponse,
    responses={
        200: {"model": AskResponse},
        400: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
    },
    tags=["Core AI"],
)
async def ask_endpoint(payload: AskRequest):
    """Processes a user question through the core AI loop."""
    try:
        answer = core_ai_loop(payload.user_input)
        return AskResponse(success=True, answer=answer)
    except ValueError as e:
        # Client validation or configuration error
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"success": False, "error": str(e)},
        )
    except PermissionError as e:
        # Missing or invalid credentials
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "error": str(e)},
        )
    except ConnectionError as e:
        # Upstream network/API connectivity failure
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"success": False, "error": str(e)},
        )
    except Exception as e:
        # General runtime failure
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "error": f"Internal server error: {e}"},
        )

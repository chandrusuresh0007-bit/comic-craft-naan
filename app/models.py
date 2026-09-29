from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
)


# =========================================================
# Authentication models
# =========================================================

class RegisterRequest(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )


class LoginRequest(BaseModel):
    email: EmailStr

    password: str = Field(
        min_length=1,
        max_length=128,
    )


# =========================================================
# Home planner
# =========================================================

class HomeRequest(BaseModel):
    model_config = ConfigDict(
        extra="ignore"
    )

    budget: float = Field(
        gt=0,
        le=10_000_000,
    )

    rooms: list[str] = Field(
        min_length=1,
        max_length=10,
    )

    style: str = Field(
        default="modern",
        min_length=1,
        max_length=50,
    )

    priorities: list[str] = Field(
        default_factory=list,
        max_length=10,
    )

    notes: str = Field(
        default="",
        max_length=2000,
    )


# =========================================================
# Party planner
# =========================================================

class PartyRequest(BaseModel):
    model_config = ConfigDict(
        extra="ignore"
    )

    budget: float = Field(
        gt=0,
        le=10_000_000,
    )

    guests: int = Field(
        gt=0,
        le=10_000,
    )

    event_type: str = Field(
        min_length=1,
        max_length=100,
    )

    venue: str = Field(
        default="",
        max_length=200,
    )

    city: str = Field(
        default="",
        max_length=100,
    )

    food_preference: str = Field(
        default="mixed",
        max_length=100,
    )

    notes: str = Field(
        default="",
        max_length=2000,
    )


# =========================================================
# Jewelry planner
# =========================================================

class JewelryRequest(BaseModel):
    model_config = ConfigDict(
        extra="ignore"
    )

    budget: float = Field(
        gt=0,
        le=10_000_000,
    )

    occasion: str = Field(
        min_length=1,
        max_length=100,
    )

    style: str = Field(
        default="elegant",
        max_length=100,
    )

    metal: str = Field(
        default="any",
        max_length=100,
    )

    notes: str = Field(
        default="",
        max_length=2000,
    )


# =========================================================
# Recommendation models
# =========================================================

class RecommendationItem(BaseModel):
    category: str

    name: str

    estimated_price: float

    reason: str

    platform: str

    search_url: str


class RecommendationResponse(BaseModel):
    planner: str

    budget: float

    allocation: dict[str, float]

    summary: str

    items: list[RecommendationItem]

    tips: list[str]

    source_mode: Literal[
        "gemini",
        "fallback",
    ]

from typing import Optional, Any

from pydantic import (
    BaseModel,
    Field,
    EmailStr,
    ConfigDict
)


# =========================
# Authentication
# =========================

class RegisterRequest(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100
    )

    email: EmailStr

    password: str = Field(
        min_length=6,
        max_length=128
    )


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    name: str
    email: EmailStr


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# =========================
# Home Planner
# =========================

class HomeBudgetInput(BaseModel):
    total_budget: float = Field(
        gt=0
    )

    num_lights: int = Field(
        default=0,
        ge=0,
        le=100
    )

    num_fans: int = Field(
        default=0,
        ge=0,
        le=100
    )

    num_furniture: int = Field(
        default=0,
        ge=0,
        le=100
    )

    num_dining_tables: int = Field(
        default=0,
        ge=0,
        le=20
    )

    has_living_room: bool = False
    has_kitchen: bool = False
    has_bedroom: bool = False

    additional_requirements: Optional[str] = Field(
        default=None,
        max_length=1000
    )


# =========================
# Party Planner
# =========================

class PartyBudgetInput(BaseModel):
    total_budget: float = Field(
        gt=0
    )

    party_type: str = Field(
        min_length=2,
        max_length=60
    )

    num_guests: int = Field(
        gt=0,
        le=10000
    )

    venue_type: Optional[str] = Field(
        default=None,
        max_length=100
    )

    needs_catering: bool = True

    needs_decoration: bool = True

    needs_entertainment: bool = False

    additional_requirements: Optional[str] = Field(
        default=None,
        max_length=1000
    )


# =========================
# Jewelry Planner
# =========================

class JewelryBudgetInput(BaseModel):
    total_budget: float = Field(
        gt=0
    )

    occasion: str = Field(
        min_length=2,
        max_length=100
    )

    preferences: Optional[str] = Field(
        default=None,
        max_length=1000
    )


# =========================
# Recommendation response
# =========================

class Item(BaseModel):
    name: str

    description: str = ""

    estimated_price: float = Field(
        ge=0
    )

    quantity: int = Field(
        default=1,
        ge=1
    )

    search_terms: str = ""

    shopping_links: dict[str, str] = {}


class BudgetCategory(BaseModel):
    category: str

    allocation: float = Field(
        ge=0
    )

    items: list[Item] = []


class RecommendationResult(BaseModel):
    planner: str

    total_budget: float

    budget_breakdown: list[BudgetCategory]

    remaining_budget: float = Field(
        ge=0
    )

    additional_suggestions: list[str] = []

    calculation_table_inr: list[dict[str, Any]] = []

    outfit_analysis: Optional[dict[str, Any]] = None

    styling_tips: list[str] = []
import json
import uuid

from pathlib import Path

from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form
)

from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session

from .config import settings

from .db import (
    Base,
    engine,
    get_db
)

from .models import (
    User,
    Recommendation
)

from .schemas import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserOut,
    HomeBudgetInput,
    PartyBudgetInput,
    JewelryBudgetInput,
    RecommendationResult
)

from .auth import (
    hash_password,
    verify_password,
    create_token,
    current_user
)

from .ai import (
    home,
    party,
    jewelry
)


# =========================================================
# APPLICATION SETUP
# =========================================================

Path(
    settings.upload_dir
).mkdir(
    parents=True,
    exist_ok=True
)


Base.metadata.create_all(
    bind=engine
)


app = FastAPI(
    title=settings.app_name,
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        settings.frontend_origin
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)


# =========================================================
# HEALTH
# =========================================================

@app.get("/api/health")
def health():

    return {
        "status": "ok",
        "ai_configured": bool(
            settings.gemini_api_key
        ),
        "model": settings.gemini_model
    }


# =========================================================
# REGISTER
# =========================================================

@app.post(
    "/api/auth/register",
    response_model=TokenResponse
)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):

    email = data.email.lower()

    existing = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if existing:

        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )

    user = User(
        name=data.name.strip(),
        email=email,
        password_hash=hash_password(
            data.password
        )
    )

    db.add(user)

    db.commit()

    db.refresh(user)

    return {
        "access_token": create_token(
            user.id
        ),
        "user": user
    }


# =========================================================
# LOGIN
# =========================================================

@app.post(
    "/api/auth/login",
    response_model=TokenResponse
)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):

    user = (
        db.query(User)
        .filter(
            User.email == data.email.lower()
        )
        .first()
    )

    if (
        not user
        or not verify_password(
            data.password,
            user.password_hash
        )
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    return {
        "access_token": create_token(
            user.id
        ),
        "user": user
    }


# =========================================================
# CURRENT USER
# =========================================================

@app.get(
    "/api/auth/me",
    response_model=UserOut
)
def me(
    user: User = Depends(current_user)
):

    return user


# =========================================================
# SAVE RECOMMENDATION
# =========================================================

def save_recommendation(
    db: Session,
    user: User,
    planner: str,
    total_budget: float,
    result: dict,
    input_data: dict
):

    recommendation = Recommendation(

        user_id=user.id,

        planner=planner,

        total_budget=total_budget,

        remaining_budget=result.get(
            "remaining_budget",
            0
        ),

        input_json=json.dumps(
            input_data
        ),

        result_json=json.dumps(
            result
        )
    )

    db.add(
        recommendation
    )

    db.commit()

    db.refresh(
        recommendation
    )

    return recommendation


# =========================================================
# HOME PLANNER
# =========================================================

@app.post(
    "/api/planners/home",
    response_model=RecommendationResult
)
def home_plan(
    data: HomeBudgetInput,

    db: Session = Depends(get_db),

    user: User = Depends(current_user)
):

    result = home(data)

    save_recommendation(
        db,
        user,
        "home",
        data.total_budget,
        result,
        data.model_dump()
    )

    return result


# =========================================================
# PARTY PLANNER
# =========================================================

@app.post(
    "/api/planners/party",
    response_model=RecommendationResult
)
def party_plan(
    data: PartyBudgetInput,

    db: Session = Depends(get_db),

    user: User = Depends(current_user)
):

    result = party(data)

    save_recommendation(
        db,
        user,
        "party",
        data.total_budget,
        result,
        data.model_dump()
    )

    return result


# =========================================================
# JEWELRY PLANNER
# =========================================================

@app.post(
    "/api/planners/jewelry",
    response_model=RecommendationResult
)
async def jewelry_plan(

    total_budget: float = Form(...),

    occasion: str = Form(...),

    preferences: str | None = Form(
        None
    ),

    image: UploadFile | None = File(
        None
    ),

    db: Session = Depends(get_db),

    user: User = Depends(current_user)
):

    if total_budget <= 0:

        raise HTTPException(
            status_code=422,
            detail="Budget must be positive"
        )

    image_bytes = None

    mime_type = None

    filename = None

    # -------------------------
    # IMAGE VALIDATION
    # -------------------------

    if image:

        allowed_types = {
            "image/jpeg",
            "image/png",
            "image/webp"
        }

        if image.content_type not in allowed_types:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Only JPG, PNG, or WEBP "
                    "images are supported"
                )
            )

        image_bytes = await image.read()

        max_bytes = (
            settings.max_upload_mb
            * 1024
            * 1024
        )

        if len(image_bytes) > max_bytes:

            raise HTTPException(
                status_code=413,
                detail="Image is too large"
            )

        filename = image.filename

        mime_type = image.content_type

        safe_name = (
            f"{uuid.uuid4().hex}_"
            f"{Path(image.filename or 'outfit').name}"
        )

        Path(
            settings.upload_dir,
            safe_name
        ).write_bytes(
            image_bytes
        )

    data = JewelryBudgetInput(
        total_budget=total_budget,
        occasion=occasion,
        preferences=preferences
    )

    result = jewelry(
        data,
        image_bytes,
        mime_type
    )

    input_data = data.model_dump()

    input_data["image_filename"] = filename

    save_recommendation(
        db,
        user,
        "jewelry",
        total_budget,
        result,
        input_data
    )

    return result


# =========================================================
# HISTORY
# =========================================================

@app.get("/api/history")
def history(
    db: Session = Depends(get_db),

    user: User = Depends(current_user)
):

    rows = (
        db.query(Recommendation)
        .filter(
            Recommendation.user_id == user.id
        )
        .order_by(
            Recommendation.created_at.desc()
        )
        .all()
    )

    return [
        {
            "id": row.id,

            "planner": row.planner,

            "total_budget":
                row.total_budget,

            "remaining_budget":
                row.remaining_budget,

            "created_at":
                row.created_at.isoformat(),

            "input":
                json.loads(
                    row.input_json
                ),

            "result":
                json.loads(
                    row.result_json
                )
        }

        for row in rows
    ]


# =========================================================
# DELETE HISTORY
# =========================================================

@app.delete(
    "/api/history/{rec_id}"
)
def delete_history(
    rec_id: int,

    db: Session = Depends(get_db),

    user: User = Depends(current_user)
):

    row = (
        db.query(Recommendation)
        .filter(
            Recommendation.id == rec_id,
            Recommendation.user_id == user.id
        )
        .first()
    )

    if not row:

        raise HTTPException(
            status_code=404,
            detail="Recommendation not found"
        )

    db.delete(row)

    db.commit()

    return {
        "message": "Deleted"
    }


# =========================================================
# RUN DIRECTLY
# =========================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
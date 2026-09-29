import json
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from sqlalchemy.orm import Session

from app.database import (
    RecommendationHistory,
    get_db,
)

from app.models import (
    HomeRequest,
    JewelryRequest,
    PartyRequest,
)

from app.security import (
    get_current_user,
)

from app.services.gemini import (
    generate_recommendations,
)


router = APIRouter(
    tags=["Recommendation Planners"]
)


# =========================================================
# Save history
# =========================================================

def save_history(
    db: Session,
    user_id: int,
    planner: str,
    request_data: dict,
    response_data: dict,
) -> RecommendationHistory:

    record = RecommendationHistory(
        user_id=user_id,
        planner=planner,
        request_json=json.dumps(
            request_data,
            ensure_ascii=False,
        ),
        response_json=json.dumps(
            response_data,
            ensure_ascii=False,
        ),
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


# =========================================================
# Home planner
# =========================================================

@router.post("/generate-home")
def generate_home(
    data: HomeRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):

    result = generate_recommendations(
        planner="home",
        data=data.model_dump(),
    )

    save_history(
        db=db,
        user_id=user.id,
        planner="home",
        request_data=data.model_dump(),
        response_data=result,
    )

    return result


# =========================================================
# Party planner
# =========================================================

@router.post("/generate-party")
def generate_party(
    data: PartyRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):

    result = generate_recommendations(
        planner="party",
        data=data.model_dump(),
    )

    save_history(
        db=db,
        user_id=user.id,
        planner="party",
        request_data=data.model_dump(),
        response_data=result,
    )

    return result


# =========================================================
# Jewelry planner
# =========================================================

@router.post("/generate-jewelry")
async def generate_jewelry(
    budget: float = Form(...),
    occasion: str = Form(...),
    style: str = Form("elegant"),
    metal: str = Form("any"),
    notes: str = Form(""),
    outfit_image: Optional[UploadFile] = File(None),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):

    if budget <= 0:
        raise HTTPException(
            status_code=422,
            detail="Budget must be greater than zero.",
        )

    if budget > 10_000_000:
        raise HTTPException(
            status_code=422,
            detail="Budget is too large.",
        )

    image_bytes = None
    image_mime_type = None

    if outfit_image is not None:

        if not outfit_image.content_type:
            raise HTTPException(
                status_code=400,
                detail="Uploaded image has no content type.",
            )

        allowed_types = {
            "image/jpeg",
            "image/png",
            "image/webp",
        }

        if outfit_image.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Only JPG, PNG and WEBP images "
                    "are supported."
                ),
            )

        image_bytes = await outfit_image.read()

        # 5 MB safety limit
        if len(image_bytes) > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="Image must be smaller than 5 MB.",
            )

        image_mime_type = (
            outfit_image.content_type
        )

    request_data = {
        "budget": budget,
        "occasion": occasion,
        "style": style,
        "metal": metal,
        "notes": notes,
        "image_uploaded": image_bytes is not None,
    }

    result = generate_recommendations(
        planner="jewelry",
        data=request_data,
        image_bytes=image_bytes,
        image_mime_type=image_mime_type,
    )

    save_history(
        db=db,
        user_id=user.id,
        planner="jewelry",
        request_data=request_data,
        response_data=result,
    )

    return result


# =========================================================
# History
# =========================================================

@router.get("/history")
def history(
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):

    records = (
        db.query(
            RecommendationHistory
        )
        .filter(
            RecommendationHistory.user_id
            == user.id
        )
        .order_by(
            RecommendationHistory.created_at.desc()
        )
        .all()
    )

    return {
        "history": [
            {
                "id": record.id,
                "planner": record.planner,
                "created_at": (
                    record.created_at.isoformat()
                    if record.created_at
                    else None
                ),
                "request": json.loads(
                    record.request_json
                ),
                "response": json.loads(
                    record.response_json
                ),
            }
            for record in records
        ]
    }


# =========================================================
# Recommendation details
# =========================================================

@router.get(
    "/recommendations-details/{recommendation_id}"
)
def recommendation_details(
    recommendation_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):

    record = db.get(
        RecommendationHistory,
        recommendation_id,
    )

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Recommendation not found.",
        )

    if record.user_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="You cannot access this recommendation.",
        )

    return {
        "id": record.id,
        "planner": record.planner,
        "created_at": (
            record.created_at.isoformat()
            if record.created_at
            else None
        ),
        "request": json.loads(
            record.request_json
        ),
        "response": json.loads(
            record.response_json
        ),
    }

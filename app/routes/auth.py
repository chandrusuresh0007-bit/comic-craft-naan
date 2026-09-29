from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
)

from sqlalchemy.orm import Session

from app.database import (
    get_db,
    User,
)

from app.models import (
    LoginRequest,
    RegisterRequest,
)

from app.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)


router = APIRouter(
    tags=["Authentication"]
)


# =========================================================
# Register
# =========================================================

@router.post("/register")
def register(
    data: RegisterRequest,
    request: Request,
    db: Session = Depends(get_db),
):

    email = data.email.lower().strip()

    existing = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists.",
        )

    user = User(
        name=data.name.strip(),
        email=email,
        password_hash=hash_password(
            data.password
        ),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(
        user.id
    )

    request.session[
        "access_token"
    ] = token

    return {
        "message": "Registration successful.",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
        },
    }


# =========================================================
# Login
# =========================================================

@router.post("/login")
def login(
    data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
):

    email = data.email.lower().strip()

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if (
        user is None
        or not verify_password(
            data.password,
            user.password_hash,
        )
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    request.session[
        "access_token"
    ] = create_access_token(
        user.id
    )

    return {
        "message": "Login successful.",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
        },
    }


# =========================================================
# Logout
# =========================================================

@router.post("/logout")
def logout(
    request: Request,
):
    request.session.clear()

    return {
        "message": "Logged out successfully."
    }


# =========================================================
# Session information
# =========================================================

@router.get("/session-info")
def session_info(
    user=Depends(get_current_user),
):

    return {
        "logged_in": True,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
        },
    }


# =========================================================
# Session personalization data
# =========================================================

@router.get("/session-data")
def session_data(
    user=Depends(get_current_user),
):

    return {
        "user_id": user.id,
        "login_status": True,
        "personalization": {
            "name": user.name,
            "email": user.email,
        },
    }


# =========================================================
# Token compatibility endpoint
# =========================================================

@router.post("/token")
def token(
    data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
):

    result = login(
        data=data,
        request=request,
        db=db,
    )

    return {
        "access_token": request.session.get(
            "access_token"
        ),
        "token_type": "bearer",
        "user": result["user"],
    }

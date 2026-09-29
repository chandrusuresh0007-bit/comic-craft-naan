from pathlib import Path

from fastapi import (
    APIRouter,
    Request,
)

from fastapi.responses import HTMLResponse

from fastapi.templating import Jinja2Templates


BASE_DIR = Path(
    __file__
).resolve().parent.parent


templates = Jinja2Templates(
    directory=str(
        BASE_DIR / "templates"
    )
)


router = APIRouter()


# =========================================================
# Home
# =========================================================

@router.get(
    "/",
    response_class=HTMLResponse,
)
def index(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )


# =========================================================
# Login
# =========================================================

@router.get(
    "/login",
    response_class=HTMLResponse,
)
def login_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="login.html",
    )


# =========================================================
# Register
# =========================================================

@router.get(
    "/register",
    response_class=HTMLResponse,
)
def register_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="register.html",
    )


# =========================================================
# Dashboard
# =========================================================

@router.get(
    "/dashboard",
    response_class=HTMLResponse,
)
def dashboard_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
    )


# =========================================================
# Planner pages
# =========================================================

@router.get(
    "/planner/{planner}",
    response_class=HTMLResponse,
)
def planner_page(
    request: Request,
    planner: str,
):

    allowed = {
        "home",
        "party",
        "jewelry",
    }

    if planner not in allowed:
        planner = "home"

    return templates.TemplateResponse(
        request=request,
        name=f"{planner}_planner.html",
    )

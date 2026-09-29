from datetime import datetime, timezone

from sqlalchemy import (
    create_engine,
    String,
    Integer,
    DateTime,
    Text,
    ForeignKey,
)

from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
)

from app.config import settings


# ---------------------------------------------------------
# Engine
# ---------------------------------------------------------

connect_args = {}

if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False,
    }


engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    future=True,
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


# ---------------------------------------------------------
# Base
# ---------------------------------------------------------

class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------
# User
# ---------------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    history: Mapped[list["RecommendationHistory"]] = relationship(
        "RecommendationHistory",
        back_populates="user",
        cascade="all, delete-orphan",
    )


# ---------------------------------------------------------
# Recommendation history
# ---------------------------------------------------------

class RecommendationHistory(Base):
    __tablename__ = "recommendation_history"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    planner: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    request_json: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    response_json: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user: Mapped[User] = relationship(
        "User",
        back_populates="history",
    )


# ---------------------------------------------------------
# Database initialization
# ---------------------------------------------------------

def init_db() -> None:
    Base.metadata.create_all(
        bind=engine,
    )


# ---------------------------------------------------------
# FastAPI database dependency
# ---------------------------------------------------------

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

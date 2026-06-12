from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import Account
from app.security.jwt_verifier import JWTVerifier

settings = get_settings()
jwt_verifier = JWTVerifier(
    secret_key=settings.secret_key,
    algorithm=settings.algorithm,
    cookie_name=settings.cookie_name,
)


def get_current_aid(request: Request, db: Annotated[Session, Depends(get_db)]) -> int:
    if settings.debug:
        return settings.debug_aid

    claims = jwt_verifier.verify_request(request)
    username = jwt_verifier.get_username(claims)
    account = db.scalar(
        select(Account).where(Account.username == username, Account.is_deleted.is_(False))
    )
    if account is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="アカウントが見つかりません",
        )
    return account.id


CurrentAid = Annotated[int, Depends(get_current_aid)]
DbSession = Annotated[Session, Depends(get_db)]

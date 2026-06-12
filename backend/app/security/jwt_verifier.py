from typing import Any, Callable

from fastapi import HTTPException, Request, status
from jose import JWTError, jwt


class JWTVerifier:
    """HttpOnly Cookie に格納された JWT を検証する。"""

    def __init__(
        self,
        *,
        secret_key: str,
        algorithm: str = "HS256",
        cookie_name: str = "access_token",
    ) -> None:
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.cookie_name = cookie_name

    def get_raw_token(self, request: Request) -> str | None:
        return request.cookies.get(self.cookie_name)

    def decode_token(self, token: str) -> dict[str, Any]:
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except JWTError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="無効または期限切れのトークンです",
            ) from exc

    def verify_request(self, request: Request) -> dict[str, Any]:
        token = self.get_raw_token(request)
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="認証が必要です",
            )
        return self.decode_token(token)

    def get_username(self, payload: dict[str, Any]) -> str:
        username = payload.get("username")
        if not isinstance(username, str) or not username.strip():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="トークンに有効なユーザー名が含まれていません",
            )
        return username.strip()

    def dependency(self) -> Callable[[Request], dict[str, Any]]:
        def _dependency(request: Request) -> dict[str, Any]:
            return self.verify_request(request)

        return _dependency

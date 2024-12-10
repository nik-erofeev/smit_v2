from datetime import datetime, timedelta, timezone

from jose import jwt
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth.dao import UsersDAO
from app.api.auth.schemas import EmailModel
from app.api.auth.utils import verify_password
from app.core.settings import APP_CONFIG
from app.dao.session_maker import SessionDep


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=30)
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(
        to_encode,
        APP_CONFIG.SECRET_KEY,
        algorithm=APP_CONFIG.ALGORITHM,
    )
    return encode_jwt


async def authenticate_user(
    email: EmailStr,
    password: str,
    session: AsyncSession = SessionDep,  # type: ignore
):
    user = await UsersDAO.find_one_or_none(
        session=session,
        filters=EmailModel(email=email),
    )
    if (
        not user
        or verify_password(plain_password=password, hashed_password=user.password)
        is False
    ):
        return None
    return user

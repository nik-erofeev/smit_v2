from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth.auth import authenticate_user, create_access_token
from app.api.auth.dao import UsersDAO
from app.api.auth.dependencies import get_current_admin_user, get_current_user
from app.api.auth.exceptions import (
    IncorrectEmailOrPasswordException,
    UserAlreadyExistsException,
)
from app.api.auth.schemas import (
    EmailModel,
    SUserAddDB,
    SUserAuth,
    SUserInfo,
    SUserRegister,
    UAuthResponse,
    UserOutResponse,
    UserRegResponse,
)
from app.dao.session_maker import SessionDep
from app.models import User

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register/",
    summary="Регистрация пользователя",
    response_model=UserRegResponse,
    response_class=ORJSONResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    user_data: SUserRegister,
    session: AsyncSession = SessionDep,
):
    user = await UsersDAO.find_one_or_none(
        session=session,
        filters=EmailModel(email=user_data.email),
    )
    if user:
        raise UserAlreadyExistsException
    user_data_dict = user_data.model_dump()
    del user_data_dict["confirm_password"]
    await UsersDAO.add(session=session, values=SUserAddDB(**user_data_dict))
    return UserRegResponse()


@router.post(
    "/login/",
    response_model=UAuthResponse,
    response_class=ORJSONResponse,
    status_code=status.HTTP_200_OK,
)
async def auth_user(
    response: Response,
    user_data: SUserAuth,
    session: AsyncSession = SessionDep,
):
    check = await authenticate_user(
        session=session,
        email=user_data.email,
        password=user_data.password,
    )
    if check is None:
        raise IncorrectEmailOrPasswordException
    access_token = create_access_token({"sub": str(check.id)})
    response.set_cookie(key="users_access_token", value=access_token, httponly=False)
    return UAuthResponse(access_token=access_token)


@router.post(
    "/logout/",
    response_model=UserOutResponse,
    response_class=ORJSONResponse,
    status_code=status.HTTP_200_OK,
)
async def logout_user(response: Response):
    response.delete_cookie(key="users_access_token")
    return UserOutResponse()


@router.get(
    "/me/",
    response_model=SUserInfo,
    response_class=ORJSONResponse,
    status_code=status.HTTP_200_OK,
)
async def get_me(user_data: User = Depends(get_current_user)):
    return SUserInfo.model_validate(user_data)


@router.get(
    "/all_users/",
    response_model=list[SUserInfo],
    response_class=ORJSONResponse,
    status_code=status.HTTP_200_OK,
)
async def get_all_users(
    session: AsyncSession = SessionDep,
    user_data: User = Depends(get_current_admin_user),
):
    result = await UsersDAO.find_all(session=session, filters=None)
    return [SUserInfo.model_validate(user) for user in result]

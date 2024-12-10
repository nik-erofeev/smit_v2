from fastapi import HTTPException, status

TokenNoFound = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Токен истек",
)


NoJwtException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Токен не валидный!",
)


TokenExpiredException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Токен истек",
)


NoUserIdException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Не найден ID пользователя",
)


ForbiddenException = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Недостаточно прав!",
)


UserAlreadyExistsException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Пользователь уже существует",
)


IncorrectEmailOrPasswordException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Неверная почта или пароль",
)

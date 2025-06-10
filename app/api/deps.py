# from typing import Generator, AsyncGenerator
# from fastapi import Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer
# from jose import jwt, JWTError
# from sqlalchemy.ext.asyncio import AsyncSession
# from app.db.session import SessionLocal
# from app.core import security, config
# from app.schemas.token import TokenData
# from app.models.user import User
# from app.crud import crud_user

# reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")

# async def get_db() -> AsyncGenerator[AsyncSession, None]:
#     async with SessionLocal() as session:
#         yield session

# async def get_current_user(
#     db: AsyncSession = Depends(get_db), token: str = Depends(reusable_oauth2)
# ) -> User:
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(
#             token, config.settings.SECRET_KEY, algorithms=[config.settings.ALGORITHM]
#         )
#         email: str = payload.get("sub")
#         if email is None:
#             raise credentials_exception
#         token_data = TokenData(email=email)
#     except JWTError:
#         raise credentials_exception
#     user = await crud_user.get_by_email(db, email=token_data.email)
#     if user is None:
#         raise credentials_exception
#     return user

from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import SessionLocal
from app.core import security, config
from app.schemas.token import TokenData
from app.models.user import User
# --- THIS IS THE KEY CHANGE ---
# Import the 'user' instance from the crud_user module
from app.crud.crud_user import user as crud_user_instance

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session

async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, config.settings.SECRET_KEY, algorithms=[config.settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    # --- THIS IS THE FIXED LINE ---
    # We call the method on the imported instance
    user = await crud_user_instance.get_by_email(db, email=token_data.email)
    
    if user is None:
        raise credentials_exception
    return user
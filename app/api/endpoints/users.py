# # from fastapi import APIRouter, Depends, HTTPException, status
# # from fastapi.security import OAuth2PasswordRequestForm
# # from sqlalchemy.ext.asyncio import AsyncSession
# # from app import schemas, crud, models
# # from app.api import deps
# # from app.core.security import create_access_token, get_password_hash, verify_password
# # from app.schemas.user import User as UserSchema, UserCreate
# # from app.schemas.token import Token

# # router = APIRouter()

# # @router.post("/register", response_model=schemas.User)
# # async def register_user(
# #     user_in: schemas.UserCreate,
# #     db: AsyncSession = Depends(deps.get_db)
# # ):
# #     user = await crud.crud_user.get_by_email(db, email=user_in.email)
# #     if user:
# #         raise HTTPException(
# #             status_code=400,
# #             detail="The user with this email already exists.",
# #         )
# #     hashed_password = get_password_hash(user_in.password)
# #     user_create = schemas.UserCreate(email=user_in.email, password=hashed_password)
    
# #     # This is a bit of a hack because our CRUD expects a plain UserCreate
# #     # A better way would be to adjust the CRUD base or have a separate schema
# #     db_user = models.User(
# #         email=user_create.email,
# #         hashed_password=user_create.password # It's already hashed here
# #     )
# #     db.add(db_user)
# #     await db.commit()
# #     await db.refresh(db_user)
# #     return db_user


# # @router.post("/login", response_model=schemas.Token)
# # async def login_for_access_token(
# #     db: AsyncSession = Depends(deps.get_db),
# #     form_data: OAuth2PasswordRequestForm = Depends()
# # ):
# #     user = await crud.crud_user.get_by_email(db, email=form_data.username)
# #     if not user or not verify_password(form_data.password, user.hashed_password):
# #         raise HTTPException(
# #             status_code=status.HTTP_401_UNAUTHORIZED,
# #             detail="Incorrect email or password",
# #             headers={"WWW-Authenticate": "Bearer"},
# #         )
# #     access_token = create_access_token(subject=user.email)
# #     return {"access_token": access_token, "token_type": "bearer"}









# # app/api/endpoints/users.py

# from fastapi import APIRouter, Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordRequestForm
# from sqlalchemy.ext.asyncio import AsyncSession

# from app import crud, models # We still need these
# from app.api import deps
# from app.core.security import create_access_token, get_password_hash, verify_password

# from app.schemas.user import User as UserSchema, UserCreate
# from app.schemas.token import Token
# # -----------------------------

# router = APIRouter()

# # Note the change here: response_model is now UserSchema
# @router.post("/register", response_model=UserSchema)
# async def register_user(
#     # And here: user_in is now explicitly UserCreate
#     user_in: UserCreate,
#     db: AsyncSession = Depends(deps.get_db)
# ):
#     user = await crud.crud_user.get_by_email(db, email=user_in.email)
#     if user:
#         raise HTTPException(
#             status_code=400,
#             detail="The user with this email already exists.",
#         )
#     hashed_password = get_password_hash(user_in.password)
    
#     # We create the DB model directly
#     db_user = models.User(
#         email=user_in.email,
#         hashed_password=hashed_password
#     )
#     db.add(db_user)
#     await db.commit()
#     await db.refresh(db_user)
#     return db_user


# # Note the change here: response_model is now Token
# @router.post("/login", response_model=Token)
# async def login_for_access_token(
#     db: AsyncSession = Depends(deps.get_db),
#     form_data: OAuth2PasswordRequestForm = Depends()
# ):
#     user = await crud.crud_user.get_by_email(db, email=form_data.username)
#     if not user or not verify_password(form_data.password, user.hashed_password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect email or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token = create_access_token(subject=user.email)
#     return {"access_token": access_token, "token_type": "bearer"}
# app/api/endpoints/users.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
# --- THIS IS THE KEY CHANGE ---
from app.models.user import User as UserModel # Import the class directly and give it an alias
from app.api import deps
from app.core.security import create_access_token, get_password_hash, verify_password
from app.schemas.user import User as UserSchema, UserCreate
from app.schemas.token import Token

router = APIRouter()

@router.post("/register", response_model=UserSchema)
async def register_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(deps.get_db)
):
    user_in_db = await crud.crud_user.user.get_by_email(db, email=user_in.email)
    
    if user_in_db:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists.",
        )
        
    hashed_password = get_password_hash(user_in.password)
    
    # --- USE THE CORRECTLY IMPORTED MODEL ---
    db_user = UserModel(
        email=user_in.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.post("/login", response_model=Token)
async def login_for_access_token(
    db: AsyncSession = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = await crud.crud_user.user.get_by_email(db, email=form_data.username)
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(subject=user.email)
    return {"access_token": access_token, "token_type": "bearer"}
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate

class CRUDUser(CRUDBase[User, UserCreate]):
    async def get_by_email(self, db: AsyncSession, *, email: str) -> User | None:
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalars().first()

user = CRUDUser(User)
from sqlalchemy.ext.asyncio import AsyncSession
# --- THIS IS THE MISSING LINE ---
from sqlalchemy.future import select
from app.crud.base import CRUDBase
from app.models.item import ScrapedItem
from app.schemas.item import ItemCreate

class CRUDItem(CRUDBase[ScrapedItem, ItemCreate]):
    async def create_with_owner(
        self, db: AsyncSession, *, obj_in: ItemCreate, owner_id: int
    ) -> ScrapedItem:
        db_obj = self.model(**obj_in.dict(), owner_id=owner_id)
        db.add(db_obj)
        return db_obj

    async def get_multi_by_owner(
        self, db: AsyncSession, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> list[ScrapedItem]:
        # This code will now work because 'select' is correctly imported.
        result = await db.execute(
            select(self.model)
            .filter(self.model.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

item = CRUDItem(ScrapedItem)
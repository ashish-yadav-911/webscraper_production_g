from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class ScrapedItem(Base):
    __tablename__ = "scraped_items"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True)
    title = Column(String, index=True)
    price = Column(Float)
    description = Column(String)
    # --- ADD THIS LINE ---
    image_url = Column(String, nullable=True)

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User")
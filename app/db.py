import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///app.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Lead(Base):
    __tablename__ = "leads"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow)
    customer_message = Column(Text)
    intent = Column(String)
    priority = Column(String)
    revenue_tier = Column(String)
    territory_code = Column(String)
    zone_id = Column(String)
    service_tier = Column(String)
    tech_assigned = Column(String)
    quote_min = Column(Integer)
    quote_max = Column(Integer)
    status = Column(String, default="new")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "customer_message": self.customer_message,
            "intent": self.intent,
            "priority": self.priority,
            "revenue_tier": self.revenue_tier,
            "territory_code": self.territory_code,
            "zone_id": self.zone_id,
            "service_tier": self.service_tier,
            "tech_assigned": self.tech_assigned,
            "quote_min": self.quote_min,
            "quote_max": self.quote_max,
            "status": self.status,
        }


def init_db() -> None:
    Base.metadata.create_all(bind=engine)

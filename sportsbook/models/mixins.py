from sqlalchemy import Column, DateTime
from datetime import datetime



class TimestampMixin(object):
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
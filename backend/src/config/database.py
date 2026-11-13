from sqlalchemy import create_engine,inspect,text
from sqlalchemy.orm import DeclarativeBase,sessionmaker
from .settings import DATABASE_URL
class Base(DeclarativeBase): pass
engine=create_engine(DATABASE_URL,pool_pre_ping=True)
SessionLocal=sessionmaker(engine,expire_on_commit=False)
def ensure_columns():
 inspector=inspect(engine)
 if 'spectrum_runs' not in inspector.get_table_names():return
 columns={column['name'] for column in inspector.get_columns('spectrum_runs')}
 with engine.begin() as connection:
  if 'trend_plan_snapshot' not in columns:connection.execute(text('ALTER TABLE spectrum_runs ADD COLUMN trend_plan_snapshot JSON'))
def get_db():
 with SessionLocal() as db: yield db

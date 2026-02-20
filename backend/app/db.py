from collections.abc import Generator

from sqlmodel import Session, create_engine

from app.config import config_manager

db_config = config_manager.get_database_config()

if db_config:
    engine = create_engine(
        str(db_config.dsn),
        pool_size=db_config.pool_size,
        max_overflow=db_config.max_overflow,
        pool_recycle=db_config.pool_recycle,
        echo=db_config.echo,
    )
else:
    engine = None


def get_session() -> Generator[Session, None, None]:
    if engine is None:
        raise RuntimeError("Database not configured")
    with Session(engine) as session:
        yield session

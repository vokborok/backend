import logging
import time

from alembic import command
from alembic.config import Config

logger = logging.getLogger(__name__)


def run_migrations_with_retry(max_retries: int = 3, delay: int = 5) -> bool:
    for attempt in range(max_retries):
        try:
            alembic_cfg = Config("alembic.ini")
            command.upgrade(alembic_cfg, "head")
            return True
        except Exception as e:
            logger.warning(f"Migration attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logger.error("All migration attempts failed")
                return False
    return False

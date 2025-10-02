from __future__ import annotations
import logging


def configure_logging() -> None:
    """Configura logging padrão da aplicação."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

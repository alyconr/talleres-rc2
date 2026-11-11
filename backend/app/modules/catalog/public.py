from app.modules.catalog.application.ports import CatalogReader
from app.modules.catalog.domain.catalog_items import AvailabilitySlot, BookableService
from app.modules.catalog.infrastructure.sqlalchemy_catalog_reader import SqlAlchemyCatalogReader


def build_catalog_reader(sessions) -> CatalogReader:
    return SqlAlchemyCatalogReader(sessions)


__all__ = [
    "AvailabilitySlot",
    "BookableService",
    "CatalogReader",
    "build_catalog_reader",
]

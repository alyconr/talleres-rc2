from datetime import datetime
from typing import Protocol

from app.modules.catalog.domain.catalog_items import AvailabilitySlot, BookableService


class CatalogReader(Protocol):
    async def get_service_name(self, tenant_id: str, service_id: str) -> str | None: ...

    async def list_bookable_services(self, tenant_id: str) -> list[BookableService]: ...

    async def get_bookable_service(
        self, tenant_id: str, service_id: str
    ) -> BookableService | None: ...

    async def list_slots(
        self,
        tenant_id: str,
        service_id: str,
        starts_after: datetime,
        ends_before: datetime,
    ) -> list[AvailabilitySlot]: ...

    async def get_slot(
        self, tenant_id: str, service_id: str, starts_at: datetime
    ) -> AvailabilitySlot | None: ...

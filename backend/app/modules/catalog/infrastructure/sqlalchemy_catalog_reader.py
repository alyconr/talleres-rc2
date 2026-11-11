from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.modules.catalog.domain.catalog_items import AvailabilitySlot, BookableService
from app.modules.catalog.infrastructure.models import AvailabilitySlotRecord, ServiceRecord


class SqlAlchemyCatalogReader:
    def __init__(self, sessions: async_sessionmaker[AsyncSession]) -> None:
        self._sessions = sessions

    async def get_service_name(self, tenant_id: str, service_id: str) -> str | None:
        async with self._sessions() as session:
            return await session.scalar(
                select(ServiceRecord.name).where(
                    ServiceRecord.tenant_id == tenant_id,
                    ServiceRecord.id == service_id,
                )
            )

    async def list_bookable_services(self, tenant_id: str) -> list[BookableService]:
        async with self._sessions() as session:
            records = await session.scalars(
                select(ServiceRecord).where(
                    *self._bookable_service_filters(tenant_id),
                )
            )
            return [service for record in records if (service := self._bookable(record))]

    async def get_bookable_service(
        self, tenant_id: str, service_id: str
    ) -> BookableService | None:
        async with self._sessions() as session:
            record = await session.scalar(
                select(ServiceRecord).where(
                    ServiceRecord.tenant_id == tenant_id,
                    ServiceRecord.id == service_id,
                    ServiceRecord.active.is_(True),
                )
            )
            if record is None:
                return None
            return self._bookable(record)

    async def list_slots(
        self,
        tenant_id: str,
        service_id: str,
        starts_after: datetime,
        ends_before: datetime,
    ) -> list[AvailabilitySlot]:
        async with self._sessions() as session:
            records = await session.scalars(
                select(AvailabilitySlotRecord)
                .join(ServiceRecord, ServiceRecord.id == AvailabilitySlotRecord.service_id)
                .where(
                    AvailabilitySlotRecord.tenant_id == tenant_id,
                    AvailabilitySlotRecord.service_id == service_id,
                    AvailabilitySlotRecord.active.is_(True),
                    *self._bookable_service_filters(tenant_id),
                    AvailabilitySlotRecord.starts_at >= starts_after,
                    AvailabilitySlotRecord.ends_at <= ends_before,
                )
                .order_by(AvailabilitySlotRecord.starts_at)
                .limit(500)
            )
            return [self._slot(record) for record in records]

    async def get_slot(
        self, tenant_id: str, service_id: str, starts_at: datetime
    ) -> AvailabilitySlot | None:
        async with self._sessions() as session:
            record = await session.scalar(
                select(AvailabilitySlotRecord)
                .join(ServiceRecord, ServiceRecord.id == AvailabilitySlotRecord.service_id)
                .where(
                    AvailabilitySlotRecord.tenant_id == tenant_id,
                    AvailabilitySlotRecord.service_id == service_id,
                    AvailabilitySlotRecord.starts_at == starts_at,
                    AvailabilitySlotRecord.active.is_(True),
                    *self._bookable_service_filters(tenant_id),
                )
            )
            return self._slot(record) if record else None

    @staticmethod
    def _bookable_service_filters(tenant_id: str) -> tuple:
        return (
            ServiceRecord.tenant_id == tenant_id,
            ServiceRecord.active.is_(True),
            ServiceRecord.deposit_amount > 0,
            ServiceRecord.deposit_amount != Decimal("NaN"),
            ServiceRecord.currency.is_not(None),
        )

    @staticmethod
    def _bookable(record: ServiceRecord) -> BookableService | None:
        amount = record.deposit_amount
        currency = record.currency
        if (
            amount is None
            or not amount.is_finite()
            or amount <= 0
            or currency is None
            or len(currency) != 3
            or not currency.isalpha()
            or currency != currency.upper()
        ):
            return None
        return BookableService(
            id=record.id,
            tenant_id=record.tenant_id,
            name=record.name,
            duration_minutes=record.duration_minutes,
            deposit_amount=amount,
            currency=currency,
        )

    @staticmethod
    def _slot(record: AvailabilitySlotRecord) -> AvailabilitySlot:
        return AvailabilitySlot(
            id=record.id,
            tenant_id=record.tenant_id,
            service_id=record.service_id,
            starts_at=record.starts_at,
            ends_at=record.ends_at,
        )


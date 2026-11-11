from decimal import Decimal

import asyncio
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.dialects import postgresql

from app.modules.catalog.infrastructure.models import ServiceRecord
from app.modules.catalog.infrastructure.sqlalchemy_catalog_reader import SqlAlchemyCatalogReader


@pytest.mark.parametrize(
    "deposit_amount",
    [Decimal("0"), Decimal("-1"), Decimal("NaN")],
    ids=["zero", "negative", "not-finite"],
)
def test_catalog_rejects_services_without_a_positive_finite_deposit(
    deposit_amount: Decimal,
) -> None:
    record = ServiceRecord(
        id="service-1",
        tenant_id="workshop-1",
        name="Cambio de aceite",
        duration_minutes=60,
        deposit_amount=deposit_amount,
        currency="COP",
        active=True,
    )

    assert SqlAlchemyCatalogReader._bookable(record) is None


def test_catalog_availability_query_excludes_nonpositive_and_nonfinite_deposits() -> None:
    class QueryCapture:
        statement = None

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_: object) -> None:
            return None

        async def scalars(self, statement):
            self.statement = statement
            return []

    session = QueryCapture()
    reader = SqlAlchemyCatalogReader(lambda: session)  # type: ignore[arg-type]
    starts_after = datetime(2026, 11, 11, tzinfo=timezone.utc)

    asyncio.run(
        reader.list_slots(
            "workshop-1", "service-1", starts_after, starts_after + timedelta(days=1)
        )
    )

    assert session.statement is not None
    compiled = session.statement.compile(dialect=postgresql.dialect())
    sql = str(compiled)
    assert "services.deposit_amount >" in sql
    assert "services.deposit_amount !=" in sql
    assert any(
        isinstance(value, Decimal) and value.is_nan()
        for value in compiled.params.values()
    )

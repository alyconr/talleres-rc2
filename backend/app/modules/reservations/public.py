from app.modules.reservations.application.create_pending_appointment import (
    CreatePendingAppointment,
)
from app.modules.reservations.application.ports import ReservationStore
from app.modules.reservations.application.booking_service import BookingService
from app.modules.reservations.application.public_types import BookingResult
from app.modules.reservations.domain.appointment import Appointment, AppointmentStatus
from app.modules.reservations.domain.availability import slots_overlap
from app.modules.reservations.infrastructure.sqlalchemy_reservation_store import (
    SqlAlchemyReservationStore,
)
from app.modules.reservations.api.routes import router


def build_reservation_store(sessions, catalog) -> ReservationStore:
    return SqlAlchemyReservationStore(sessions, catalog)

__all__ = [
    "Appointment",
    "AppointmentStatus",
    "BookingResult",
    "BookingService",
    "CreatePendingAppointment",
    "ReservationStore",
    "build_reservation_store",
    "slots_overlap",
    "router",
]

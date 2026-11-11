# TASKS: Conectar persistencia y composici?n ejecutable del flujo H001

## Implementation Tasks
- [ ] T001: Configuraci?n estricta, motor y sesiones SQLAlchemy async, metadata base y migraci?n Alembic del esquema m?nimo por m?dulo.
- [ ] T002: Adaptadores de cat?logo, reservas y pagos con persistencia tenant-scoped, transacci?n de reserva, checkout y confirmaci?n idempotente.
- [ ] T003: Caso de uso de reserva, dependencias FastAPI tipadas y composici?n/lifespan que conecte endpoints con adaptadores y Mercado Pago.
- [ ] T004: Pruebas cr?ticas de API, persistencia, concurrencia, webhook, errores de configuraci?n y aislamiento tenant; corregir arquitectura y ejecutar gates.

## Planning Notes
- Work from `requirements.md` as the source of scope.
- Validate each task against `acceptance.md`.
- Keep implementation changes inside the documented scope.

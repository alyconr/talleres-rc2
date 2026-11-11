# TASKS: Reserva p?blica de citas con anticipo en Mercado Pago

## Implementation Tasks
- [ ] T001: Scaffold mínimo con un test que pase con la estructura de .rapid-os/standards/architecture.md (un módulo de ejemplo con sus cuatro capas y su punto público). Lee la configuración de .env.example (nunca valores fijos); el esquema de datos va en migraciones versionadas; las pruebas unitarias no usan servicios externos y las de integración llevan un marcador propio, de modo que gate.tests pasa sin Docker; Dockerfile multi-stage con usuario no root y healthcheck
- [ ] Modelar las reglas de reserva y disponibilidad, con creaci?n at?mica de citas pending_payment y validaci?n del tenant.
- [ ] Implementar el m?dulo de pagos con puerto Mercado Pago, adaptador seguro, inicio del anticipo e idempotencia del webhook aprobado.
- [ ] Exponer los endpoints necesarios para consultar disponibilidad, crear reservas y recibir notificaciones de pago; integrarlos en la composici?n FastAPI.
- [ ] Implementar el flujo Angular de reserva y continuaci?n al pago con estados de carga y error controlados.
- [ ] A?adir cobertura del camino cr?tico e integraci?n del flujo completo mediante rapid check.

## Planning Notes
- Work from `requirements.md` as the source of scope.
- Validate each task against `acceptance.md`.
- Keep implementation changes inside the documented scope.

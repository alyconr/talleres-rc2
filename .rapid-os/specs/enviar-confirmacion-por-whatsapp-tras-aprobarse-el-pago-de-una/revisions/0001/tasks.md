# TASKS: Enviar confirmación por WhatsApp tras aprobarse el pago de una cita

## Implementation Tasks
- [ ] T001: Crear dominio, contratos públicos y puertos del módulo conversaciones para notificaciones WhatsApp de cita confirmada.
- [ ] T002: Persistir la notificación de forma idempotente y conectarla transaccionalmente al webhook de pago aprobado.
- [ ] T003: Implementar publicación/consumo RabbitMQ y envío mediante el puerto WhatsApp con reintentos seguros.
- [ ] T004: Añadir cobertura de integración PostgreSQL y RabbitMQ para aprobación, duplicados y fallas/reintentos.

## Planning Notes
- Work from `requirements.md` as the source of scope.
- Validate each task against `acceptance.md`.
- Keep implementation changes inside the documented scope.

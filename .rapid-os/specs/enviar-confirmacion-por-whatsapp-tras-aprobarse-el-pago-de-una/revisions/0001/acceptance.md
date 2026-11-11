# ACCEPTANCE: Enviar confirmación por WhatsApp tras aprobarse el pago de una cita

## Acceptance Criteria
- [ ] Un webhook válido de pago aprobado confirma la cita y persiste una sola notificación WhatsApp asociada al mismo tenant, cita y cliente.
- [ ] Pagos rechazados, webhooks con firma inválida y pagos con monto o moneda discordantes no producen notificación.
- [ ] Reprocesar el mismo webhook y reintentar el envío no crea ni entrega confirmaciones duplicadas.
- [ ] La notificación se envía a través de un puerto WhatsApp configurable; fallas transitorias quedan pendientes para reintento.
- [ ] Los tests de integración verifican el flujo con PostgreSQL y RabbitMQ levantados, incluyendo idempotencia y recuperación de fallas.

## Testing Strategy
- Tests de dominio y aplicación para estados, contenido mínimo, idempotencia y fallas.
- Tests API para webhooks inválidos, no aprobados y aprobados.
- Tests de integración con PostgreSQL y RabbitMQ activos para persistencia, publicación, consumo y reintento.
- Ejecutar cada comando de verificación por rapid check y validar arquitectura con rapid arch check.

## Definition of Done
- [ ] Acceptance criteria reviewed
- [ ] Testing strategy completed or explicitly deferred
- [ ] Implementation matches `requirements.md`
- [ ] Tasks in `tasks.md` are complete or intentionally deferred

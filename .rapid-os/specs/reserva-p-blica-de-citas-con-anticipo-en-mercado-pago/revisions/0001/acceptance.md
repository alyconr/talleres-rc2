# ACCEPTANCE: Reserva p?blica de citas con anticipo en Mercado Pago

## Acceptance Criteria
- [ ] El cliente puede consultar servicios activos y horarios disponibles del taller y enviar una reserva v?lida desde Angular.
- [ ] Una cita creada queda en pending_payment y su servicio, cliente y taller pertenecen al mismo tenant.
- [ ] El pago se inicia por el anticipo configurado del servicio; si la configuraci?n falta o no es v?lida, el cobro no inicia.
- [ ] La cita permanece sin confirmar ante pagos pendientes, rechazados, notificaciones inv?lidas o fallos del proveedor.
- [ ] Una notificaci?n aut?ntica de pago aprobado confirma la cita asociada y registra el pago.
- [ ] La repetici?n de una notificaci?n no crea pagos ni citas duplicados ni altera incorrectamente una cita.
- [ ] Dos solicitudes concurrentes no pueden reservar el mismo horario.
- [ ] Las respuestas p?blicas no revelan datos de otro tenant, secretos ni detalles internos.

## Testing Strategy
- Cubrir el camino cr?tico de reserva, pago aprobado y repetici?n del webhook con pytest/httpx a trav?s de rapid check.
- Verificar que pagos pendientes/rechazados, firmas inv?lidas, configuraci?n de anticipo ausente y conflictos concurrentes no confirman ni duplican citas.
- Verificar validaciones de pertenencia al tenant para servicio, horario, cliente, cita y pago.
- Verificar el flujo Angular con las pruebas disponibles del stack, sin a?adir pruebas unitarias de componentes UI salvo que sean necesarias para el camino cr?tico.

## Definition of Done
- [ ] Acceptance criteria reviewed
- [ ] Testing strategy completed or explicitly deferred
- [ ] Implementation matches `requirements.md`
- [ ] Tasks in `tasks.md` are complete or intentionally deferred

# ACCEPTANCE: Conectar persistencia y composici?n ejecutable del flujo H001

## Acceptance Criteria
- [ ] Con configuraci?n v?lida, la aplicaci?n construye y conecta los servicios; los endpoints de servicios, disponibilidad, reserva y webhook no responden 503 por falta de inyecci?n.
- [ ] El backend obtiene monto y moneda del servicio y rechaza checkout sin configuraci?n v?lida, sin aceptar esos valores desde el request.
- [ ] Una reserva crea cliente y cita pending_payment bajo el mismo tenant; solicitudes concurrentes no ocupan dos veces el mismo horario.
- [ ] El checkout asociado a la cita se persiste y la API devuelve la URL segura de Mercado Pago.
- [ ] Solo un pago consultado y aprobado, con referencia, importe y moneda coincidentes, confirma la cita.
- [ ] Webhooks repetidos y concurrentes no duplican pagos ni citas; fallos revierten el cambio y no informan ?xito.
- [ ] Migraciones aplican el esquema y los tests cr?ticos pasan mediante rapid check; rapid arch check no informa violaciones.

## Testing Strategy
- Usar rapid check -- <comando> para las pruebas backend; cubrir reservas y pagos con pruebas de aplicaci?n y persistencia en una base temporal cuando sea compatible.
- Verificar tenant isolation, horarios solapados concurrentes, falta de importe/moneda, pago rechazado, firma inv?lida/vencida, discrepancia de monto y webhook repetido.
- Verificar que la composici?n FastAPI inyecta dependencias con configuraci?n de prueba y que una configuraci?n faltante falla de forma controlada.
- Ejecutar rapid arch check y los gates autom?ticos indicados por rapid next --json.

## Definition of Done
- [ ] Acceptance criteria reviewed
- [ ] Testing strategy completed or explicitly deferred
- [ ] Implementation matches `requirements.md`
- [ ] Tasks in `tasks.md` are complete or intentionally deferred

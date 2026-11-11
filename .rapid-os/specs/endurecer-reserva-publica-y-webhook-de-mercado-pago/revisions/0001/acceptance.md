# ACCEPTANCE: Endurecer reserva pública y webhook de Mercado Pago

## Acceptance Criteria
- [ ] SEC-001 / CWE-20: cualquier digest HMAC que no sea hexadecimal ASCII de 64 caracteres se rechaza con 401 controlado y no consulta el proveedor.
- [ ] SEC-002 / CWE-862: toda consulta de ocupación de citas incluye tenant_id y los tests mantienen el aislamiento entre talleres.
- [ ] SEC-003 / CWE-400: la disponibilidad rechaza rangos mayores a 90 días y limita la consulta a 500 slots como máximo.
- [ ] SEC-004 / CWE-20: las rutas públicas rechazan fechas de cita sin zona horaria, nombres en blanco/controlados y teléfonos fuera de E.164; entradas válidas mantienen el flujo.
- [ ] Los webhooks repetidos siguen registrando un pago y una confirmación como máximo.
- [ ] Los errores de webhook y reserva no exponen secretos o trazas en respuesta ni logs.
- [ ] La suite posterior no reduce los tests aprobados de la baseline y rapid arch check pasa.

## Testing Strategy
- Registrar baseline backend y frontend en el workspace aislado.
- Añadir pruebas negativas para firma malformada, aislamiento tenant, límites y validación de campos públicos.
- Repetir el gate de pruebas que indique rapid next sin sustituir su comando.
- Ejecutar rapid arch check y revisar evidencia por hallazgo.

## Definition of Done
- [ ] Acceptance criteria reviewed
- [ ] Testing strategy completed or explicitly deferred
- [ ] Implementation matches `requirements.md`
- [ ] Tasks in `tasks.md` are complete or intentionally deferred

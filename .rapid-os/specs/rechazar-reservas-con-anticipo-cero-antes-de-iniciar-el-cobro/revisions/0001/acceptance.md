# ACCEPTANCE: Rechazar reservas con anticipo cero antes de iniciar el cobro

## Acceptance Criteria
- [ ] Un test de regresión reproduce que un servicio con anticipo 0 es rechazado con error 4xx controlado.
- [ ] El test verifica que el rechazo no crea reserva ni pago y que el adaptador de Mercado Pago no es invocado.
- [ ] Un anticipo positivo mantiene el comportamiento existente.
- [ ] La verificación definida por el run termina en verde y la arquitectura modular no presenta violaciones.

## Testing Strategy
- T001 reproduce el bug con un test que falla antes de la corrección.
- Después del arreglo, ejecutar los tests requeridos mediante rapid check -- <comando>.
- Ejecutar rapid arch check según el flujo y revisar evidencia de cada criterio de aceptación.

## Definition of Done
- [ ] Acceptance criteria reviewed
- [ ] Testing strategy completed or explicitly deferred
- [ ] Implementation matches `requirements.md`
- [ ] Tasks in `tasks.md` are complete or intentionally deferred

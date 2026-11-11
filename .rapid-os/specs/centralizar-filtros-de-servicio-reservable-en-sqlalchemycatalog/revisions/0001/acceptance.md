# ACCEPTANCE: Centralizar filtros de servicio reservable en SqlAlchemyCatalogReader

## Acceptance Criteria
- [ ] Las tres consultas usan un único sitio para construir los filtros comunes de servicio reservable.
- [ ] Los filtros conservan tenant, activo, anticipo > 0, anticipo != NaN y moneda no nula.
- [ ] La baseline y las pruebas posteriores pasan sin disminuir el número de tests aprobados.
- [ ] rapid arch check no reporta violaciones.

## Testing Strategy
- Ejecutar como baseline la suite backend con rapid check antes de editar.
- Ejecutar de nuevo la misma suite backend después del refactor y comparar resultados.
- Ejecutar rapid arch check.

## Definition of Done
- [ ] Acceptance criteria reviewed
- [ ] Testing strategy completed or explicitly deferred
- [ ] Implementation matches `requirements.md`
- [ ] Tasks in `tasks.md` are complete or intentionally deferred

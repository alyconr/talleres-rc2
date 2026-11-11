# SPEC: Centralizar filtros de servicio reservable en SqlAlchemyCatalogReader

## Title
Centralizar filtros de servicio reservable en SqlAlchemyCatalogReader

## Mode
refactor

## Business Objective
Reducir duplicación y facilitar el mantenimiento de las consultas del catálogo sin cambiar resultados observables.

## Problem Statement
SqlAlchemyCatalogReader repite en tres consultas los mismos filtros de tenant, servicio activo, anticipo positivo y distinto de NaN, y moneda presente.

## Scope
- Extraer los filtros comunes de servicio reservable a un único sitio en SqlAlchemyCatalogReader.
- Aplicar el filtro compartido a las tres consultas actuales que lo repiten.
- Preservar los predicados, parámetros y resultados de cada consulta.

## Out of Scope
- Cambios de comportamiento o de reglas de reserva.
- Cambios en BookingService, modelos de datos o endpoints.
- Añadir dependencias o ampliar el alcance a otras consultas.

## Actors / Users
- Desarrollador que mantiene el catálogo.

## Main Flow
- Registrar y ejecutar la baseline de pruebas antes del refactor.
- Centralizar los filtros compartidos y reutilizarlos en list_bookable_services, list_slots y get_slot.
- Ejecutar las mismas verificaciones y comparar los resultados con la baseline.

## Edge Cases
- El filtro debe seguir excluyendo anticipo cero, negativo y NaN.
- El filtro debe conservar el aislamiento por tenant, los servicios inactivos y la moneda nula.

## Business Rules
- El comportamiento observable y los resultados de las tres consultas no cambian.
- El número de tests pasados no disminuye respecto a la baseline.

## Technical Constraints
- Respetar Python 3.13, SQLAlchemy 2 asíncrono y la arquitectura modular existente.
- No añadir dependencias ni modificar reglas de negocio.

## Affected Files / Modules
- backend/app/modules/catalog/infrastructure/sqlalchemy_catalog_reader.py
- backend/tests/test_catalog_reader.py

## Data Impact
_Not specified._

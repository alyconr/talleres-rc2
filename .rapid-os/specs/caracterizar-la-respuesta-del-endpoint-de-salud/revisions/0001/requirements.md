# SPEC: Caracterizar la respuesta del endpoint de salud

## Title
Caracterizar la respuesta del endpoint de salud

## Mode
refactor

## Business Objective
Aumentar la confianza al mantener el endpoint de salud mediante una comprobación automatizada de su respuesta HTTP.

## Problem Statement
GET /health carece de una prueba explícita que detecte si deja de responder con HTTP 200.

## Scope
- Añadir un test que invoque GET /health y compruebe el estado HTTP 200.

## Out of Scope
- Cambiar la implementación o el comportamiento del endpoint /health.

## Actors / Users
- Desarrollador que mantiene el backend

## Main Flow
- El test realiza una petición GET /health.
- El test verifica que la respuesta tiene estado 200.

## Edge Cases
- La prueba debe seguir las convenciones existentes para probar endpoints HTTP.

## Business Rules
- El comportamiento observable no cambia; GET /health responde 200.

## Technical Constraints
- Usar las dependencias y convenciones de pruebas existentes del backend Python/FastAPI.
- No añadir dependencias.

## Affected Files / Modules
- backend

## Data Impact
_Not specified._

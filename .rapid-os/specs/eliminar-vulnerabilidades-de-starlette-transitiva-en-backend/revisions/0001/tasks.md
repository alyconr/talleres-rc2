# TASKS: Eliminar vulnerabilidades de Starlette transitiva en backend

El estado de cada tarea vive en el run: rapid status

## Implementation Tasks
- [ ] T001: Actualizar FastAPI a una versión permitida por exclude-newer cuyo rango admita Starlette >=1.3.1 y regenerar el lockfile fijado.
- [ ] T002: Corregir incompatibilidades de backend causadas por la actualización y verificar el funcionamiento.
- [ ] T003: Exportar el lockfile, verificar que pip-audit no detecta vulnerabilidades y ejecutar los checks requeridos.

## Planning Notes
- Work from `requirements.md` as the source of scope.
- Validate each task against `acceptance.md`.
- Keep implementation changes inside the documented scope.

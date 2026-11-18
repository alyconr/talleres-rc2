# TASKS: Endurecer la resolución de dependencias de frontend y backend

El estado de cada tarea vive en el run: rapid status

## Implementation Tasks
- [ ] T001: Añadir las salvaguardas de pnpm a frontend/pnpm-workspace.yaml y validar la instalación frozen.
- [ ] T002: Añadir exclude-newer a [tool.uv] del backend, refrescar opciones de uv.lock sin cambiar versiones y validar uv sync --locked.
- [ ] T003: Ejecutar la suite completa en el workspace aislado.

## Planning Notes
- Work from `requirements.md` as the source of scope.
- Validate each task against `acceptance.md`.
- Keep implementation changes inside the documented scope.

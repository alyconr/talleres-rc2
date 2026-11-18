# ACCEPTANCE: Endurecer la resolución de dependencias de frontend y backend

## Acceptance Criteria
- [ ] SEC-001 (CWE-829): frontend/pnpm-workspace.yaml declara blockExoticSubdeps: true, minimumReleaseAge: 10080 y trustPolicy: no-downgrade; pnpm 12.18.0 los acepta y pnpm install --frozen-lockfile termina sin modificar pnpm-lock.yaml.
- [ ] SEC-002 (CWE-829): backend/pyproject.toml declara exclude-newer = "7 days" en [tool.uv]; uv lock --check y uv sync --locked pasan sin cambiar ninguna versión fijada en uv.lock.
- [ ] La suite de tests del proyecto sigue pasando.
- [ ] No se usan credenciales y no se modifican archivos de .rapid-os/.

## Testing Strategy
- pnpm config get de las tres claves y pnpm install --frozen-lockfile en frontend/, comparando el lockfile.
- uv lock --check y uv sync --locked en backend/, comparando versiones de uv.lock.
- Suite completa con rapid check en el workspace aislado.

## Definition of Done
- [ ] Acceptance criteria reviewed
- [ ] Testing strategy completed or explicitly deferred
- [ ] Implementation matches `requirements.md`
- [ ] Tasks in `tasks.md` are complete or intentionally deferred

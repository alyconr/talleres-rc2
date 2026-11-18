# ACCEPTANCE: Endurecer la resolución de dependencias del frontend

## Acceptance Criteria
- [ ] El finding SEC-001 (CWE-829) queda mitigado con blockExoticSubdeps: true, minimumReleaseAge: 10080 y trustPolicy: no-downgrade en frontend/pnpm-workspace.yaml.
- [ ] pnpm 12.18.0, fijado en frontend/package.json, acepta las tres opciones de configuración.
- [ ] La instalación con el lockfile congelado termina correctamente y no modifica el lockfile.
- [ ] La plantilla backend aplicable se revisa; si requiere un ajuste equivalente para uv, se aplica y se valida; si no existe tal requisito, no se altera backend.
- [ ] No se usan credenciales y no se cambian archivos .rapid-os/.

## Testing Strategy
- Comprobar la disponibilidad de las tres claves en pnpm 12.18.0 mediante documentación oficial y/o validación de la CLI instalada.
- Ejecutar la instalación frozen en el frontend del workspace aislado.
- Comparar el lockfile antes y después de la instalación.

## Definition of Done
- [ ] Acceptance criteria reviewed
- [ ] Testing strategy completed or explicitly deferred
- [ ] Implementation matches `requirements.md`
- [ ] Tasks in `tasks.md` are complete or intentionally deferred

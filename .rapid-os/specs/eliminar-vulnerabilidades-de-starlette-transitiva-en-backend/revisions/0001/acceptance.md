# ACCEPTANCE: Eliminar vulnerabilidades de Starlette transitiva en backend

## Acceptance Criteria
- [ ] AC-SEC-161: Starlette resuelta queda en 1.3.1 o posterior y corrige PYSEC-2026-161 (CWE-444; CVSS v4.0 6.9 Medium; CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N).
- [ ] AC-SEC-2280: Starlette resuelta corrige PYSEC-2026-2280 (CWE-470; CVSS v4.0 6.9 Medium; CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N).
- [ ] AC-SEC-2281: Starlette resuelta corrige PYSEC-2026-2281 (CWE-918; CVSS v4.0 8.7 High; CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N).
- [ ] AC-SEC-248: Starlette resuelta corrige PYSEC-2026-248 (CWE-20; CVSS v4.0 6.3 Medium; CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N).
- [ ] AC-SEC-249: Starlette resuelta corrige PYSEC-2026-249 (CWE-770; CVSS v4.0 8.7 High; CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N).
- [ ] La resolución actualizada conserva el exclude-newer de siete días, queda fijada en backend/uv.lock y el lockfile exportado auditado con pip-audit no tiene vulnerabilidades.
- [ ] La suite configurada del backend pasa, incluyendo las pruebas de integración aplicables; cualquier incompatibilidad causada por la actualización queda corregida.

## Testing Strategy
- Ejecutar rapid check para los tests configurados del proyecto.
- Exportar backend/uv.lock a un archivo temporal de requirements y ejecutar pip-audit sobre esa exportación; guardar salida y código de retorno como evidencia del run.
- Comprobar que la resolución usa Starlette >=1.3.1, que FastAPI permite esa versión y que exclude-newer permanece intacto.
- Ejecutar rapid arch check si el run lo exige; no introducir cambios de arquitectura.

## Definition of Done
- [ ] Acceptance criteria reviewed
- [ ] Testing strategy completed or explicitly deferred
- [ ] Implementation matches `requirements.md`
- [ ] Tasks in `tasks.md` are complete or intentionally deferred

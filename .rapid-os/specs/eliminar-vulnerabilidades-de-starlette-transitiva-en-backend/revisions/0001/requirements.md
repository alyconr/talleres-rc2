# SPEC: Eliminar vulnerabilidades de Starlette transitiva en backend

## Title
Eliminar vulnerabilidades de Starlette transitiva en backend

## Mode
hardening

## Business Objective
Reducir la superficie de ataque del backend actualizando FastAPI y Starlette a versiones corregidas y mantener una resolución reproducible de dependencias.

## Problem Statement
pip-audit detecta cinco avisos de Starlette 0.50.0, dependencia transitiva de FastAPI 0.128.0. La restricción de FastAPI impide alcanzar Starlette 1.3.1 o posterior, versión que corrige todos los avisos indicados.

## Scope
- Actualizar FastAPI a una versión compatible con Starlette 1.3.1 o posterior y fijar las dependencias del backend.
- Respetar el exclude-newer de [tool.uv] al actualizar y regenerar backend/uv.lock.
- Resolver y corregir incompatibilidades introducidas por la actualización dentro del run.
- Exportar backend/uv.lock e inspeccionar la exportación con pip-audit.
- Registrar los cinco hallazgos de Starlette con CWE, vector CVSS v4.0, severidad y estándar aplicable.

## Out of Scope
- Cambios funcionales ajenos a la actualización de dependencias del backend.
- Cambios a la política exclude-newer o a estándares de Rapid OS.

## Actors / Users
- Equipo de desarrollo y mantenimiento del backend
- Atacante remoto que envía solicitudes HTTP malformadas o abusivas

## Main Flow
- Resolver una versión de FastAPI que permita Starlette >=1.3.1 sin ignorar exclude-newer.
- Actualizar y fijar dependencias en pyproject.toml y uv.lock.
- Corregir incompatibilidades de la aplicación si aparecen.
- Exportar el lockfile y comprobar la exportación con pip-audit.
- Ejecutar verificaciones del proyecto y revisar la evidencia de los hallazgos.

## Edge Cases
- FastAPI mantiene un límite superior de Starlette que excluye la versión corregida.
- exclude-newer impide resolver una versión recién publicada de FastAPI o Starlette.
- La versión compatible de FastAPI cambia el comportamiento o las interfaces usadas por el backend.
- pip-audit encuentra vulnerabilidades adicionales en el conjunto de dependencias exportado.

## Business Rules
- Ninguna vulnerabilidad reportada en las versiones afectadas de Starlette puede permanecer en el lockfile final.
- Las dependencias deben conservarse fijadas en el lockfile y la resolución debe respetar [tool.uv].exclude-newer = "7 days".
- Los hallazgos de seguridad incluyen CWE, vector CVSS v4.0, severidad y referencia estándar conforme a OWASP A03:2025 y la regla de hallazgos de seguridad del proyecto.

## Technical Constraints
- Backend Python 3.13, FastAPI async y uv; conservar los límites existentes de Python y el resto del stack.
- No cambiar [tool.uv].exclude-newer = "7 days" ni fijar una versión publicada durante los siete días anteriores a la resolución.
- Los avisos oficiales de GitHub para PYSEC-2026-161, PYSEC-2026-2280, PYSEC-2026-2281, PYSEC-2026-248 y PYSEC-2026-249 publican CWEs e impactos y puntuaciones CVSS 3.1; para cumplir el estándar local CVSS v4.0 se registran vectores v4 derivados de esos impactos. Para CVE-2026-54282 y CVE-2026-54283 se contrastan además vectores v4 del aviso de SUSE.
- Fuentes: https://github.com/advisories/GHSA-86qp-5c8j-p5mr ; https://github.com/advisories/GHSA-x746-7m8f-x49c ; https://github.com/advisories/GHSA-wqp7-x3pw-xc5r ; https://github.com/advisories/GHSA-jp82-jpqv-5vv3 ; https://github.com/advisories/GHSA-82w8-qh3p-5jfq ; https://www.suse.com/security/cve/CVE-2026-54282.html ; https://www.suse.com/security/cve/CVE-2026-54283.html
- La spec y la evidencia no deben contener credenciales ni secretos.

## Affected Files / Modules
- backend/pyproject.toml
- backend/uv.lock
- backend/app
- backend/tests

## Data Impact
_Not specified._

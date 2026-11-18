# SPEC: Endurecer la resolución de dependencias de frontend y backend

## Title
Endurecer la resolución de dependencias de frontend y backend

## Mode
hardening

## Business Objective
Reducir el riesgo de instalar paquetes recién publicados, de fuentes exóticas o con menor nivel de confianza (cadena de suministro) y desbloquear la CI de seguridad.

## Problem Statement
semgrep p/owasp-top-ten bloquea la CI porque frontend/pnpm-workspace.yaml no declara blockExoticSubdeps: true, minimumReleaseAge: 10080 ni trustPolicy: no-downgrade, que exige la plantilla del stack Angular. La plantilla python-fastapi exige además exclude-newer = "7 days" en [tool.uv] de backend/pyproject.toml, que tampoco está.

## Scope
- Añadir blockExoticSubdeps: true, minimumReleaseAge: 10080 y trustPolicy: no-downgrade a frontend/pnpm-workspace.yaml.
- Añadir [tool.uv] con exclude-newer = "7 days" a backend/pyproject.toml y actualizar backend/uv.lock solo en sus opciones, sin cambiar versiones.
- Verificar que pnpm 12.18.0 (packageManager) y uv admiten los ajustes y que la instalación con lockfile sigue funcionando.

## Out of Scope
- Actualizar versiones de dependencias o de herramientas.
- Cambiar los workflows de CI, archivos .rapid-os/ o añadir credenciales.

## Actors / Users
- Mantenedor del proyecto
- Atacante potencial de la cadena de suministro

## Main Flow
- El mantenedor instala dependencias con el lockfile versionado.
- pnpm y uv rechazan versiones publicadas hace menos de siete días; pnpm además rechaza subdependencias exóticas y downgrades de confianza.
- La instalación con lockfile congelado termina sin cambios en las versiones fijadas.

## Edge Cases
- La versión de pnpm fijada no reconoce una de las claves.
- Una dependencia fijada se publicó hace menos de siete días o baja de nivel de confianza.
- uv marca el lockfile como desactualizado al cambiar exclude-newer.

## Business Rules
- No se debilita ni se omite la política para hacer pasar la instalación.
- No se solicitan ni incorporan credenciales.
- Cada hallazgo se registra con CWE, vector CVSS v4.0 y cita de .rapid-os/standards/security.md.

## Technical Constraints
- Respeta el stack del proyecto (tech-stack); sin nuevas dependencias.
- Mantener packageManager pnpm@12.18.0 sin cambios.
- No modificar .rapid-os/.

## Affected Files / Modules
- frontend/pnpm-workspace.yaml
- backend/pyproject.toml
- backend/uv.lock

## Data Impact
_Not specified._

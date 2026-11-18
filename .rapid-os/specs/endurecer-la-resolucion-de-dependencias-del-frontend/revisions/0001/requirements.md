# SPEC: Endurecer la resolución de dependencias del frontend

## Title
Endurecer la resolución de dependencias del frontend

## Mode
hardening

## Business Objective
Reducir el riesgo de introducir paquetes transitivos comprometidos en la instalación del frontend.

## Problem Statement
La CI bloquea frontend/pnpm-workspace.yaml porque no expresa las salvaguardas de cadena de suministro exigidas por la plantilla del stack: bloqueo de fuentes exóticas transitivas, antigüedad mínima de publicación y política de confianza sin downgrade.

## Scope
- Configurar blockExoticSubdeps: true, minimumReleaseAge: 10080 y trustPolicy: no-downgrade en frontend/pnpm-workspace.yaml.
- Verificar que la versión fijada en frontend/package.json admite los tres ajustes.
- Instalar usando el lockfile existente en modo frozen y comprobar que el lockfile no cambia.
- Consultar la plantilla del backend para determinar si exige un ajuste equivalente en uv y aplicarlo solo si está definido.

## Out of Scope
- Actualizar dependencias, regenerar el lockfile, cambiar versiones de herramientas o añadir credenciales.
- Cambiar políticas de la CI, archivos .rapid-os/ o salvaguardas no requeridas por la plantilla.

## Actors / Users
- Mantenedor del proyecto
- Atacante potencial de la cadena de suministro

## Main Flow
- La configuración de pnpm declara explícitamente las salvaguardas solicitadas.
- El mantenedor instala las dependencias con pnpm 12.18.0 y el lockfile versionado.
- La instalación valida las políticas y conserva el lockfile.

## Edge Cases
- La versión de pnpm fijada no reconoce una de las claves.
- Una dependencia fijada en el lockfile incumple la ventana de antigüedad o la política de confianza.
- La instalación frozen propone cambios al lockfile.

## Business Rules
- No se debilita ni se omite la política para hacer pasar la instalación.
- No se solicitan ni se incorporan credenciales.
- Los hallazgos se documentan con CWE, vector CVSS v4.0 y una cita del estándar local.

## Technical Constraints
- Respetar OWASP A03:2025 y SLSA 1.2 según .rapid-os/standards/security.md.
- Mantener packageManager en frontend/package.json sin cambiar su versión.
- No modificar .rapid-os/.
- Solo modificar la configuración de uv si una plantilla backend aplicable exige explícitamente el control equivalente.

## Affected Files / Modules
- frontend/pnpm-workspace.yaml
- backend/ (solo si la plantilla exige un ajuste equivalente para uv)

## Data Impact
_Not specified._

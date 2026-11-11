# SPEC: Endurecer reserva pública y webhook de Mercado Pago

## Title
Endurecer reserva pública y webhook de Mercado Pago

## Mode
hardening

## Business Objective
Reducir riesgos de manipulación del webhook, acceso entre tenants y agotamiento de recursos en la reserva pública, protegiendo pagos y disponibilidad de los talleres.

## Problem Statement
Threat model: activos: pagos, citas y disponibilidad por tenant, datos de contacto y secreto de firma. Atacantes: clientes anónimos y remitentes de notificaciones malformadas o repetidas. Vectores: headers x-signature, query data.id y parámetros/body de rutas públicas. Mitigaciones: validación estricta antes de procesar, consultas tenant-scoped, límites de entrada y errores genéricos sin registrar secretos.

## Scope
- Validar el formato del digest HMAC del webhook y rechazar de forma controlada cualquier firma malformada.
- Aplicar tenant_id explícito a la comprobación de ocupación de disponibilidad.
- Validar fechas con zona horaria y formato de teléfono en la reserva pública.
- Limitar el intervalo y el número de resultados de consultas públicas de disponibilidad.
- Verificar idempotencia ante webhook repetido y que secretos no aparezcan en logs o respuestas.

## Out of Scope
- Cambiar reglas de pago, montos, reembolsos o vencimiento de reservas pendientes.
- Cambiar el proveedor de pagos o introducir dependencias.
- Cambiar autenticación del cliente o publicar servicios.

## Actors / Users
- Cliente que consulta servicios, disponibilidad y reserva.
- Taller dueño de la disponibilidad y los datos de citas.
- Atacante remoto que envía headers o parámetros malformados.
- Mercado Pago como emisor legítimo de webhooks firmados.

## Main Flow
- La ruta valida entradas públicas y delega únicamente parámetros válidos al servicio de reservas.
- El webhook valida una firma HMAC fresca y con digest hexadecimal válido antes de consultar Mercado Pago.
- El pago aprobado se registra una sola vez y confirma solo la cita del tenant dueño del checkout.
- Las respuestas de error son genéricas y ningún secreto se registra.

## Edge Cases
- Firma con digest no ASCII, longitud incorrecta, caracteres no hexadecimales, campos duplicados o timestamp obsoleto.
- Webhook aprobado repetido, webhook con payment id que no coincide o con checkout de otro tenant.
- Fecha de cita sin zona horaria, rango de disponibilidad invertido o excesivamente amplio.
- Teléfono con formato inválido, nombre vacío o con caracteres de control, e identificadores fuera de longitud.

## Business Rules
- Un webhook solo produce efectos tras verificar HMAC, frescura, id del pago, monto y moneda.
- Una notificación repetida no duplica pagos, citas ni confirmaciones.
- Las consultas de reserva conservan el aislamiento por tenant.
- Los errores para el cliente no exponen credenciales, firmas, trazas ni datos internos.

## Technical Constraints
- Respeta Python 3.13, FastAPI, Pydantic v2, SQLAlchemy 2 asíncrono y PostgreSQL.
- No añadir dependencias; los filtros SQL deben seguir parametrizados.
- Cada hallazgo debe conservar CWE, vector CVSS v4.0 completo, severidad y referencia al estándar del proyecto.

## Affected Files / Modules
- backend/app/modules/payments/infrastructure/webhook_signature.py
- backend/app/modules/payments/api/routes.py
- backend/app/modules/reservations/api/routes.py
- backend/app/modules/reservations/api/schemas.py
- backend/app/modules/reservations/infrastructure/sqlalchemy_reservation_store.py
- backend/app/modules/catalog/infrastructure/sqlalchemy_catalog_reader.py
- backend/tests

## Data Impact
_Not specified._

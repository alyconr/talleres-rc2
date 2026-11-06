---
rapid-doc: data-model
source: drafted
status: confirmed
sha256: fc8698f82437290bef1aaba15a0d81cfe9c57559c08c29a212bfc7be70da8ca4
---
## Entidades

- **Taller (tenant):** `id`, `name`, `status`.
- **Usuario y membresía:** usuario autenticado y vínculo a taller, con rol propuesto (`owner` o `staff`).
- **Servicio:** `id`, `tenant_id`, `name`, `duration`, `deposit_amount`, `active`; monto/porcentaje y moneda pendientes.
- **Cliente:** `id`, `tenant_id`, `name`, `phone`.
- **Disponibilidad:** `id`, `tenant_id`, intervalos o reglas de horario; recurrencia pendiente.
- **Cita:** `id`, `tenant_id`, `customer_id`, `service_id`, `starts_at`, `ends_at`, `status`.
- **Pago:** `id`, `tenant_id`, `appointment_id`, `provider`, `provider_payment_id`, `amount`, `currency`, `status`.
- **Conversación y mensaje:** conversación vinculada a tenant y cliente; mensajes con dirección, contenido, estado, canal WhatsApp e identificador externo. Proveedor exacto pendiente.

## Relaciones

- Un taller tiene membresías, servicios, disponibilidad, clientes, citas y conversaciones.
- Una cita pertenece al mismo taller que su cliente y servicio, y puede tener pagos.
- Una conversación pertenece al mismo taller que su cliente y contiene mensajes.
- Supabase Realtime notifica cambios de conversaciones/mensajes a usuarios autorizados del mismo tenant.

## Invariantes

- Todas las filas y relaciones de negocio conservan `tenant_id`; ningún usuario consulta datos de otro taller.
- La autorización verifica membresía al taller. Si FastAPI usa la clave secreta de Supabase, RLS no sustituye las comprobaciones del backend.
- Una cita no pasa a confirmada hasta que el pago del anticipo esté aprobado.
- Webhooks repetidos de Mercado Pago no duplican pagos ni confirmaciones.
- Teléfono y contenido de chats son datos personales; retención y acceso quedan sujetos a una política por definir.
- No se fija monto, cancelación o reembolso.

## Estados

- **Cita:** `pending_payment` → `confirmed` → `completed`; también puede pasar a `cancelled`, con política pendiente.
- **Pago:** `pending` → `approved`, `rejected` o `refunded`.
- **Conversación:** `open` o `closed`.
- **Mensaje:** `received`, `queued`, `sent` o `failed`.

## Base de datos local

- Producción: PostgreSQL administrado por Supabase; Supabase Realtime publica cambios autorizados.
- Desarrollo local: Rapid prepara PostgreSQL 18 y RabbitMQ 4 para compose; herramienta/versión de Supabase local, variable de conexión, datos de prueba y comando de migraciones quedan pendientes de revisar con los archivos generados.

## Tablas

Propuesta sujeta a revisión: `workshops` (PK `id`); `users` (PK `id`, identidad Supabase); `workshop_memberships` (PK `id`, FK `workshop_id` → `workshops.id`, FK `user_id` → `users.id`); `services` (PK `id`, FK `workshop_id`); `customers` (PK `id`, FK `workshop_id`); `availability_rules` (PK `id`, FK `workshop_id`); `appointments` (PK `id`, FK `workshop_id`, `customer_id`, `service_id`); `payments` (PK `id`, FK `workshop_id`, `appointment_id`); `conversations` (PK `id`, FK `workshop_id`, `customer_id`); `messages` (PK `id`, FK `workshop_id`, `conversation_id`). Las FK deben validar pertenencia al mismo taller.

## Migraciones

Pendiente de definir herramienta, carpeta y comandos para aplicar migraciones en local y en cada entorno; no se fija una convención como requisito confirmado.

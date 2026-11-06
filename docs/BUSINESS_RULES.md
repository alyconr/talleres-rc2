---
rapid-doc: business
source: drafted
status: confirmed
sha256: 0e1d4ef7ec7cee1c56a02cf2dc250bfb5d655994eeeae10d372fd01a647dd82c
---
## Objetivo

Permitir que talleres de motos en Colombia gestionen citas, anticipos y conversaciones desde un panel multitenant; el cliente reserva, paga con Mercado Pago y recibe confirmación por WhatsApp.

## Reglas no negociables

- Los datos y chats de un taller solo son visibles para ese taller y sus usuarios autorizados.
- El panel muestra en vivo los chats asociados al taller; Supabase Realtime es el mecanismo elegido.
- Una cita no queda confirmada antes de que Mercado Pago apruebe el anticipo.
- Los webhooks repetidos no deben duplicar pagos, reservas ni confirmaciones.
- No se ha fijado monto o porcentaje del anticipo ni política de cancelación o reembolso.
- El agente de IA se limita a contestar consultas de servicio; permisos y escalamiento al personal quedan por definir.

## Restricciones

- El producto se dirige a talleres y clientes en Colombia.
- Se requieren Mercado Pago y WhatsApp; el proveedor concreto de WhatsApp y el proveedor del modelo de IA están pendientes.
- Supabase aloja PostgreSQL y provee actualizaciones en vivo; Auth queda como propuesta técnica por confirmar.
- No se han definido restricciones legales, costos máximos ni fechas objetivo.

## Supuestos

- Cada taller opera como un tenant independiente.
- WhatsApp es el canal de consultas y confirmaciones; el alcance de conversaciones entrantes aún debe validarse.
- Cada dueño o empleado ve solo los datos y chats de los talleres donde tiene membresía.
- El cliente recibe confirmación cuando el pago del anticipo queda aprobado.

## Glosario

- **Taller / tenant:** negocio que gestiona sus propios servicios, citas, pagos y chats.
- **Anticipo:** pago inicial asociado a una cita; valor y condiciones pendientes.
- **Panel:** interfaz privada del taller para gestionar citas y consultar conversaciones.
- **Mercado Pago:** proveedor para cobrar el anticipo.
- **Chat:** conversación de WhatsApp asociada a un cliente y a un taller.
- **Realtime:** actualización en vivo del panel cuando cambia una conversación.

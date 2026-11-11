# SPEC: Enviar confirmación por WhatsApp tras aprobarse el pago de una cita

## Title
Enviar confirmación por WhatsApp tras aprobarse el pago de una cita

## Mode
feature

## Business Objective
Confirmar al cliente la reserva cuando Mercado Pago apruebe el anticipo.

## Problem Statement
El webhook actual confirma la cita al aprobarse el pago, pero no envía al cliente una confirmación por WhatsApp.

## Scope
- Crear el flujo del módulo conversaciones para producir y enviar la confirmación WhatsApp tras confirmar una cita.
- Procesar el mensaje de forma durable e idempotente usando RabbitMQ y persistencia transaccional.
- Proveer un puerto de aplicación para el emisor WhatsApp, sin seleccionar un proveedor concreto.

## Out of Scope
- Elegir proveedor de WhatsApp, crear credenciales o enviar mensajes reales desde este entorno.
- Conversaciones entrantes, respuestas del agente de IA, cancelaciones y reembolsos.

## Actors / Users
- Cliente que reservó una cita y pagó el anticipo.
- Mercado Pago como origen del webhook de aprobación.
- Servicio de mensajería WhatsApp configurado mediante un puerto.

## Main Flow
- Mercado Pago envía el webhook de pago aprobado.
- La API verifica firma, estado, monto y moneda.
- En una transacción se registra el pago, se confirma la cita y se guarda una única notificación pendiente.
- Un worker publica/procesa la notificación mediante el puerto WhatsApp y marca su estado.
- El cliente recibe un mensaje con la confirmación y los datos esenciales de su cita.

## Edge Cases
- Webhook inválido, pago rechazado o monto/moneda discordantes no generan confirmación.
- Webhooks repetidos no generan mensajes duplicados.
- Una falla transitoria del emisor conserva la notificación para reintento sin filtrar datos personales o secretos en logs.
- La notificación mantiene tenant_id y solo usa el teléfono del cliente de la misma cita y taller.

## Business Rules
- Según docs/BUSINESS_RULES.md: una cita no queda confirmada antes de que Mercado Pago apruebe el anticipo.
- Según docs/BUSINESS_RULES.md: los webhooks repetidos no deben duplicar pagos, reservas ni confirmaciones.
- Según docs/BUSINESS_RULES.md: el proveedor concreto de WhatsApp sigue pendiente.

## Technical Constraints
- Respetar Python 3.13, FastAPI, SQLAlchemy 2 asíncrono, PostgreSQL 18 y RabbitMQ 4.
- Respetar el monolito modular: módulo conversaciones con api, application, domain, infrastructure y public.py.
- Los módulos pagos y reservas solo pueden integrarse mediante sus contratos públicos.
- Mantener idempotencia y persistencia consistente entre confirmación de cita y notificación.
- No añadir credenciales ni seleccionar proveedor WhatsApp.

## Affected Files / Modules
- backend/app/modules/conversations
- backend/app/modules/payments
- backend/app/main.py
- backend/alembic
- backend/tests

## Data Impact
_Not specified._

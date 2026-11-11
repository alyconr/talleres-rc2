# SPEC: Rechazar reservas con anticipo cero antes de iniciar el cobro

## Title
Rechazar reservas con anticipo cero antes de iniciar el cobro

## Mode
bugfix

## Business Objective
Restablecer la regla de que una reserva no puede iniciar el cobro de Mercado Pago si el servicio tiene anticipo cero, evitando reservas y cobros inválidos.

## Problem Statement
Un taller puede configurar un servicio con anticipo de 0; el sistema permite crear una reserva e iniciar el cobro en Mercado Pago. Se espera rechazar ese flujo con un error controlado antes de crear la reserva o contactar Mercado Pago. Reproducir con un servicio activo cuyo anticipo sea 0 e intentar reservarlo y cobrarlo.

## Scope
- Reproducir el escenario con un test de regresión antes de implementar la corrección.
- Validar que el anticipo sea mayor que cero antes de confirmar/crear la reserva y antes de iniciar el cobro con Mercado Pago.
- Devolver un error controlado y verificar que no se invoque el proveedor de pagos ni se persista un cobro inválido.

## Out of Scope
- Cambiar montos, porcentajes o políticas de anticipo.
- Cambiar reglas de cancelación o reembolso.
- Refactors o mejoras no relacionadas con el defecto.

## Actors / Users
- Cliente que intenta reservar un servicio
- Taller que configura servicios y anticipos

## Main Flow
- El taller tiene un servicio activo con anticipo de 0.
- El cliente intenta crear una reserva e iniciar el pago de ese servicio.
- El sistema rechaza la operación con un error 4xx controlado antes de crear la reserva o llamar a Mercado Pago.

## Edge Cases
- Un anticipo positivo válido conserva el flujo existente de reserva y cobro.
- El rechazo no deja reserva ni pago parcial persistido.
- La respuesta de error no expone trazas internas ni detalles del proveedor.

## Business Rules
- El anticipo asociado al flujo de cobro debe ser mayor que cero.
- Una operación inválida falla de forma cerrada: no crea reservas/cobros ni invoca Mercado Pago.

## Technical Constraints
- Respeta Python 3.13, FastAPI asíncrono, Pydantic V2 estricto, SQLAlchemy 2 asíncrono y la arquitectura de monolito modular.
- Mantén autorización y validación en el servidor; no añadas dependencias.

## Affected Files / Modules
- backend/app/modules/reservas
- backend/app/modules/pagos
- backend/tests

## Data Impact
_Not specified._

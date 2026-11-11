# SPEC: Reserva p?blica de citas con anticipo en Mercado Pago

## Title
Reserva p?blica de citas con anticipo en Mercado Pago

## Mode
feature

## Business Objective
Permitir que un cliente reserve un servicio y deje la cita confirmada ?nicamente despu?s de que Mercado Pago apruebe el anticipo.

## Problem Statement
Los clientes necesitan elegir un servicio y horario de un taller, registrar la cita y pagar el anticipo sin que la reserva se confirme antes de la aprobaci?n del pago.

## Scope
- Consultar servicios activos y horarios disponibles para un taller y ofrecerlos en un flujo p?blico de reserva.
- Crear una cita pendiente de pago y asociar el cliente y servicio del mismo tenant.
- Iniciar el cobro del anticipo configurado para el servicio mediante Mercado Pago.
- Procesar la notificaci?n de pago aprobado, verificar su autenticidad y confirmar la cita de forma idempotente.
- Proveer en Angular el flujo p?blico para seleccionar servicio y horario, ingresar datos del cliente y continuar al pago.

## Out of Scope
- Panel privado para administrar servicios, disponibilidad o citas (H003).
- Confirmaciones por WhatsApp (H002), bandeja de conversaciones (H004) y agente de IA (H005).
- Definir monto o porcentaje global del anticipo, ni pol?ticas de cancelaci?n o reembolso.
- Definir un proveedor de WhatsApp o de IA.

## Actors / Users
- Cliente que realiza una reserva p?blica.
- Taller due?o de los servicios, horarios y cita.
- Mercado Pago como proveedor externo de pagos.
- Backend FastAPI que valida pertenencia al tenant y procesa la notificaci?n de pago.

## Main Flow
- El cliente abre el flujo de reserva de un taller y consulta sus servicios activos y horarios disponibles.
- El cliente selecciona servicio y horario e ingresa los datos necesarios para identificarlo.
- El backend valida que el servicio y el horario pertenecen al taller y que el horario sigue disponible; crea la cita en estado pending_payment.
- El backend obtiene el anticipo configurado para el servicio y crea la operaci?n de pago en Mercado Pago, vincul?ndola a la cita y al tenant.
- El cliente completa el pago en Mercado Pago.
- El backend valida la notificaci?n de Mercado Pago y consulta/valida el pago asociado; al aprobarse, registra el pago y transiciona la cita a confirmed.
- Las notificaciones repetidas producen el mismo resultado sin duplicar pagos ni confirmar dos veces la cita.

## Edge Cases
- El servicio est? inactivo, pertenece a otro taller o deja de estar disponible antes de crear la cita: rechazar la reserva.
- El servicio no tiene un anticipo v?lido configurado: no iniciar el cobro ni confirmar la cita; devolver un error controlado.
- Dos clientes intentan reservar el mismo horario simult?neamente: solo una reserva puede ocuparlo.
- Mercado Pago rechaza, deja pendiente o no responde: mantener la cita sin confirmar y manejar el estado de pago sin duplicar operaciones.
- La notificaci?n es inv?lida, no corresponde a la operaci?n creada o se repite: no confirmar la cita ni duplicar registros.
- El cliente env?a datos inv?lidos o excede los l?mites definidos para la petici?n: rechazarla sin persistir datos parciales.

## Business Rules
- Seg?n docs/BUSINESS_RULES.md: una cita no queda confirmada antes de que Mercado Pago apruebe el anticipo.
- Seg?n docs/BUSINESS_RULES.md: los webhooks repetidos no deben duplicar pagos, reservas ni confirmaciones.
- Seg?n docs/BUSINESS_RULES.md: los datos de un taller solo son visibles para ese taller y sus usuarios autorizados; las validaciones de tenant se aplican tambi?n al flujo p?blico.
- Seg?n docs/BUSINESS_RULES.md: no se ha fijado monto o porcentaje del anticipo ni pol?tica de cancelaci?n o reembolso.
- Seg?n docs/DATA_MODEL.md: las relaciones de cita, cliente y servicio deben validar pertenencia al mismo tenant; la cita inicia pending_payment y solo cambia a confirmed tras aprobarse el pago.
- Seg?n docs/DATA_MODEL.md: tel?fono y otros datos del cliente son datos personales y no deben exponerse ni registrarse innecesariamente.

## Technical Constraints
- Respetar el stack confirmado: backend Python 3.13, FastAPI async, Pydantic V2 estricto, SQLAlchemy 2 async, PostgreSQL y uv; frontend Angular 22 con TypeScript estricto y pnpm.
- Ubicar c?digo nuevo en los m?dulos de negocio y respetar sus capas y puntos p?blicos conforme a AGENTS.md; ning?n m?dulo accede a las capas internas de otro.
- El m?dulo de pagos integra Mercado Pago mediante puertos y adaptadores; mantener credenciales solo en el servidor.
- Validar autenticidad y contenido de notificaciones de Mercado Pago, usar operaciones idempotentes y fallar de forma cerrada.
- No inventar el monto, moneda ni pol?tica del anticipo. Usar ?nicamente una configuraci?n v?lida del servicio y bloquear el checkout si falta; documentar cualquier decisi?n t?cnica necesaria como supuesto.
- Aplicar l?mites y validaci?n a las entradas p?blicas; evitar exponer detalles internos o datos personales en errores y logs.
- Incluir modelo de amenazas breve: activos: datos de clientes, citas, credenciales y pagos; atacantes: clientes automatizados y emisores de webhooks falsos; amenazas: abuso de reservas, cruce de tenant, manipulaci?n de estado y repetici?n de eventos; mitigaciones: validaci?n de tenant, l?mites de petici?n, verificaci?n del proveedor, idempotencia y autorizaci?n del servidor.

## Affected Files / Modules
- backend/app/modules/reservations
- backend/app/modules/payments
- frontend/src/app/features/booking
- backend/app/main.py

## Data Impact
_Not specified._

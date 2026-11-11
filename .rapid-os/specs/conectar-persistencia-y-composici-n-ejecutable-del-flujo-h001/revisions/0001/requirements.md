# SPEC: Conectar persistencia y composici?n ejecutable del flujo H001

## Title
Conectar persistencia y composici?n ejecutable del flujo H001

## Mode
feature

## Business Objective
Hacer que una reserva p?blica persista y llegue a Checkout Pro, y que un webhook aprobado confirme la cita, completando H001 de extremo a extremo.

## Problem Statement
El run anterior dej? routers que dependen de servicios no configurados en app.state, por lo que las rutas responden 503. Tambi?n faltan los adaptadores de persistencia que guardan la reserva y el intento de pago.

## Scope
- Configurar SQLAlchemy async y sesiones PostgreSQL, con migraciones Alembic siguiendo el stack del proyecto.
- Implementar lectura tenant-scoped de servicios y horarios disponibles para el flujo p?blico, respetando los puntos p?blicos de los m?dulos.
- Persistir cliente, cita pending_payment, checkout e idempotencia de pagos en sus m?dulos propietarios.
- Orquestar el flujo de reserva y pago y confirmar la cita solamente despu?s de consultar un pago aprobado y validar monto, moneda, referencia y firma.
- Conectar los casos de uso y adaptadores en la composici?n FastAPI; retirar la dependencia de servicios ausentes en app.state y devolver respuestas controladas cuando falte configuraci?n.
- A?adir pruebas cr?ticas de API, persistencia, aislamiento tenant, conflicto de horario, pago aprobado, eventos repetidos y firma inv?lida.

## Out of Scope
- Panel de administraci?n de servicios, disponibilidad y citas (H003).
- Confirmaciones por WhatsApp (H002), bandeja en vivo (H004) y agente IA (H005).
- Fijar montos, porcentajes, moneda global, pol?tica de cancelaciones o reembolsos; se usa solo una configuraci?n v?lida del servicio y se rechaza el checkout si falta.
- Definir Supabase Auth o el host productivo de FastAPI.

## Actors / Users
- Cliente que consulta el cat?logo p?blico y reserva.
- Mercado Pago como proveedor de checkout y notificaciones.
- API FastAPI que valida el tenant y aplica los cambios de estado.
- Taller propietario de los servicios, horarios, clientes, citas y pagos.

## Main Flow
- FastAPI carga configuraci?n, crea el motor y la f?brica de sesiones al arrancar e inyecta los casos de uso y adaptadores en sus routers.
- El cliente consulta solo servicios activos y horarios del tenant indicado.
- La API valida el servicio, su configuraci?n de anticipo y el horario disponible dentro del mismo tenant; en una transacci?n crea o recupera al cliente y crea la cita pending_payment sin permitir solapamientos concurrentes.
- El backend crea Checkout Pro con el importe y moneda configurados para el servicio, asocia la referencia de la cita y persiste el checkout antes de devolver su URL.
- Al recibir una notificaci?n, la API verifica HMAC y vigencia, consulta el pago actual en Mercado Pago y valida referencia, tenant, importe y moneda.
- Una transacci?n registra el pago una sola vez y confirma la cita; una repetici?n produce el mismo estado sin duplicados.

## Edge Cases
- DATABASE_URL o credenciales de Mercado Pago faltantes: fallar de forma cerrada y no aceptar reservas ni webhooks como procesados.
- Servicio o horario de otro tenant, inactivo o ya ocupado: no persistir la reserva y devolver un error gen?rico apropiado.
- Servicio sin importe o moneda v?lidos: no crear checkout ni confirmar la cita.
- Fallo de Mercado Pago al crear checkout: no dejar una cita ocupando el horario sin un checkout utilizable.
- Pago pendiente, rechazado, con firma vencida/inv?lida, referencia incorrecta, o monto/moneda distintos: no confirmar la cita.
- Webhook repetido o concurrente: persistir un ?nico pago y mantener confirmaci?n idempotente.
- Error de base de datos: revertir la transacci?n y no informar ?xito al cliente.

## Business Rules
- Seg?n docs/BUSINESS_RULES.md: una cita no queda confirmada antes de que Mercado Pago apruebe el anticipo.
- Seg?n docs/BUSINESS_RULES.md: webhooks repetidos no duplican pagos, reservas ni confirmaciones.
- Seg?n docs/BUSINESS_RULES.md: los datos de un taller solo son visibles para ese taller y sus usuarios autorizados.
- Seg?n docs/BUSINESS_RULES.md: no se ha fijado monto o porcentaje del anticipo ni pol?tica de cancelaci?n o reembolso.
- Seg?n docs/DATA_MODEL.md: cliente, servicio, disponibilidad, cita y pago conservan tenant_id; la cita inicia pending_payment y solo cambia a confirmed tras pago aprobado.
- Seg?n docs/DATA_MODEL.md: las relaciones deben validar pertenencia al mismo taller y los tel?fonos son datos personales que no deben registrarse innecesariamente.

## Technical Constraints
- Respetar Python 3.13, FastAPI async, Pydantic V2 estricto, SQLAlchemy 2 async, asyncpg, PostgreSQL y Alembic; fijar dependencias exactas y actualizar uv.lock.
- Seguir la arquitectura modular: cada m?dulo es due?o de sus tablas y otros m?dulos consumen solo public.py; shared/ no importa m?dulos.
- Usar dependencias FastAPI tipadas y ra?z de composici?n en backend/app/main.py; cerrar el motor y clientes en el lifespan.
- No permitir que el navegador env?e o determine el importe del anticipo; el backend toma el valor del servicio.
- Verificar la firma HMAC con comparaci?n en tiempo constante y consultar el recurso real en Mercado Pago; no confiar en el cuerpo del webhook como estado de pago.
- Modelo de amenazas: activos: datos de cliente, citas, pagos y secretos; atacantes: clientes automatizados y emisores falsos de webhooks; amenazas: cruce de tenant, abuso de horarios, alteraci?n de pagos y replay; mitigaciones: validaci?n tenant-scoped, l?mites de entrada, transacciones con protecci?n de concurrencia, firma vigente, consulta al proveedor e idempotencia.
- La recurrencia de disponibilidad, retenci?n de datos y pol?tica de expiraci?n de pagos pendientes permanecen sin definir; no introducir esas reglas en este cambio.

## Affected Files / Modules
- backend/app/shared
- backend/app/modules/catalog
- backend/app/modules/reservations
- backend/app/modules/payments
- backend/app/main.py
- backend/alembic
- backend/tests
- backend/pyproject.toml
- backend/uv.lock

## Data Impact
_Not specified._

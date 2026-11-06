# Rapid OS Compiled Context

## Task

Mode: research
Harness: codex
Objective: Decidir qu? alternativa integrar para conversaciones y confirmaciones por WhatsApp, con evidencia sobre viabilidad en Colombia, costo total y carga operativa para talleres multitenant.
Affected Paths: experiments/whatsapp-provider-spike

## Business Rules

> Supuestos redactados por el agente, no confirmados por la persona.

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

## Architecture

> Supuestos redactados por el agente, no confirmados por la persona.

## Decisión

Aplicación con frontend y backend separados: Angular para la reserva pública y el panel privado del taller; Python/FastAPI como API. El backend será un monolito modular, con aislamiento multitenant por taller. Supabase alojará PostgreSQL y dará Realtime para actualizar la bandeja de chats; Supabase Auth se propone para identidad y acceso, pendiente de confirmar. RabbitMQ procesará trabajos de pagos y mensajería.

## Por qué

El panel y el flujo público necesitan una interfaz, mientras que FastAPI ya fue elegido como backend en Python. Separarlos mantiene la API como punto de entrada de las reglas de negocio. Las actualizaciones en vivo de la bandeja pueden usar Supabase Realtime. Pagos y conversaciones integran proveedores externos y requieren reintentos, por eso se proponen como módulos hexagonales.

## Alternativas descartadas

- Una sola aplicación fullstack en Next.js: se conserva FastAPI como backend elegido y se separa Angular.
- PostgreSQL autogestionado en producción: Supabase reduce la operación de base de datos para este MVP; el motor sigue siendo PostgreSQL.
- Kafka para actualizaciones en vivo: no se añade; Supabase Realtime cubre el panel.
- Llamar a Mercado Pago y WhatsApp directamente desde cada endpoint: los módulos de pagos y conversaciones aíslan esos proveedores y usan RabbitMQ para procesar trabajos.

## Consecuencias

- Se operan y despliegan frontend y backend separados.
- Supabase reduce la operación de PostgreSQL, pero crea dependencia del proveedor. FastAPI debe validar el tenant en cada operación; las claves secretas permanecen en el servidor porque omiten RLS.
- RabbitMQ añade configuración y operación, a cambio de procesar trabajos y reintentar fallos.
- Cada registro de negocio lleva `tenant_id`; RLS y la autorización del backend deben impedir acceso cruzado.
- WhatsApp, el proveedor de IA, la política de reintentos y los términos de anticipo siguen pendientes.

## Módulos

- **Identidad y talleres** — talleres, membresías y roles; tablas `workshops`, `workshop_memberships`. Capas estándar.
- **Catálogo y agenda** — servicios y disponibilidad; tablas `services`, `availability_rules`. Capas estándar.
- **Reservas** — clientes y citas; tablas `customers`, `appointments`. Capas estándar; las reglas de horario y confirmación quedan en este módulo.
- **Pagos** — pagos y conciliación de eventos de Mercado Pago; tabla `payments`. Hexagonal, con puertos para proveedor de pagos y cola; adaptadores en `infrastructure/`.
- **Conversaciones** — conversaciones, mensajes, confirmaciones y agente de IA; tablas `conversations`, `messages`. Hexagonal, con puertos para WhatsApp, modelo de IA, RabbitMQ y actualizaciones de Supabase; adaptadores en `infrastructure/`.
- **Panel Angular** — funcionalidades de reserva pública y gestión privada; consume la API y se suscribe a Realtime con identidad autorizada.

## Reglas de dependencia

- Cada módulo vive en `backend/app/modules/<módulo>/` con las capas: api, application, domain, infrastructure.
- api puede importar: application, domain.
- application puede importar: domain.
- domain puede importar: ninguna otra capa.
- infrastructure puede importar: application, domain.
- Un módulo solo importa de otro su punto público (`public.py`), nunca una de sus capas.
- `backend/app/shared` no importa ningún módulo.
- domain no importa: fastapi, sqlalchemy, starlette, httpx.
- Cada módulo vive en `frontend/src/app/features/<módulo>/` con las capas: ui, state, data-access, model.
- ui puede importar: state, model.
- state puede importar: data-access, model.
- data-access puede importar: model.
- model puede importar: ninguna otra capa.
- Un módulo solo importa de otro su punto público (`index.ts`), nunca una de sus capas.
- `frontend/src/app/shared` no importa ningún módulo.
- model no importa: react, react-dom, vue, svelte, @angular/core, next, nuxt, @sveltejs/kit, astro.

## Servicios de infraestructura

- **database / PostgreSQL 18 / ahora:** alojado por Supabase en producción; Rapid prepara PostgreSQL local para desarrollo. Lo usan Identidad, Catálogo, Reservas, Pagos y Conversaciones. El brief requiere guardar citas, pagos y conversaciones.
- **queue / RabbitMQ 4 / ahora:** procesa eventos y reintentos en Pagos y Conversaciones. El brief requiere confirmación tras pagar por Mercado Pago y WhatsApp.
- **Supabase Realtime:** capacidad del proveedor para actualizar la bandeja en vivo; no se añade Kafka como servicio separado.

## Integraciones externas

Mercado Pago para anticipos y webhooks; WhatsApp para mensajes y chats (proveedor por elegir); un modelo de IA para el agente (proveedor por elegir); Supabase para PostgreSQL, Realtime y, como propuesta pendiente, Auth.

## Proveedor BaaS

Supabase administra PostgreSQL y ofrece Realtime para el panel. Se propone Supabase Auth para identidad, con membresías y autorización por taller en FastAPI. FastAPI conserva las reglas de reservas, pagos, aislamiento tenant y llamadas con claves secretas; Angular no recibe secretos de servidor. RLS protege consultas autorizadas y Realtime solo debe publicar cambios que el usuario puede leer.

# ARQUITECTURA: MONOLITO MODULAR

Esta es una regla, no una sugerencia. Todo código nuevo la cumple. Rapid OS la verifica en cada run con `rapid arch check` (gate `gate.architecture`).

Las responsabilidades son las mismas en todos los lenguajes: **entrada** (HTTP, eventos), **aplicación** (casos de uso y puertos), **dominio** (reglas sin framework), **infraestructura** (persistencia y adaptadores) y el **contrato público** del módulo. Lo que cambia es el nombre de la carpeta o del paquete y el mecanismo que hace público el contrato; ambos están en «Estructura por stack», más abajo.

## Módulos por capacidad de negocio

- Organiza el sistema en **módulos por capacidad de negocio** (por ejemplo: citas, pagos, talleres), nunca en capas globales (`controllers/`, `services/`, `models/` en la raíz).
- Un módulo es una capacidad que el negocio nombraría sin hablar de tecnología. Si dudas entre dos módulos, es uno solo hasta que haya una razón para separarlos.

## Estructura de cada módulo

Cada módulo tiene exactamente estas piezas, con los nombres de tu stack:

- entrada: HTTP, eventos y esquemas de entrada y salida;
- aplicación: casos de uso. Aquí viven los puertos (interfaces) si el módulo es hexagonal;
- dominio: entidades, reglas e invariantes. Sin framework web ni ORM;
- infraestructura: repositorios, ORM y adaptadores de sistemas externos;
- un **único punto público**: lo único que otros módulos pueden usar.

## Dirección de dependencias

- entrada -> aplicación -> dominio.
- infraestructura -> aplicación y dominio (implementa los puertos).
- El dominio no importa nada de las otras capas ni librerías de framework web, ORM o clientes externos.
- El punto público expone lo que el módulo ofrece y puede usar las capas de su propio módulo.

## Entre módulos

- Un módulo solo usa el **punto público** de otro módulo. Nunca sus capas.
- Cada módulo es **dueño de sus tablas**: otro módulo no las lee ni las escribe directamente. Si necesita esos datos, los pide por el punto público.

## shared/

- `shared/` es un núcleo mínimo: configuración, sesión de base de datos y errores base.
- `shared/` no importa ningún módulo. Si algo de `shared/` empieza a depender de un módulo, ese código pertenece a un módulo.

## Cuándo un módulo es hexagonal

Usa puertos y adaptadores (los puertos en la capa de aplicación, los adaptadores en la de infraestructura) cuando el módulo:

- integra un sistema externo (pagos, mensajería, IA, correo);
- tiene un dominio con reglas complejas que deben probarse sin infraestructura;
- o se prevé cambiar de proveedor.

Un CRUD simple no necesita hexagonal: repositorio directo en infraestructura y casos de uso simples en aplicación.

## Por qué esta forma

- No se empieza con microservicios: un monolito modular da los mismos límites con un solo despliegue, y un módulo con su punto público y sus tablas propias se extrae después si hace falta.
- No se usan capas globales: obligan a tocar toda la raíz por cada cambio y la migración posterior a módulos es costosa; empezar por módulos evita esa migración.

## Estructura por stack

### python-fastapi — backend (en `backend/`)

```text
app/
  main.py                      # composición: crea la app y conecta los módulos
  shared/                      # configuración, sesión de BD, errores base
  modules/
    <m>/
      public.py                # único punto público del módulo
      api/                     # rutas y esquemas
      application/             # casos de uso (y puertos si es hexagonal)
      domain/                  # entidades, reglas, invariantes
      infrastructure/          # repositorios, ORM, adaptadores
```

Módulos en `backend/app/modules/<m>/`; contrato público: public.py.

Cada módulo tiene:

- `api/`: entrada: HTTP, eventos y esquemas de entrada y salida.
- `application/`: casos de uso; aquí viven los puertos si el módulo es hexagonal.
- `domain/`: entidades, reglas e invariantes, sin framework web ni ORM.
- `infrastructure/`: repositorios, ORM y adaptadores de sistemas externos.
- **Un único punto público** (`public.py`): lo único que otros módulos pueden usar.

| Nombre en este stack | Responsabilidad canónica |
|---|---|
| `api` | Entrada (HTTP, eventos) |
| `application` | Aplicación (casos de uso y puertos) |
| `domain` | Dominio (reglas sin framework) |
| `infrastructure` | Infraestructura (persistencia y adaptadores) |
| `public.py` | Contrato público del módulo |

El `__init__.py` de un módulo está vacío o solo reexporta desde su `public.py`; nunca importa de `api`, `application`, `domain` ni `infrastructure`. Si no, importar el paquete del módulo sería una puerta trasera a sus capas.

### angular — frontend (en `frontend/`)

```text
src/app/
  shared/                      # componentes y utilidades mínimas, sin importar funcionalidades
  features/
    <f>/
      index.ts                 # único punto público de la funcionalidad
      ui/                      # componentes
      state/                   # estado
      data-access/             # llamadas a la API
      model/                   # tipos y reglas de presentación
```

Módulos en `frontend/src/app/features/<f>/`; contrato público: index.ts.

Cada módulo tiene:

- `ui/`: componentes de la funcionalidad.
- `state/`: estado de la funcionalidad.
- `data-access/`: llamadas a la API.
- `model/`: tipos y reglas de presentación, sin framework de interfaz.
- **Un único punto público** (`index.ts`): lo único que otros módulos pueden usar.

| Nombre en este stack | Responsabilidad canónica |
|---|---|
| `ui` | Interfaz (componentes) |
| `state` | Estado de la funcionalidad |
| `data-access` | Acceso a datos (llamadas a la API) |
| `model` | Modelo (tipos y reglas de presentación) |
| `index.ts` | Contrato público del módulo |

Los imports son relativos o por ruta absoluta desde `src/`.

## Verificación

- Ejecuta `rapid arch check` antes de dar una tarea por terminada. Informa cada violación con archivo, línea, import y regla.
- La regla en forma de máquina está en `.rapid-os/standards/architecture.json`. Nunca desactives ni edites `.rapid-os/standards/architecture.json` para que un check pase: cambia el código o pide a la persona que cambie la regla.
- Un proyecto existente no se migra de golpe: la regla aplica al código nuevo, dentro de la carpeta de módulos. La migración se hace con `/rapid-refactor`.

## Topology

# 🏗️ TOPOLOGY: SEPARATED FRONTEND & BACKEND

## ARCHITECTURE
- **Type:** Decoupled.
- **Frontend:** Consumer (Next.js/React).
- **Backend:** Provider (Python FastAPI / Go / Node).
- **Database:** Separate (PostgreSQL / MongoDB).
- **Communication:** REST API or GraphQL.

## DATA STRATEGY
- **Frontend:** NEVER access the DB directly. ALWAYS fetch from the Backend API.
- **Contracts:** Use TypeScript interfaces mirroring the API DTOs.

## Technical Stack

# 🐍 TECH STACK: PYTHON FASTAPI
- **Runtime:** Python 3.13 (taken from the Python that runs Rapid OS; edit this line if the project targets another version).
- **Framework:** FastAPI (Async).
- **Validation:** Pydantic V2 (Strict).
- **Testing:** pytest + httpx (AsyncClient).
- **Linting:** Ruff.
- **Package manager:** uv.
- **ORM:** SQLAlchemy 2 (async) + Alembic (migrations).
- **Database:** PostgreSQL 18 + asyncpg.
- **Queue:** RabbitMQ 4 + aio-pika.
- **Version Control:** Git.
- **Orchestration:** to decide, not imposed. Options: LangGraph, CrewAI, LangChain or the model provider's own SDK. Record the choice and why in docs/ARCHITECTURE.md before adding a dependency.
<!-- rapid-stack: backend=python-fastapi -->

# 🅰️ TECH STACK: ANGULAR
- **Runtime:** Node.js 24 (Active LTS), TypeScript strict.
- **Framework:** Angular 22 (standalone components, signals).
- **Routing:** Angular Router.
- **Data:** HttpClient.
- **Testing:** Vitest (default in new projects) with `ng test`.
- **Linting:** ESLint + angular-eslint.
- **Package manager:** pnpm.
- **Version Control:** Git.
<!-- rapid-stack: frontend=angular -->

## Task Specifications

# SPEC: Spike: ?API de WhatsApp Cloud directa o un proveedor (Twilio, 360dialog)?

## Title
Spike: ?API de WhatsApp Cloud directa o un proveedor (Twilio, 360dialog)?

## Mode
research

## Business Objective
Decidir qu? alternativa integrar para conversaciones y confirmaciones por WhatsApp, con evidencia sobre viabilidad en Colombia, costo total y carga operativa para talleres multitenant.

## Problem Statement
El proyecto requiere WhatsApp para chats de clientes y confirmaciones de citas, pero el proveedor est? pendiente. Se debe comparar integrar directamente WhatsApp Cloud API de Meta frente a Twilio y 360dialog, considerando diferencias en alta de n?meros y talleres, webhooks, plantillas, soporte, precios y requisitos de operaci?n.

## Scope
- Comparar WhatsApp Cloud API directa, Twilio y 360dialog con los mismos criterios y supuestos de volumen.
- Verificar disponibilidad y requisitos oficiales para operar desde Colombia, alta y propiedad de n?meros, plantillas, ventanas de conversaci?n, webhooks y soporte.
- Estimar costo total mensual para escenarios expl?citos de mensajes de servicio y plantillas, separando cargos del proveedor y cargos de Meta cuando apliquen.
- Evaluar onboarding multitenant: qui?n conecta y posee el n?mero, credenciales y tokens, aislamiento por taller, operaci?n de webhooks, reintentos y baja del proveedor.
- Documentar fuentes oficiales, supuestos, riesgos, matriz comparativa y recomendaci?n con nivel de confianza.

## Out of Scope
- Implementar la integraci?n de WhatsApp o a?adir dependencias y credenciales.
- Elegir o contratar un proveedor, registrar n?meros o crear cuentas de WhatsApp Business.
- Dise?ar una migraci?n definitiva de datos o cambiar la arquitectura aprobada.

## Actors / Users
- Equipo que decidir? la integraci?n de conversaciones
- Due?o o administrador del taller que conectar? el canal
- Personal que operar? mensajes y confirmaciones

## Main Flow
- Fijar escenarios y criterios comparables para un MVP en Colombia.
- Revisar documentaci?n y precios oficiales vigentes de Meta, Twilio y 360dialog.
- Comparar requisitos de alta, operaci?n multitenant, webhooks, plantillas, soporte y salida del proveedor.
- Registrar fuentes, supuestos, brechas de evidencia y costo por escenario.
- Recomendar una alternativa y documentar las condiciones que cambiar?an la recomendaci?n.

## Edge Cases
- Precios o requisitos dependen del pa?s, moneda, categor?a del mensaje, volumen o fecha de consulta.
- Un proveedor no publica tarifas o no confirma un requisito para Colombia; registrar el dato como no verificado en vez de inferirlo.
- Los n?meros de los talleres requieren onboarding individual o no pueden compartirse con la plataforma.
- Cambios de tarifa o pol?ticas de Meta alteran la comparaci?n; fechar cada fuente consultada.

## Business Rules
- Seg?n docs/BUSINESS_RULES.md, WhatsApp es un canal requerido para mensajes y chats, pero el proveedor concreto est? pendiente.
- Seg?n docs/BUSINESS_RULES.md, los datos y chats de un taller solo son visibles para ese taller y sus usuarios autorizados.
- Seg?n docs/ARCHITECTURE.md, conversaciones es un m?dulo hexagonal con puertos para WhatsApp; el proveedor debe permanecer detr?s de ese l?mite.
- No almacenar ni exponer tokens, secretos ni datos personales reales durante la investigaci?n.

## Technical Constraints
- Respetar el monolito modular FastAPI y el l?mite p?blico del m?dulo de conversaciones documentado en docs/ARCHITECTURE.md.
- No a?adir dependencias ni modificar c?digo de producci?n durante el spike.
- Usar fuentes primarias oficiales para precios, productos, onboarding y pol?ticas; anotar URL y fecha de consulta.
- Separar cargos de Meta, cargos del proveedor, costos operativos y supuestos de volumen; no comparar cifras con bases distintas.

## Affected Files / Modules
- experiments/whatsapp-provider-spike

## Data Impact
_Not specified._

## Implementation Tasks

# TASKS: Spike: ?API de WhatsApp Cloud directa o un proveedor (Twilio, 360dialog)?

## Implementation Tasks
- [ ] T001: Definir escenarios, supuestos y criterios de comparaci?n para el MVP colombiano.
- [ ] T002: Investigar y comparar Meta Cloud API directa, Twilio y 360dialog; guardar hallazgos con fuentes en experiments/whatsapp-provider-spike/T002.md y adjuntarlos.
- [ ] T003: Documentar la decisi?n recomendada, confianza, riesgos y condiciones de revisi?n en experiments/whatsapp-provider-spike/T003.md y adjuntarla.

## Planning Notes
- Work from `requirements.md` as the source of scope.
- Validate each task against `acceptance.md`.
- Keep implementation changes inside the documented scope.

## Acceptance Criteria

# ACCEPTANCE: Spike: ?API de WhatsApp Cloud directa o un proveedor (Twilio, 360dialog)?

## Acceptance Criteria
- [ ] La matriz compara las tres opciones con criterios y escenarios de volumen expl?citos.
- [ ] Cada afirmaci?n sobre precio, disponibilidad o requisitos tiene fuente oficial y fecha, o queda marcada como no verificada.
- [ ] Se documentan costos estimados, supuestos, riesgos multitenant y costos de salida para cada alternativa.
- [ ] La conclusi?n recomienda una opci?n para el MVP, expresa confianza y enumera qu? dato podr?a cambiarla.
- [ ] Los hallazgos y la recomendaci?n quedan adjuntos como evidencia del run mediante rapid attach.

## Testing Strategy
- No se requieren tests de c?digo para este spike; validar manualmente la matriz, consistencia de escenarios, enlaces oficiales y trazabilidad de la recomendaci?n.

## Definition of Done
- [ ] Acceptance criteria reviewed
- [ ] Testing strategy completed or explicitly deferred
- [ ] Implementation matches `requirements.md`
- [ ] Tasks in `tasks.md` are complete or intentionally deferred

## Project Intelligence

Database:
- postgres

Deployment:
- github-actions

## Product Brief

> Supuestos redactados por el agente, no confirmados por la persona.

## Problema

Los talleres de motos en Colombia necesitan recibir reservas, cobrar anticipos y atender consultas de clientes desde un flujo claro. El taller requiere un panel multitenant para gestionar sus datos y ver en vivo los chats de sus propios clientes.

## Usuarios

- **Cliente:** consulta servicios, agenda una cita, paga el anticipo con Mercado Pago y conversa por WhatsApp sobre la reserva o el servicio.
- **Dueño o personal del taller:** administra servicios, disponibilidad y citas desde el panel; consulta los chats de su taller en vivo.
- **Agente de IA:** responde consultas de clientes sobre servicios por WhatsApp; sus permisos y límites quedan por definir.

## Historias

- [ ] H001: Como cliente, quiero elegir un servicio y horario disponible, reservar la cita y pagar el anticipo con Mercado Pago para dejar confirmada mi reserva.
- [ ] H002: Como cliente, quiero recibir por WhatsApp la confirmación de mi cita cuando se apruebe el pago.
- [ ] H003: Como dueño de taller, quiero administrar servicios, disponibilidad y citas en un panel para gestionar mi operación.
- [ ] H004: Como dueño de taller, quiero consultar en vivo los chats de clientes que reservan o preguntan por mis servicios, aislados de otros talleres.
- [ ] H005: Como cliente, quiero consultar por WhatsApp a un agente de IA sobre los servicios del taller.

Señales de éxito: citas confirmadas tras aprobarse el pago; los chats aparecen en vivo en el panel correcto; ningún taller accede a datos o chats de otro. Monto y política del anticipo, cancelaciones y reembolsos quedan pendientes.

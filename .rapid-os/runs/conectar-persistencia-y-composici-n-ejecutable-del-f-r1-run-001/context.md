# Rapid OS Compiled Context

## Task

Mode: feature
Harness: codex
Objective: Hacer que una reserva p?blica persista y llegue a Checkout Pro, y que un webhook aprobado confirme la cita, completando H001 de extremo a extremo.
Affected Paths: backend/alembic, backend/app/main.py, backend/app/modules/catalog, backend/app/modules/payments, backend/app/modules/reservations, backend/app/shared, backend/pyproject.toml, backend/tests, backend/uv.lock
Tags: story:h001

## Security Rules

# SEGURIDAD: BASE OBLIGATORIA

Estas reglas son obligatorias para todo código nuevo y todo cambio. Cada regla cita entre corchetes el estándar que la respalda. La velocidad nunca rebaja esta base.

## Nivel de verificación

- Este proyecto verifica OWASP ASVS 5.0.0 nivel L1. Revisa cada cambio contra los requisitos de ese nivel. [OWASP ASVS 5.0.0, https://github.com/OWASP/ASVS]

## OWASP Top 10:2025

### A01 Broken Access Control

- Deniega por omisión: toda operación privada comprueba autenticación y autorización en el servidor, nunca solo en el cliente. [OWASP A01:2025, CWE-862]
- Comprueba que el usuario sea dueño del recurso antes de leerlo o modificarlo; un id recibido nunca basta. [OWASP A01:2025, CWE-639]

### A02 Security Misconfiguration

- La configuración de producción es explícita: sin modo debug, sin cuentas ni credenciales por defecto, sin puertos ni endpoints de administración expuestos. [OWASP A02:2025, CWE-16]
- Envía las cabeceras de seguridad HTTP y limita CORS a los orígenes necesarios, nunca `*` con credenciales. [OWASP A02:2025]

### A03 Software Supply Chain Failures

- Declara y fija cada dependencia; revisa una dependencia nueva antes de añadirla y prefiere las mantenidas. [OWASP A03:2025, CWE-1104]
- Las dependencias se auditan en cada PR (el workflow `rapid-security-<lenguaje>.yml` ya lo hace); un hallazgo alto o crítico bloquea el merge. [OWASP A03:2025]

### A04 Cryptographic Failures

- Cifra en tránsito (TLS) y en reposo los datos sensibles; no inventes criptografía, usa las bibliotecas estándar. [OWASP A04:2025, CWE-327]
- Guarda las contraseñas solo con un algoritmo de hash lento y con sal (Argon2id, scrypt o bcrypt); nunca en claro ni con hash rápido. [OWASP A04:2025, CWE-916]
- Ningún secreto, llave ni token en el repositorio, en los logs ni en el código del cliente; usa un gestor de secretos. [OWASP A04:2025, CWE-798]

### A05 Injection

- Usa consultas parametrizadas y APIs seguras; nunca construyas SQL, comandos de shell, rutas ni plantillas concatenando texto. [OWASP A05:2025, CWE-89, CWE-78]
- Escapa la salida según su contexto (HTML, atributos, URL, JavaScript) y valida toda entrada externa: tipo, longitud y valores permitidos. [OWASP A05:2025, CWE-79]

### A06 Insecure Design

- Diseña con modelo de amenazas: lo que el sistema nunca debe permitir se escribe como regla y se prueba. [OWASP A06:2025]
- Limita por diseño lo abusable: límites de intentos, de tamaño y de tasa en las operaciones que el negocio no quiere que se repitan sin freno. [OWASP A06:2025]

### A07 Authentication Failures

- Limita los intentos de autenticación y bloquea o retrasa la fuerza bruta; los mensajes de error no revelan si el usuario existe. [OWASP A07:2025, CWE-307]
- Las sesiones y tokens expiran, se invalidan al cerrar sesión y se regeneran al autenticar. [OWASP A07:2025, CWE-613]

### A08 Software or Data Integrity Failures

- No deserialices datos no confiables con formatos que ejecutan código; valida el esquema antes de usar el dato. [OWASP A08:2025, CWE-502]
- Verifica la integridad de lo que se instala o se descarga (lockfile con hashes, firmas o sumas de verificación). [OWASP A08:2025]

### A09 Security Logging and Alerting Failures

- Registra los eventos de seguridad (autenticación, denegaciones de acceso, cambios de permisos) con identificador de usuario y de petición, y haz que lleguen a alguien que pueda reaccionar. [OWASP A09:2025, CWE-778]
- No registres secretos, contraseñas, tokens ni datos personales innecesarios. [OWASP A09:2025, CWE-532]

### A10 Mishandling of Exceptional Conditions

- Falla de forma cerrada: ante un error, la operación se deniega, nunca se concede. [OWASP A10:2025]
- Maneja cada ruta de error y de tiempo agotado; el cliente recibe un error genérico y el detalle queda solo en el log. [OWASP A10:2025, CWE-209]


## OWASP API Security Top 10:2023

- API1 Broken Object Level Authorization: autoriza por objeto en cada endpoint que recibe un id; comprueba que el usuario autenticado puede acceder a ese objeto concreto. [OWASP API1:2023, CWE-639]
- API2 Broken Authentication: la autenticación de la API usa un mecanismo estándar, limita los intentos y no acepta tokens sin firmar ni caducados. [OWASP API2:2023]
- API3 Broken Object Property Level Authorization: define esquemas de salida explícitos sin campos sensibles y rechaza la asignación masiva (acepta solo los campos permitidos de entrada). [OWASP API3:2023, CWE-915]
- API4 Unrestricted Resource Consumption: impón límites de tamaño de petición, paginación con tope y límites de tasa en toda API. [OWASP API4:2023, CWE-770]
- API5 Broken Function Level Authorization: cada función administrativa o privilegiada comprueba el rol en el servidor. [OWASP API5:2023]
- API6 Unrestricted Access to Sensitive Business Flows: protege los flujos de negocio abusables (compras, registros, reservas) con límites y detección de automatización. [OWASP API6:2023]
- API7 Server Side Request Forgery: valida y restringe con una lista permitida toda URL que el servidor vaya a consultar por indicación del usuario. [OWASP API7:2023, CWE-918]
- API8 Security Misconfiguration: aplica la configuración segura también a la API (CORS estricto, métodos permitidos, sin trazas de error en las respuestas). [OWASP API8:2023]
- API9 Improper Inventory Management: mantén un inventario de endpoints y versiones; retira lo que ya no se usa y no expongas entornos de prueba. [OWASP API9:2023]
- API10 Unsafe Consumption of APIs: valida la firma y el contenido de los webhooks y de las respuestas de terceros antes de usarlos; trátalos como entrada no confiable. [OWASP API10:2023]

## NIST SSDF (SP 800-218)

- PO (Prepare the Organization): esta base es el requisito de seguridad del proyecto; toda spec la cita y toda historia la cumple. [NIST SP 800-218 PO]
- PS (Protect Software): el código y los artefactos viven en un repositorio con acceso controlado; ningún secreto en el repositorio. [NIST SP 800-218 PS]
- PW (Produce Well-Secured Software): la spec de toda historia que toque autenticación, pagos o datos personales incluye un modelo de amenazas breve (activos, quién ataca, cómo, y la mitigación). [NIST SP 800-218 PW]
- PW: todo cambio pasa la revisión humana del gate final de Rapid OS y los escaneos de CI (secretos, análisis estático, dependencias) antes del merge. [NIST SP 800-218 PW]
- RV (Respond to Vulnerabilities): toda vulnerabilidad se trata con su severidad CVSS: crítica y alta se corrigen antes de publicar, media en el siguiente ciclo, y de cada una se anota la causa raíz. [NIST SP 800-218 RV]

## Cadena de suministro (SLSA 1.2)

- Versiona el lockfile y fija las dependencias a versiones exactas en todos los proyectos. [SLSA 1.2, OWASP A03:2025]
- Fija las acciones de CI por SHA completo del commit, con la versión en un comentario; nunca por etiqueta ni por rama. [SLSA 1.2, OWASP A03:2025]

## Hallazgos: CWE y CVSS

- Todo hallazgo de seguridad se reporta con su CWE (https://cwe.mitre.org/) y su vector CVSS v4.0 (`CVSS:4.0/...`), la severidad que resulta y la regla de este archivo que lo cubre. [CWE, CVSS v4.0]

## Seguridad de IA (LLM y agentes)

Aplica a todo componente que use modelos o agentes. [OWASP Top 10 for LLM Applications 2025, OWASP Top 10 for Agentic Applications 2026]

- La salida del modelo es entrada no confiable: valídala y trátala antes de usarla en consultas, comandos, HTML o llamadas a otros sistemas. [LLM05:2025 Improper Output Handling]
- Defiéndete de la inyección de instrucciones: separa las instrucciones de los datos, no obedezcas instrucciones que lleguen dentro de documentos, correos o páginas, y limita lo que un texto externo puede provocar. [LLM01:2025 Prompt Injection, ASI01 Agent Goal Hijack]
- Las herramientas del agente están en una lista permitida y con el mínimo privilegio: solo lo que la tarea necesita, con credenciales propias y acotadas. [LLM06:2025 Excessive Agency, ASI02 Tool Misuse and Exploitation, ASI03 Identity and Privilege Abuse]
- Las acciones irreversibles (pagos, borrados, mensajes a clientes) requieren aprobación humana explícita. [LLM06:2025 Excessive Agency, ASI09 Human-Agent Trust Exploitation]
- Ningún secreto en los prompts ni en la memoria del agente; la memoria y el contexto recuperado se tratan como no confiables. [LLM02:2025 Sensitive Information Disclosure, LLM07:2025 System Prompt Leakage, ASI06 Memory & Context Poisoning]
- Fija límites de costo y de iteraciones por petición y por usuario, con corte automático. [LLM10:2025 Unbounded Consumption, ASI08 Cascading Failures]
- Verifica el origen de los modelos, datos y herramientas que el agente incorpora (cadena de suministro de IA) y no ejecutes código generado sin aislamiento. [LLM03:2025 Supply Chain, ASI04 Agentic Supply Chain Vulnerabilities, ASI05 Unexpected Code Execution (RCE)]

<!-- Fuentes verificadas:
OWASP ASVS 5.0.0: https://github.com/OWASP/ASVS
OWASP Top 10:2025: https://top10.owasp.org/2025
OWASP API Security Top 10:2023: https://owasp.org/API-Security/editions/2023/en/0x11-t10/
OWASP Top 10 for LLM Applications 2025: https://genai.owasp.org/llm-top-10/
OWASP Top 10 for Agentic Applications for 2026: https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/
NIST SP 800-218 (SSDF 1.1): https://csrc.nist.gov/pubs/sp/800/218/final
SLSA 1.2: https://slsa.dev/spec/v1.2/
CVSS v4.0: https://www.first.org/cvss/v4-0/specification-document
CWE: https://cwe.mitre.org/
-->

## Business Rules

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

## Coding Rules

# 🚀 MVP CODING RULES (VELOCITY FIRST)

## PHILOSOPHY
- **Ship It:** Functionality > Perfection. Code cleanliness is secondary to working features.
- **YAGNI:** You Aren't Gonna Need It. Do not over-engineer or create abstractions for future use cases.

## STANDARDS
1. **Testing:** Only write tests for critical paths (e.g., Payments, Auth). Skip unit tests for UI components.
2. **Comments:** Only comment complex logic. Self-documenting code is preferred.
3. **Refactoring:** Postpone refactoring until after the feature is validated by users.
4. **Base:** La velocidad nunca rebaja la base de seguridad ni la arquitectura modular.

## Task Specifications

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

## Acceptance Criteria

# ACCEPTANCE: Conectar persistencia y composici?n ejecutable del flujo H001

## Acceptance Criteria
- [ ] Con configuraci?n v?lida, la aplicaci?n construye y conecta los servicios; los endpoints de servicios, disponibilidad, reserva y webhook no responden 503 por falta de inyecci?n.
- [ ] El backend obtiene monto y moneda del servicio y rechaza checkout sin configuraci?n v?lida, sin aceptar esos valores desde el request.
- [ ] Una reserva crea cliente y cita pending_payment bajo el mismo tenant; solicitudes concurrentes no ocupan dos veces el mismo horario.
- [ ] El checkout asociado a la cita se persiste y la API devuelve la URL segura de Mercado Pago.
- [ ] Solo un pago consultado y aprobado, con referencia, importe y moneda coincidentes, confirma la cita.
- [ ] Webhooks repetidos y concurrentes no duplican pagos ni citas; fallos revierten el cambio y no informan ?xito.
- [ ] Migraciones aplican el esquema y los tests cr?ticos pasan mediante rapid check; rapid arch check no informa violaciones.

## Testing Strategy
- Usar rapid check -- <comando> para las pruebas backend; cubrir reservas y pagos con pruebas de aplicaci?n y persistencia en una base temporal cuando sea compatible.
- Verificar tenant isolation, horarios solapados concurrentes, falta de importe/moneda, pago rechazado, firma inv?lida/vencida, discrepancia de monto y webhook repetido.
- Verificar que la composici?n FastAPI inyecta dependencias con configuraci?n de prueba y que una configuraci?n faltante falla de forma controlada.
- Ejecutar rapid arch check y los gates autom?ticos indicados por rapid next --json.

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

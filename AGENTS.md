# RAPID OS - CODEX PROJECT INSTRUCTIONS
# SOURCE OF TRUTH FOR CODEX.


### 🛑 TECH STACK
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


### 🛑 TOPOLOGY
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

### 🛑 ARCHITECTURE
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


### 🛑 SECURITY
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


### 🛑 CODING RULES
# 🚀 MVP CODING RULES (VELOCITY FIRST)

## PHILOSOPHY
- **Ship It:** Functionality > Perfection. Code cleanliness is secondary to working features.
- **YAGNI:** You Aren't Gonna Need It. Do not over-engineer or create abstractions for future use cases.

## STANDARDS
1. **Testing:** Only write tests for critical paths (e.g., Payments, Auth). Skip unit tests for UI components.
2. **Comments:** Only comment complex logic. Self-documenting code is preferred.
3. **Refactoring:** Postpone refactoring until after the feature is validated by users.
4. **Base:** La velocidad nunca rebaja la base de seguridad ni la arquitectura modular.


### 📄 BRIEF DEL PRODUCTO
## Problema

Los talleres de motos en Colombia necesitan recibir reservas, cobrar anticipos y atender consultas de clientes desde un flujo claro. El taller requiere un panel multitenant para gestionar sus datos y ver en vivo los chats de sus propios clientes.

## Usuarios

- **Cliente:** consulta servicios, agenda una cita, paga el anticipo con Mercado Pago y conversa por WhatsApp sobre la reserva o el servicio.
- **Dueño o personal del taller:** administra servicios, disponibilidad y citas desde el panel; consulta los chats de su taller en vivo.
- **Agente de IA:** responde consultas de clientes sobre servicios por WhatsApp; sus permisos y límites quedan por definir.

## Historias

- [x] H001: Como cliente, quiero elegir un servicio y horario disponible, reservar la cita y pagar el anticipo con Mercado Pago para dejar confirmada mi reserva.
- [x] H002: Como cliente, quiero recibir por WhatsApp la confirmación de mi cita cuando se apruebe el pago.
- [ ] H003: Como dueño de taller, quiero administrar servicios, disponibilidad y citas en un panel para gestionar mi operación.
- [ ] H004: Como dueño de taller, quiero consultar en vivo los chats de clientes que reservan o preguntan por mis servicios, aislados de otros talleres.
- [ ] H005: Como cliente, quiero consultar por WhatsApp a un agente de IA sobre los servicios del taller.

Señales de éxito: citas confirmadas tras aprobarse el pago; los chats aparecen en vivo en el panel correcto; ningún taller accede a datos o chats de otro. Monto y política del anticipo, cancelaciones y reembolsos quedan pendientes.

### 📄 REGLAS DE NEGOCIO
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

### 📄 MODELO DE DATOS
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

### 📄 ARQUITECTURA
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

### 📄 DESPLIEGUE
## Destino

- **Frontend Angular:** Cloudflare Pages. El comando de build y la carpeta de salida se fijarán cuando Rapid genere el frontend.
- **API FastAPI:** host de contenedores por elegir. Este borrador conserva Python/FastAPI con SQLAlchemy asíncrono.
- **RabbitMQ 4:** el mismo proveedor de contenedores, como servicio separado.
- **Base de datos:** PostgreSQL administrado por Supabase; elegir región al crear el proyecto.
- **Chats en vivo:** Supabase Realtime con políticas para que cada taller vea solo sus conversaciones.

## Configuración y secretos

- El entorno local usa `compose.yaml` para PostgreSQL y RabbitMQ; producción conecta FastAPI a Supabase y al RabbitMQ desplegado.
- Credenciales de PostgreSQL, RabbitMQ, Mercado Pago, WhatsApp y el proveedor de IA viven en el almacén de secretos del host de API.
- La clave pública de Supabase puede usarse en el frontend para Auth/Realtime si se confirma ese diseño. La clave secreta y credenciales de pago nunca se exponen al navegador ni al repositorio.
- Variables de Cloudflare Pages se limitan a valores públicos de compilación.

## Servicios gestionados

- Cloudflare Pages sirve el frontend Angular y sus assets.
- Supabase administra PostgreSQL y Realtime; Auth permanece como propuesta.
- El proveedor de contenedores para FastAPI y RabbitMQ sigue pendiente.
- No se usa Cloudflare Workers para la API en esta propuesta, para conservar el stack FastAPI elegido.

## Verificación y reversión

- Verificar carga del panel, API saludable, reserva y pago de prueba, separación entre tenants y actualización en vivo del chat.
- Si falla el frontend, restaurar el despliegue anterior de Pages. Si falla la API o RabbitMQ, restaurar la imagen anterior en el proveedor de contenedores.
- El procedimiento concreto y la región de Supabase se definirán cuando se elija el host. Este borrador no representa un despliegue realizado ni verificado.

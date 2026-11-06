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

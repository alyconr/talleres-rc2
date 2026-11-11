---
rapid-doc: deployment
source: drafted
status: confirmed
sha256: a6b610a35b1c886f7297b9ddbb8dc7e36373302f73ff4d5dda494882cc87627c
---
## Destino

- **Frontend Angular:** Workers con Static Assets es el destino recomendado por Cloudflare para proyectos nuevos. Fijar comando de build y directorio de salida cuando Rapid genere el frontend. Pages sigue siendo opción si el proyecto ya está alojado allí.
- **API y cola:** conservar FastAPI asíncrono y RabbitMQ 4 en un proveedor de contenedores por elegir. El backend y la cola no se han desplegado.
- **Datos y chat:** PostgreSQL y Realtime en Supabase. Aplicar autorización por taller en FastAPI y políticas de Realtime para aislar conversaciones. El cliente usa solo credenciales públicas autorizadas.

## Encaje del stack y salidas

FastAPI en Python Workers usa `asgi.entrypoint` y `pywrangler`, pero no admite SQLAlchemy async por falta de `greenlet`. Hyperdrive con PostgreSQL requiere `compatibility_date` 2026-09-08 o posterior.

1. **Recomendado:** Angular en Workers Static Assets; FastAPI async y RabbitMQ 4 en un proveedor de contenedores. Conserva el stack y la semántica actual.
2. **API en Python Workers:** adaptar el acceso a datos a modo síncrono, usar `asgi.entrypoint`/`pywrangler` y Hyperdrive. Requiere cambios de código y no está implementado.
3. **Cloudflare Queues:** alternativa a RabbitMQ que requiere cambiar el adaptador. La entrega es al menos una vez, por lotes y con reintentos; los consumidores deben ser idempotentes para evitar duplicar pagos, reservas y confirmaciones.
4. **Cloudflare Containers:** evaluar en Workers Paid para ejecutar imágenes desde un Worker. Validar soporte y operación de FastAPI y RabbitMQ antes de elegirlo; no se asume compatibilidad.

## Configuración y secretos

- Configurar `wrangler.jsonc` con bindings, `compatibility_date`, flags y entornos explícitos; `vars` y bindings no se heredan.
- Con `compatibility_date` desde 2026-08-04, Node.js compatibility viene activa; antes, añadir `nodejs_compat` si hace falta.
- Guardar secretos con `wrangler secret put <NOMBRE>`, nunca en config, código ni frontend. En local usar `.dev.vars` o `.env` junto a Wrangler, no ambos, y excluir `.dev.vars*` y `.env*` de Git.
- Mantener credenciales de PostgreSQL, RabbitMQ, Mercado Pago, WhatsApp, IA y Supabase secret en el almacén del servicio o CI que las use. No incluir valores en el repositorio ni exponerlos al navegador.
- Si un Worker conecta a Supabase PostgreSQL con Hyperdrive, usar la cadena Direct connection; Hyperdrive gestiona el pool. Conectar con `pg` o Postgres.js, no con el cliente JavaScript de Supabase.
- Migraciones y Edge Functions de Supabase se gestionan desde CI con Supabase CLI, no Wrangler; guardar allí `SUPABASE_ACCESS_TOKEN` y `SUPABASE_DB_PASSWORD` como secretos.

## Servicios gestionados

| Componente | Destino |
|---|---|
| Angular | Cloudflare Workers Static Assets; build pendiente. Pages si ya se usa. |
| FastAPI async | Host de contenedores por elegir; no es compatible sin adaptación a Python Workers. |
| RabbitMQ 4 | Servicio separado en host por elegir; Queues requiere cambio de semántica. |
| PostgreSQL y Realtime | Supabase; región pendiente. |
| Migraciones / Edge Functions | Supabase CLI desde CI, cuando se configure. |

Rapid Setup indica que la persona levanta PostgreSQL y RabbitMQ locales con `docker compose up -d`; migraciones y pruebas de integración usan `DATABASE_URL` de `.env` cuando estén disponibles.

## Verificación y reversión

Borrador de preparación: no hay servicios desplegados ni verificados. Antes de publicar, elegir host API/cola, región Supabase, dominios, entornos, build y almacenes de secretos.

- Workers admite gradual: `wrangler versions upload` carga y `wrangler versions deploy` reparte tráfico; `wrangler deploy` envía al 100 %.
- Verificar frontend, salud de API, reserva y pago de prueba, aislamiento entre talleres y actualización de chats. Si se adopta una cola de entrega al menos una vez, verificar idempotencia.
- `wrangler rollback` o el panel devuelve Workers a una versión anterior, pero no restaura recursos conectados. Cambios incompatibles de esquema pueden romper el código anterior. Definir rollback de API y RabbitMQ con el proveedor elegido.

## Fuentes oficiales

- [Workers Static Assets](https://developers.cloudflare.com/workers/static-assets/), [Pages](https://developers.cloudflare.com/pages/) y [límites](https://developers.cloudflare.com/workers/platform/limits/)
- [FastAPI en Python Workers](https://developers.cloudflare.com/workers/languages/python/packages/fastapi/), [Hyperdrive](https://developers.cloudflare.com/hyperdrive/) y [Containers](https://developers.cloudflare.com/containers/)
- [Wrangler config y secretos](https://developers.cloudflare.com/workers/wrangler/configuration/), [Queues](https://developers.cloudflare.com/queues/)
- [Supabase Realtime](https://supabase.com/docs/guides/realtime), [gestión de entornos](https://supabase.com/docs/guides/deployment/managing-environments) y [Workers deployments](https://developers.cloudflare.com/workers/versions-and-deployments/)

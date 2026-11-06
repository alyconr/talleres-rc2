---
rapid-doc: deployment
source: drafted
status: confirmed
sha256: 600048a16a84f4022956d08bafe53a0d03fd2d0bfa4ab8efe3f9777b5dbf2caf
---
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

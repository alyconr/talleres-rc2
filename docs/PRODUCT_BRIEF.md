---
rapid-doc: brief
source: drafted
status: confirmed
sha256: fe70e058d443384cac906d17f72f78720f13f41a2830d8e26fafed10157b7607
---
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

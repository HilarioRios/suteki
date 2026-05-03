import os
import logging
import httpx
from fastapi import Request
from agent.providers.base import ProveedorWhatsApp, MensajeEntrante

logger = logging.getLogger("agentkit")


class ProveedorWhapi(ProveedorWhatsApp):

    def __init__(self):
        self.token = os.getenv("WHAPI_TOKEN")
        self.url_envio = "https://gate.whapi.cloud/messages/text"

    def parsear_body(self, body: dict) -> list[MensajeEntrante]:
        logger.info(f"Parseando body Whapi: keys={list(body.keys())}")
        mensajes = []
        for msg in body.get("messages", []):
            tipo = msg.get("type", "")
            from_me = msg.get("from_me", False)
            texto = msg.get("text", {}).get("body", "").strip()
            chat_id = msg.get("chat_id", "")
            msg_id = msg.get("id", "")

            logger.info(f"Mensaje: tipo={tipo}, from_me={from_me}, chat_id={chat_id}, texto={texto[:50]}")

            if tipo != "text" or not texto:
                continue

            mensajes.append(MensajeEntrante(
                telefono=chat_id,
                texto=texto,
                mensaje_id=msg_id,
                es_propio=from_me,
            ))
        return mensajes

    async def enviar_mensaje(self, telefono: str, mensaje: str) -> bool:
        if not self.token:
            logger.warning("WHAPI_TOKEN no configurado")
            return False
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient() as client:
            r = await client.post(
                self.url_envio,
                json={"to": telefono, "body": mensaje},
                headers=headers,
            )
            if r.status_code != 200:
                logger.error(f"Error Whapi envio: {r.status_code} — {r.text}")
            else:
                logger.info(f"Mensaje enviado OK a {telefono}")
            return r.status_code == 200

from abc import ABC, abstractmethod
from dataclasses import dataclass
from fastapi import Request


@dataclass
class MensajeEntrante:
    telefono: str
    texto: str
    mensaje_id: str
    es_propio: bool


class ProveedorWhatsApp(ABC):

    @abstractmethod
    def parsear_body(self, body: dict) -> list[MensajeEntrante]:
        """Extrae mensajes del body ya parseado como dict."""
        ...

    @abstractmethod
    async def enviar_mensaje(self, telefono: str, mensaje: str) -> bool:
        ...

    async def parsear_webhook(self, request: Request) -> list[MensajeEntrante]:
        """Compatibilidad — usa parsear_body internamente."""
        import json
        raw = await request.body()
        body = json.loads(raw)
        return self.parsear_body(body)

    async def validar_webhook(self, request: Request) -> dict | int | None:
        return None

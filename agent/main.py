import os
import json
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, JSONResponse
from dotenv import load_dotenv

from agent.brain import generar_respuesta
from agent.memory import inicializar_db, guardar_mensaje, obtener_historial
from agent.providers import obtener_proveedor

load_dotenv()

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("agentkit")

proveedor = obtener_proveedor()
PORT = int(os.getenv("PORT", 8000))


@asynccontextmanager
async def lifespan(app: FastAPI):
    await inicializar_db()
    logger.info(f"Servidor AgentKit en puerto {PORT}")
    logger.info(f"Proveedor: {proveedor.__class__.__name__}")
    yield


app = FastAPI(title="Nigiri San", version="1.0.0", lifespan=lifespan)


@app.get("/")
async def health_check():
    return {"status": "ok", "agente": "Nigiri San", "negocio": "Suteki Sushi & Pokes"}


@app.get("/webhook")
async def webhook_verificacion(request: Request):
    resultado = await proveedor.validar_webhook(request)
    if resultado is not None:
        return PlainTextResponse(str(resultado))
    return {"status": "ok"}


@app.post("/webhook")
async def webhook_handler(request: Request):
    try:
        raw = await request.body()
        logger.info(f"Webhook raw: {raw[:800].decode('utf-8', errors='ignore')}")

        if not raw:
            return JSONResponse({"status": "ok"})

        try:
            body = json.loads(raw)
        except Exception:
            logger.warning("Body no es JSON")
            return JSONResponse({"status": "ok"})

        mensajes = proveedor.parsear_body(body)

        for msg in mensajes:
            if msg.es_propio or not msg.texto:
                continue

            logger.info(f"Procesando mensaje de {msg.telefono}: {msg.texto}")

            try:
                historial = await obtener_historial(msg.telefono)
                respuesta = await generar_respuesta(msg.texto, historial)
                await guardar_mensaje(msg.telefono, "user", msg.texto)
                await guardar_mensaje(msg.telefono, "assistant", respuesta)
                await proveedor.enviar_mensaje(msg.telefono, respuesta)
                logger.info(f"Respuesta enviada a {msg.telefono}: {respuesta[:100]}")
            except Exception as e:
                logger.error(f"Error procesando mensaje: {e}", exc_info=True)

    except Exception as e:
        logger.error(f"Error en webhook: {e}", exc_info=True)

    return JSONResponse({"status": "ok"})

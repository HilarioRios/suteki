import os
import yaml
import logging

logger = logging.getLogger("agentkit")


def cargar_info_negocio() -> dict:
    try:
        with open("config/business.yaml", "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.error("config/business.yaml no encontrado")
        return {}


def obtener_horario() -> dict:
    info = cargar_info_negocio()
    return info.get("negocio", {}).get("horario", {})


def obtener_locales() -> list:
    info = cargar_info_negocio()
    return info.get("negocio", {}).get("locales", [])


def obtener_link_pedidos() -> str:
    info = cargar_info_negocio()
    return info.get("negocio", {}).get("web_pedidos", "https://pedir.suteki.com.ar")


def buscar_en_menu(consulta: str) -> str:
    knowledge_dir = "knowledge"
    resultados = []

    if not os.path.exists(knowledge_dir):
        return "No hay archivos de conocimiento disponibles."

    for archivo in os.listdir(knowledge_dir):
        ruta = os.path.join(knowledge_dir, archivo)
        if archivo.startswith(".") or not os.path.isfile(ruta):
            continue
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                contenido = f.read()
                if consulta.lower() in contenido.lower():
                    resultados.append(f"[{archivo}]: {contenido[:800]}")
        except (UnicodeDecodeError, IOError):
            continue

    if resultados:
        return "\n---\n".join(resultados)
    return "No encontre informacion especifica sobre eso en el menu."


def registrar_queja(telefono: str, descripcion: str) -> str:
    logger.warning(f"QUEJA recibida de {telefono}: {descripcion}")
    return "Queja registrada correctamente."


def escalar_a_local(telefono_cliente: str, local: str = None) -> dict:
    locales = obtener_locales()
    if local:
        for l in locales:
            if local.lower() in l["nombre"].lower():
                return l
    return locales[0] if locales else {}

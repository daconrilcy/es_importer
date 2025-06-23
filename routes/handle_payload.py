from typing import Union, Dict

from flask import request
from werkzeug.exceptions import BadRequest

import logging

logger = logging.getLogger(__name__)


def handle_json_payload() -> Union[Dict, bool]:
    """
    Helper pour charger et valider un payload JSON POST.
    """
    try:
        payload = request.get_json(force=True)
    except BadRequest:
        logger.error("Payload JSON non valide : Handle json payload: Requête JSON malformée reçue.")
        return False
    if not isinstance(payload, dict):
        logger.error("Payload JSON non valide : doit être un dictionnaire.")
        return False
    return payload
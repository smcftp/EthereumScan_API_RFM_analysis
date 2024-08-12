from typing import Optional, Literal

import logging
from requests import Response
from requests.exceptions import JSONDecodeError


def wordpress_response_handler(
    response: Response,
    action: Literal["update", "upload"],
    entity: Literal["post", "media"]
) -> Optional[int]:
    """Handles response and log helpful messages"""
    logging.info(f" | {entity.capitalize()} | {action} | {response} |")
    if response.status_code in (200, 201):
        try:
            entity_id = response.json()["id"]
            logging.info(f"{entity} with {entity}_id={entity_id} {action} successfully".capitalize())
            return entity_id
        except JSONDecodeError:
            pass
    logging.info(f"Failed to {action} {entity}")
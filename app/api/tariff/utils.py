from datetime import datetime
from enum import Enum
from typing import Any


class ActionType(str, Enum):
    CREATE_TARIFF = "create_tariff"
    CALCULATE_INSURANCE_COST = "calculate_insurance_cost"
    UPDATE_TARIFF = "update_tariff"
    DELETE_TARIFF = "delete_tariff"


def create_message(
    action: ActionType,
    date_accession_id: int | None = None,
    updated_at: str | None = None,
    tariff_id: int | None = None,
) -> dict[str, Any]:
    message = {
        "action": action.value,
        "date_accession_id": date_accession_id,
        "updated_at": updated_at,
        "tariff_id": tariff_id,
        "timestamp": str(datetime.now()),
    }
    # Удаляем ключи с значениями None
    return {k: v for k, v in message.items() if v is not None}

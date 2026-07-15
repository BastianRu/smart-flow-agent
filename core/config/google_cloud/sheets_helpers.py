"""Tutorial rápido para usar Google Sheets con Python.

Este módulo muestra las operaciones básicas de lectura y escritura usando la
Google Sheets API con credenciales OAuth ya configuradas.

Requisitos:
- Tener configuradas las variables CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN,
  ACCESS_TOKEN, TOKEN_EXPIRY en .env
- Tener habilitada la API de Google Sheets en Google Cloud Console
- Tener el scope:
    https://www.googleapis.com/auth/spreadsheets

Ejemplo de uso:
    from core.config.google_cloud.sheets_helpers import (
        get_sheets_service,
        read_sheet_values,
        append_rows,
        update_range,
    )
"""

from googleapiclient.discovery import build

from core.config.google_cloud.google_cloud import get_credentials, log_and_raise_google_error


def get_sheets_service():
    """suport function."""
    creds = get_credentials()
    return build("sheets", "v4", credentials=creds)


def read_sheet_values(spreadsheet_id: str, range_name: str):
    """Reads data from a sheet.

    use:
        read_sheet_values("1ABC123", "Hoja1!A1:D10")

    response:
        {
            "range": "Hoja1!A1:D10",
            "majorDimension": "ROWS",
            "values": [
                ["Nombre", "Edad", "Ciudad"],
                ["Ana", "25", "Bogotá"],
            ],
        }
    """
    try:
        service = get_sheets_service()
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name,
        ).execute()

        # result["values"] contiene las filas leídas.
        # if range is empty, result.get("values") may returns None.
        return result
    except Exception as exc:
        log_and_raise_google_error("read_sheet_values", exc)


def append_rows(spreadsheet_id: str, range_name: str, rows):
    """add rows at the end of a range.

    Use:
        append_rows("1ABC123", "Hoja1!A1", [["Ana", 25, "Bogotá"]])

    response:
        {
            "spreadsheetId": "1ABC123",
            "tableRange": "Hoja1!A1:Z1000",
            "updates": {
                "spreadsheetId": "1ABC123",
                "updatedRange": "Hoja1!A101:C101",
                "updatedRows": 1,
                "updatedColumns": 3,
                "updatedCells": 3,
            }
        }
    """
    try:
        service = get_sheets_service()
        body = {"values": rows}
        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="USER_ENTERED",
            body=body,
        ).execute()
        return result
    except Exception as exc:
        log_and_raise_google_error("append_rows", exc)


def update_range(spreadsheet_id: str, range_name: str, rows):
    """updates a range with specific values.

    example:
        update_range("1ABC123", "Hoja1!A2:C2", [["Luis", 30, "Medellín"]])

    response:
        {
            "spreadsheetId": "1ABC123",
            "updatedRange": "Hoja1!A2:C2",
            "updatedRows": 1,
            "updatedColumns": 3,
            "updatedCells": 3,
        }
    """
    try:
        service = get_sheets_service()
        body = {"values": rows}
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="USER_ENTERED",
            body=body,
        ).execute()
        return result
    except Exception as exc:
        log_and_raise_google_error("update_range", exc)


def clear_range(spreadsheet_id: str, range_name: str):
    """Removes data from a specific range.

    response:
        {
            "spreadsheetId": "1ABC123",
            "clearedRange": "Hoja1!A1:C10"
        }
    """
    try:
        service = get_sheets_service()
        result = service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range=range_name,
        ).execute()
        return result
    except Exception as exc:
        log_and_raise_google_error("clear_range", exc)


def batch_update(spreadsheet_id: str, requests):
    """

    schema:
        requests = [
            {
                "updateCells": {
                    "range": {"sheetId": 0, "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": 0, "endColumnIndex": 1},
                    "rows": [{"values": [{"userEnteredValue": {"stringValue": "Hola"}}]}],
                    "fields": "userEnteredValue",
                }
            }
        ]
        batch_update("1ABC123", requests)

    response schema:
        {
            "spreadsheetId": "1ABC123",
            "replies": [
                {"updateCells": {"range": {...}, "updatedRows": 1, "updatedColumns": 1, "updatedCells": 1}}
            ]
        }
    """
    try:
        service = get_sheets_service()
        result = service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": requests},
        ).execute()
        return result
    except Exception as exc:
        log_and_raise_google_error("batch_update", exc)


# ---------------------------
# Test code space 
# ---------------------------
if __name__ == "__main__":
    SAMPLE_SPREADSHEET_ID = "1ZnMWdYbBA3H2ROcg3sYMAIYfuWDDdisxzFBWJcErVy8"  # Reemplaza por tu spreadsheet ID

    # 1) Leer datos
    print("-- Leer datos --")
    read_result = read_sheet_values(SAMPLE_SPREADSHEET_ID, "Hoja1!A1:D10")
    print(read_result)

    # 2) Añadir una fila al final
    print("\n-- Agregar fila --")
    append_result = append_rows(
        SAMPLE_SPREADSHEET_ID,
        "Hoja1!A3",
        [["Ana", "25", "Bogotá"]],
        
    )
    print(append_result)

    # 3) Actualizar un rango específico
    print("\n-- Actualizar rango --")
    update_result = update_range(
        SAMPLE_SPREADSHEET_ID,
        "Hoja1!A3:C3",
        [["Luis", "30", "Medellín"]],
    )
    print(update_result)

 
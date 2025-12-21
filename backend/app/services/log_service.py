"""
Log Service - Google Sheets Integration
Handles logging form data and results to Google Sheets
"""
import os
import gspread
import json
import logging
from datetime import datetime
from typing import Dict, List, Any
from google.oauth2.service_account import Credentials

from app.core.config import settings
from app.services.risk_service import FIELD_LABELS

logger = logging.getLogger(__name__)


def get_sheet_by_name(sheet_name: str):
    """
    Get a worksheet by name from the configured Google Spreadsheet
    
    Args:
        sheet_name: Name of the worksheet to retrieve
        
    Returns:
        gspread.Worksheet: The requested worksheet
        
    Raises:
        ValueError: If credentials or spreadsheet ID is not configured
        Exception: If unable to access the spreadsheet
    """
    if not settings.GOOGLE_SERVICE_ACCOUNT_JSON:
        raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON not configured")
    
    if not settings.SPREADSHEET_ID:
        raise ValueError("SPREADSHEET_ID not configured")
    
    try:
        service_account_info = json.loads(settings.GOOGLE_SERVICE_ACCOUNT_JSON)
        
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        credentials = Credentials.from_service_account_info(
            service_account_info,
            scopes=scopes
        )
        
        client = gspread.authorize(credentials)
        spreadsheet = client.open_by_key(settings.SPREADSHEET_ID)
        
        return spreadsheet.worksheet(sheet_name)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in GOOGLE_SERVICE_ACCOUNT_JSON: {e}")
        raise ValueError("Invalid service account JSON configuration")
    except gspread.exceptions.WorksheetNotFound:
        logger.error(f"Worksheet '{sheet_name}' not found in spreadsheet")
        raise
    except Exception as e:
        logger.error(f"Failed to access Google Sheets: {e}")
        raise

def append_raw_input(data: Dict[str, Any], FORM_COLUMNS: List[str]) -> None:
    """
    Append raw form input to Google Sheets
    
    Args:
        data: Form data dictionary with English field names (age, gender, etc.)
        FORM_COLUMNS: List of column names in Thai (อายุ, เพศ, etc.)
    """
    try:
        sheet = get_sheet_by_name("raw_input")
        
        # Create reverse mapping: Thai label -> English field name
        label_to_field = {v: k for k, v in FIELD_LABELS.items()}
        
        row = [datetime.now().isoformat()]
        for col in FORM_COLUMNS[1:]:  # Skip first column (Timestamp)
            # Get English field name from Thai column name
            field_name = label_to_field.get(col)
            if field_name:
                value = data.get(field_name)
                # Convert lists to comma-separated strings
                if isinstance(value, list):
                    value = ", ".join(str(v) for v in value)
                row.append(value)
            else:
                # Column not in mapping, leave empty
                row.append(None)
        
        sheet.append_row(row, value_input_option="USER_ENTERED")
        logger.info(f"Successfully appended raw input to Google Sheets")
    except Exception as e:
        logger.error(f"Failed to append raw input to Google Sheets: {e}")
        raise
def append_with_result(
    data: Dict[str, Any], 
    ai_results: Dict[str, Dict[str, str]], 
    FORM_COLUMNS: List[str]
) -> None:
    """
    Append form data with AI classification results to Google Sheets
    
    Args:
        data: Form data dictionary
        ai_results: Dictionary mapping flow names to their risk assessment results
                   Each result should contain: risk_level, reason, recommendation
        FORM_COLUMNS: List of column names
    """
    try:
        sheet = get_sheet_by_name("input_with_result")
        
        # Create reverse mapping: Thai label -> English field name
        label_to_field = {v: k for k, v in FIELD_LABELS.items()}
        
        # Debug: Log FORM_COLUMNS
        logger.info(f"FORM_COLUMNS has {len(FORM_COLUMNS)} columns")
        logger.info(f"First 5 FORM_COLUMNS: {FORM_COLUMNS[:5]}")
        
        # Build base row with form data
        row = []
        for col in FORM_COLUMNS:
            if col == "Timestamp":
                timestamp_value = datetime.now().isoformat()
                row.append(timestamp_value)
                logger.info(f"Added Timestamp: {timestamp_value}")
            else:
                # Map Thai column name to English field name
                field_name = label_to_field.get(col)
                if field_name:
                    value = data.get(field_name)
                    # Convert lists to comma-separated strings
                    if isinstance(value, list):
                        value = ", ".join(str(v) for v in value)
                    row.append(value)
                else:
                    row.append(None)
        
        # Add AI results for each flow
        for flow_name, result in ai_results.items():
            row.extend([
                flow_name,
                result.get("risk_level", "N/A"),
                result.get("reason", "N/A"),
                result.get("recommendation", "N/A")
            ])
        
        logger.info(f"Total row length: {len(row)} (should match sheet columns)")
        logger.info(f"First 5 values in row: {row[:5]}")
        
        # Add metadata
        row.extend([
            settings.MODEL_NAME,
            datetime.now().isoformat()
        ])
        
        sheet.append_row(row, value_input_option="USER_ENTERED")
        logger.info(f"Successfully appended form with results to Google Sheets ({len(ai_results)} flows)")
    except Exception as e:
        logger.error(f"Failed to append form with results to Google Sheets: {e}")
        raise

    

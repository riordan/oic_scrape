from typing import List, Dict, Optional, Union
from datetime import datetime, date
from attrs import validate
from .items import AwardItem, AwardParticipant

def validate_awards(awards_list: List[dict]) -> bool:
    """
    Validates a list of award dictionaries against the AwardItem schema.
    
    Args:
        awards_list: List of award dictionaries to validate
        
    Returns:
        bool: True if all awards are valid
        
    Raises:
        Exception: If any award fails validation with details about which award and what failed
    """
    validation_errors = []
    
    for i, award_dict in enumerate(awards_list):
        try:
            # Convert dict back to AwardItem to trigger validation
            AwardItem(**award_dict)
        except Exception as e:
            validation_errors.append(f"Award {i}: {str(e)}")
    
    if validation_errors:
        raise Exception("Validation failed:\n" + "\n".join(validation_errors))
    
    return True

def validate_required_fields(awards_list: List[dict], additional_required: List[str] = None) -> bool:
    """
    Validates that all required fields are present and non-empty.
    
    Args:
        awards_list: List of award dictionaries to validate
        additional_required: Optional list of additional fields to require
        
    Returns:
        bool: True if all required fields are present
        
    Raises:
        Exception: If any required fields are missing
    """
    required_fields = {
        '_crawled_at',
        'source',
        'grant_id',
        'funder_org_name',
        'recipient_org_name'
    }
    
    if additional_required:
        required_fields.update(additional_required)
    
    errors = []
    for i, award in enumerate(awards_list):
        missing_fields = required_fields - set(award.keys())
        empty_fields = {
            field for field in required_fields 
            if field in award and not award[field]
        }
        
        if missing_fields:
            errors.append(f"Award {i}: Missing required fields: {missing_fields}")
        if empty_fields:
            errors.append(f"Award {i}: Empty required fields: {empty_fields}")
    
    if errors:
        raise Exception("Validation failed:\n" + "\n".join(errors))
    
    return True

def validate_dates(awards_list: List[dict]) -> bool:
    """
    Validates date fields are consistent and properly formatted.
    
    Args:
        awards_list: List of award dictionaries to validate
        
    Returns:
        bool: True if all date fields are valid
        
    Raises:
        Exception: If any date validation fails
    """
    errors = []
    
    for i, award in enumerate(awards_list):
        try:
            # Validate grant_year
            if award.get('grant_year'):
                if not isinstance(award['grant_year'], int):
                    errors.append(f"Award {i}: grant_year must be integer, got {type(award['grant_year'])}")
                current_year = datetime.now().year
                if not (1900 <= award['grant_year'] <= current_year + 1):
                    errors.append(f"Award {i}: grant_year {award['grant_year']} outside reasonable range")
            
            # Validate date order
            start = award.get('grant_start_date')
            end = award.get('grant_end_date')
            
            if start and end:
                if isinstance(start, str):
                    start = datetime.strptime(start, "%Y-%m-%d").date()
                if isinstance(end, str):
                    end = datetime.strptime(end, "%Y-%m-%d").date()
                
                if start > end:
                    errors.append(f"Award {i}: Start date {start} is after end date {end}")
                
        except ValueError as e:
            errors.append(f"Award {i}: Date format error - {str(e)}")
            
    if errors:
        raise Exception("Date validation failed:\n" + "\n".join(errors))
    
    return True

def validate_currency_fields(awards_list: List[dict]) -> bool:
    """
    Validates that currency amounts and codes are properly formatted.
    
    Args:
        awards_list: List of award dictionaries to validate
        
    Returns:
        bool: True if all currency fields are valid
        
    Raises:
        Exception: If any currency validation fails
    """
    errors = []
    
    for i, award in enumerate(awards_list):
        # Check currency code format
        if award.get('award_currency'):
            if len(award['award_currency']) != 3:
                errors.append(f"Award {i}: Invalid currency code format: {award['award_currency']}")
        
        # Validate amount fields
        amount = award.get('award_amount')
        amount_usd = award.get('award_amount_usd')
        currency = award.get('award_currency')
        
        if amount is not None:
            if not isinstance(amount, (int, float)):
                errors.append(f"Award {i}: award_amount must be numeric, got {type(amount)}")
            if amount < 0:
                errors.append(f"Award {i}: award_amount cannot be negative")
            if currency is None:
                errors.append(f"Award {i}: award_amount present but award_currency missing")
                
        if amount_usd is not None:
            if not isinstance(amount_usd, (int, float)):
                errors.append(f"Award {i}: award_amount_usd must be numeric, got {type(amount_usd)}")
            if amount_usd < 0:
                errors.append(f"Award {i}: award_amount_usd cannot be negative")
    
    if errors:
        raise Exception("Currency validation failed:\n" + "\n".join(errors))
    
    return True

def validate_participants(awards_list: List[dict]) -> bool:
    """
    Validates participant information when present.
    
    Args:
        awards_list: List of award dictionaries to validate
        
    Returns:
        bool: True if all participant data is valid
        
    Raises:
        Exception: If any participant validation fails
    """
    errors = []
    
    for i, award in enumerate(awards_list):
        if award.get('named_participants'):
            try:
                for j, participant in enumerate(award['named_participants']):
                    # Validate against AwardParticipant schema
                    AwardParticipant(**participant)
                    
                    # Additional validation
                    if participant.get('is_pi') and not award.get('pi_name'):
                        errors.append(f"Award {i}: Participant {j} marked as PI but pi_name field is empty")
                        
            except Exception as e:
                errors.append(f"Award {i}: Participant validation failed - {str(e)}")
    
    if errors:
        raise Exception("Participant validation failed:\n" + "\n".join(errors))
    
    return True

def validate_all(awards_list: List[dict], additional_required: List[str] = None) -> bool:
    """
    Runs all validation checks on the awards list.
    
    Args:
        awards_list: List of award dictionaries to validate
        additional_required: Optional list of additional required fields
        
    Returns:
        bool: True if all validations pass
        
    Raises:
        Exception: If any validation fails
    """
    validate_required_fields(awards_list, additional_required)
    validate_dates(awards_list)
    validate_currency_fields(awards_list)
    validate_participants(awards_list)
    validate_awards(awards_list)
    return True
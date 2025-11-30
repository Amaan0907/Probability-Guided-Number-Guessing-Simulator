

from typing import Tuple
from pathlib import Path


class ValidationError(Exception):
    

    pass


class InputValidator:
   

    @staticmethod
    def validate_number(
        value, min_val: int, max_val: int, field_name: str = "Number"
    ) -> int:
        
        if value is None or value == "":
            raise ValidationError(f"{field_name} cannot be empty.")

       
        try:
            num = int(value)
        except (ValueError, TypeError):
            raise ValidationError(
                f"{field_name} must be a number. You entered: '{value}'"
            )

       
        if num < min_val or num > max_val:
            raise ValidationError(
                f"{field_name} must be between {min_val} and {max_val}. "
                f"You entered: {num}"
            )

        return num

    @staticmethod
    def validate_string(
        value, min_length: int = 1, max_length: int = 100, field_name: str = "Input"
    ) -> str:
      
        if value is None:
            raise ValidationError(f"{field_name} cannot be empty.")

        # Convert to string and remove extra spaces
        text = str(value).strip()

        # Check length
        if len(text) < min_length:
            raise ValidationError(
                f"{field_name} must be at least {min_length} characters."
            )

        if len(text) > max_length:
            raise ValidationError(
                f"{field_name} is too long (max {max_length} characters)."
            )

        return text

    @staticmethod
    def validate_range(min_val: int, max_val: int) -> Tuple[int, int]:
       
        if min_val >= max_val:
            raise ValidationError(
                f"Invalid range: min ({min_val}) must be less than max ({max_val})."
            )

        if min_val < 1:
            raise ValidationError(f"Minimum value must be at least 1.")

        return min_val, max_val

    @staticmethod
    def validate_file_path(
        path: str, must_exist: bool = False, extension: str = None
    ) -> str:
        
        if not path:
            raise ValidationError("File path cannot be empty.")

        try:
            path_obj = Path(path)
        except Exception as e:
            raise ValidationError(f"Invalid path: {e}")

        # Check extension
        if extension and path_obj.suffix.lower() != extension.lower():
            raise ValidationError(f"File must be a {extension} file.")

        # Check if exists
        if must_exist and not path_obj.exists():
            raise ValidationError(f"File not found: {path}")

        return str(path_obj)

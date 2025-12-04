"""
Input Validation Module
Simple validation with clear error messages.
"""

import os


class ValidationError(Exception):
    """Exception for validation failures."""
    pass


class InputValidator:
    """
    Simple input validation for the game.
    """
    
    @staticmethod
    def validate_number(value, min_val, max_val, field_name="Number"):
        """
        Validate that a value is a number within range.
        
        Args:
            value: The value to check
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            field_name: Name for error messages
            
        Returns:
            The validated integer
            
        Raises:
            ValidationError: If validation fails
        """
        # Check if empty
        if value is None or value == "":
            raise ValidationError(f"{field_name} cannot be empty.")
        
        # Try converting to integer
        try:
            num = int(value)
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name} must be a number. You entered: '{value}'")
        
        # Check if in range
        if num < min_val or num > max_val:
            raise ValidationError(
                f"{field_name} must be between {min_val} and {max_val}. You entered: {num}" 
                
            )
        
        return num
    
    @staticmethod
    def validate_string(value, min_length=1, max_length=100, field_name="Input"):
        """
        Validate string input.
        
        Args:
            value: The value to validate
            min_length: Minimum length
            max_length: Maximum length
            field_name: Name for error messages
            
        Returns:
            The validated string
            
        Raises:
            ValidationError: If validation fails
        """
        if value is None:
            raise ValidationError(f"{field_name} cannot be empty.")
        
        # Convert to string and remove extra spaces
        text = str(value).strip()
        
        # Check length
        if len(text) < min_length:
            raise ValidationError(f"{field_name} must be at least {min_length} characters.")
        
        if len(text) > max_length:
            raise ValidationError(f"{field_name} is too long (max {max_length} characters).")
        
        return text
    
    @staticmethod
    def validate_range(min_val, max_val):
        """
        Validate that min is less than max.
        
        Args:
            min_val: Minimum value
            max_val: Maximum value
            
        Returns:
            Tuple of (min_val, max_val)
            
        Raises:
            ValidationError: If range is invalid
        """
        if min_val >= max_val:
            raise ValidationError(
                f"Invalid range: min ({min_val}) must be less than max ({max_val})."
            )
        
        if min_val < 1:
            raise ValidationError("Minimum value must be at least 1.")
        
        return min_val, max_val
    
    @staticmethod
    def validate_file_path(path, must_exist=False, extension=None):
        """
        Validate file path.
        
        Args:
            path: The file path
            must_exist: Whether file must exist
            extension: Required extension (e.g., '.csv')
            
        Returns:
            The validated path
            
        Raises:
            ValidationError: If validation fails
        """
        if not path:
            raise ValidationError("File path cannot be empty.")
        
        # Check extension
        if extension:
            _, file_ext = os.path.splitext(path)
            if file_ext.lower() != extension.lower():
                raise ValidationError(f"File must be a {extension} file.")
        
        # Check if exists
        if must_exist and not os.path.exists(path):
            raise ValidationError(f"File not found: {path}")
        
        return path
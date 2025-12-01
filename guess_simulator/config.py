

from typing import Dict, Any
from .logger import logger


class ConfigurationError(Exception):
    """Exception raised for configuration errors."""

    pass


# Hardcoded difficulty profiles
DIFFICULTY_PROFILES = {
    "easy": {
        "min_number": 1,
        "max_number": 50,
        "max_attempts": 15,
        "hint_frequency": 2,
        "probability_threshold": 0.7,
    },
    "medium": {
        "min_number": 1,
        "max_number": 100,
        "max_attempts": 10,
        "hint_frequency": 3,
        "probability_threshold": 0.6,
    },
    "hard": {
        "min_number": 1,
        "max_number": 200,
        "max_attempts": 8,
        "hint_frequency": 4,
        "probability_threshold": 0.5,
    },
    "expert": {
        "min_number": 1,
        "max_number": 500,
        "max_attempts": 12,
        "hint_frequency": 5,
        "probability_threshold": 0.4,
    },
}

# Default settings
DEFAULT_CONFIG = {
    "data_dir": "game_data",
    "log_level": "INFO",
    "log_file": "game.log",
    "max_log_size": 10485760,  # 10MB
}


class ConfigManager:
    """
    Simple configuration manager with hardcoded profiles.
    """

    def __init__(self):
        """Initialize the configuration manager."""
        self.current_profile = "medium"  # Default profile
        logger.info("Configuration manager initialized")

    def get_profile(self, profile_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific profile.

        Args:
            profile_name: Name of the profile (easy, medium, hard, expert)

        Returns:
            Dictionary of configuration values

        Raises:
            ConfigurationError: If profile doesn't exist
        """
        if profile_name not in DIFFICULTY_PROFILES:
            available = list(DIFFICULTY_PROFILES.keys())
            raise ConfigurationError(
                f"Profile '{profile_name}' not found. "
                f"Available profiles: {', '.join(available)}"
            )

        return DIFFICULTY_PROFILES[profile_name].copy()

    def set_profile(self, profile_name: str):
        """
        Set the current active profile.

        Args:
            profile_name: Name of the profile to activate
        """
        # Validate profile exists
        self.get_profile(profile_name)
        self.current_profile = profile_name
        logger.info(f"Active profile set to: {profile_name}")

    def get_current_profile(self) -> Dict[str, Any]:
        """Get the current active profile configuration."""
        return self.get_profile(self.current_profile)

    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return DEFAULT_CONFIG.copy()

    def list_profiles(self) -> list:
        """List all available profiles."""
        return list(DIFFICULTY_PROFILES.keys())

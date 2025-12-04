"""
Logging Module
Simple logging for the game.
"""

import logging
import os


class GameLogger:
    """
    Simple logging system for the game.
    Uses singleton pattern to have one logger everywhere.
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        """Create only one logger instance."""
        if cls._instance is None:
            cls._instance = super(GameLogger, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the logger once."""
        if not self._initialized:
            self.logger = None
            self._initialized = True

    def setup(self, log_file="game.log", log_level="INFO", console_output=True):
        """
        Set up logging.

        Args:
            log_file: Where to save logs
            log_level: Level of detail (DEBUG, INFO, WARNING, ERROR)
            console_output: Whether to print to console
        """
        # Create logger
        self.logger = logging.getLogger("GuessSimulator")
        self.logger.setLevel(getattr(logging, log_level.upper()))

        # Remove old handlers
        self.logger.handlers = []

        # Create format for log messages
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

        # File handler - save to file
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Console handler - print to screen (optional)
        if console_output:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

        self.info("Logger initialized")

    def debug(self, message):
        """Log debug message."""
        if self.logger:
            self.logger.debug(message)

    def info(self, message):
        """Log info message."""
        if self.logger:
            self.logger.info(message)

    def warning(self, message):
        """Log warning message."""
        if self.logger:
            self.logger.warning(message)

    def error(self, message):
        """Log error message."""
        if self.logger:
            self.logger.error(message)

    def critical(self, message):
        """Log critical message."""
        if self.logger:
            self.logger.critical(message)

    def exception(self, message):
        """Log exception with traceback."""
        if self.logger:
            self.logger.exception(message)

    def log_game_start(self, game_id, difficulty, range_info):
        """Log when a game starts."""
        self.info(
            f"Game started - ID: {game_id}, Difficulty: {difficulty}, Range: {range_info["min"]}-{range_info["max"]}"
        )

    def log_guess(self, game_id, attempt, guess, result):
        """Log a guess."""
        self.debug(
            f"Game {game_id} - Attempt {attempt}: Guess={guess}, Result={result}"
        )

    def log_game_end(self, game_id, won, attempts, target):
        """Log when a game ends."""
        status = "WON" if won else "LOST"
        self.info(
            f"Game ended - ID: {game_id}, Status: {status}, Attempts: {attempts}"
        )


# Global logger instance
logger = GameLogger()

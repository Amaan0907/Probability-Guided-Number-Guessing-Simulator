

import logging
from pathlib import Path


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
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the logger once."""
        if not self._initialized:
            self.logger = None
            self._initialized = True

    def setup(
        self,
        log_file: str = "game.log",
        log_level: str = "INFO",
        console_output: bool = True,
    ):
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
        self.logger.handlers.clear()

        # Create format for log messages
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

        # File handler - save to file
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

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

    def debug(self, message: str):
        """Log debug message."""
        if self.logger:
            self.logger.debug(message)

    def info(self, message: str):
        """Log info message."""
        if self.logger:
            self.logger.info(message)

    def warning(self, message: str):
        """Log warning message."""
        if self.logger:
            self.logger.warning(message)

    def error(self, message: str):
        """Log error message."""
        if self.logger:
            self.logger.error(message)

    def critical(self, message: str):
        """Log critical message."""
        if self.logger:
            self.logger.critical(message)

    def exception(self, message: str):
        """Log exception with traceback."""
        if self.logger:
            self.logger.exception(message)

    def log_game_start(self, game_id: str, difficulty: str, range_info: dict):
        """Log when a game starts."""
        self.info(
            f"Game started - ID: {game_id}, Difficulty: {difficulty}, "
            f"Range: {range_info['min']}-{range_info['max']}"
        )

    def log_guess(self, game_id: str, attempt: int, guess: int, result: str):
        """Log a guess."""
        self.debug(
            f"Game {game_id} - Attempt {attempt}: Guess={guess}, Result={result}"
        )

    def log_game_end(self, game_id: str, won: bool, attempts: int, target: int):
        """Log when a game ends."""
        status = "WON" if won else "LOST"
        self.info(f"Game ended - ID: {game_id}, Status: {status}, Attempts: {attempts}")


# Global logger instance
logger = GameLogger()

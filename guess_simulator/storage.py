
import json
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional
from .logger import logger


class StorageError(Exception):
    """Exception raised for storage operation failures."""

    pass


class GameStorage:
    """
    Simple JSON storage for game data.
    """

    def __init__(self, data_dir: str = "game_data"):
        """
        Initialize the storage system.

        Args:
            data_dir: Directory for game data
        """
        self.data_dir = Path(data_dir)

        # Create directory if it doesn't exist
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # File paths
        self.games_file = self.data_dir / "games.json"
        self.stats_file = self.data_dir / "statistics.json"

        logger.info(f"Storage initialized: {self.data_dir}")

    def save_game(self, game_data: Dict[str, Any]) -> bool:
        """
        Save a game to storage.

        Args:
            game_data: Dictionary containing game information

        Returns:
            True if successful, False otherwise
        """
        try:
            # Load existing games
            games = self.load_all_games()

            # Check for duplicate game_id (simple idempotent check)
            game_id = game_data.get("game_id")
            if not game_id:
                raise StorageError("Game data must have 'game_id'")

            # Update or add game
            found = False
            for i, game in enumerate(games):
                if game.get("game_id") == game_id:
                    games[i] = game_data
                    found = True
                    break

            if not found:
                games.append(game_data)

            # Write to file
            with open(self.games_file, "w", encoding="utf-8") as f:
                json.dump(games, f, indent=2, ensure_ascii=False)

            logger.info(f"Game saved: {game_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to save game: {e}")
            return False

    def load_all_games(self) -> List[Dict[str, Any]]:
        """
        Load all games from storage.

        Returns:
            List of game dictionaries
        """
        if not self.games_file.exists():
            return []

        try:
            with open(self.games_file, "r", encoding="utf-8") as f:
                games = json.load(f)

            logger.debug(f"Loaded {len(games)} games from storage")
            return games

        except json.JSONDecodeError as e:
            logger.error(f"Corrupted game data file: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to load games: {e}")
            return []

    def load_game(self, game_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a specific game by ID.

        Args:
            game_id: The game ID to load

        Returns:
            Game dictionary or None if not found
        """
        games = self.load_all_games()
        for game in games:
            if game.get("game_id") == game_id:
                return game
        return None

    def save_statistics(self, stats: Dict[str, Any]) -> bool:
        """
        Save statistics to storage.

        Args:
            stats: Statistics dictionary

        Returns:
            True if successful
        """
        try:
            with open(self.stats_file, "w", encoding="utf-8") as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)

            logger.info("Statistics saved")
            return True

        except Exception as e:
            logger.error(f"Failed to save statistics: {e}")
            return False

    def load_statistics(self) -> Dict[str, Any]:
        """
        Load statistics from storage.

        Returns:
            Statistics dictionary
        """
        if not self.stats_file.exists():
            return self._get_default_statistics()

        try:
            with open(self.stats_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load statistics: {e}")
            return self._get_default_statistics()

    def _get_default_statistics(self) -> Dict[str, Any]:
        """Get default statistics structure."""
        return {
            "total_games": 0,
            "games_won": 0,
            "games_lost": 0,
            "total_attempts": 0,
            "best_score": None,
            "average_attempts": 0.0,
        }

    def export_to_csv(self, output_path: str) -> bool:
        """
        Export all games to CSV format.

        Args:
            output_path: Path to the output CSV file

        Returns:
            True if successful
        """
        try:
            games = self.load_all_games()

            if not games:
                logger.warning("No games to export")
                return False

            # Determine all possible fields
            fieldnames = set()
            for game in games:
                fieldnames.update(game.keys())
            fieldnames = sorted(fieldnames)

            # Write CSV
            with open(output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(games)

            logger.info(f"Exported {len(games)} games to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to export to CSV: {e}")
            return False

    def import_from_csv(self, input_path: str) -> bool:
        """
        Import games from CSV format.

        Args:
            input_path: Path to the input CSV file

        Returns:
            True if successful
        """
        try:
            imported_games = []

            with open(input_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Convert numeric fields
                    if "attempts" in row:
                        row["attempts"] = int(row["attempts"])
                    if "target_number" in row:
                        row["target_number"] = int(row["target_number"])
                    if "won" in row:
                        row["won"] = row["won"].lower() == "true"

                    imported_games.append(row)

            # Merge with existing games
            existing_games = self.load_all_games()
            existing_ids = {g.get("game_id") for g in existing_games}

            new_games = 0
            for game in imported_games:
                if game.get("game_id") not in existing_ids:
                    existing_games.append(game)
                    new_games += 1

            # Save merged data
            with open(self.games_file, "w", encoding="utf-8") as f:
                json.dump(existing_games, f, indent=2, ensure_ascii=False)

            logger.info(f"Imported {new_games} new games from {input_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to import from CSV: {e}")
            return False

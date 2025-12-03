"""
Simple Storage Module
Handles basic JSON storage for game data.
"""

import json
import csv
import os
from .logger import logger


class StorageError(Exception):
    """Exception raised for storage operation failures."""

    pass


class GameStorage:
    """
    Simple JSON storage for game data.
    """

    def __init__(self, data_dir="game_data"):
        """
        Initialize the storage system.

        Args:
            data_dir: Directory for game data
        """
        self.data_dir = data_dir

        # Create directory if it doesn't exist
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        # File paths
        self.games_file = os.path.join(self.data_dir, "games.json")
        self.stats_file = os.path.join(self.data_dir, "statistics.json")

        logger.info("Storage initialized: {}".format(self.data_dir))

    def save_game(self, game_data):
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

            logger.info("Game saved: {}".format(game_id))
            return True

        except Exception as e:
            logger.error("Failed to save game: {}".format(e))
            return False

    def load_all_games(self):
        """
        Load all games from storage.

        Returns:
            List of game dictionaries
        """
        if not os.path.exists(self.games_file):
            return []

        try:
            with open(self.games_file, "r", encoding="utf-8") as f:
                games = json.load(f)

            logger.debug("Loaded {} games from storage".format(len(games)))
            return games

        except json.JSONDecodeError as e:
            logger.error("Corrupted game data file: {}".format(e))
            return []
        except Exception as e:
            logger.error("Failed to load games: {}".format(e))
            return []

    def load_game(self, game_id):
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

    def save_statistics(self, stats):
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
            logger.error("Failed to save statistics: {}".format(e))
            return False

    def load_statistics(self):
        """
        Load statistics from storage.

        Returns:
            Statistics dictionary
        """
        if not os.path.exists(self.stats_file):
            return self._get_default_statistics()

        try:
            with open(self.stats_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error("Failed to load statistics: {}".format(e))
            return self._get_default_statistics()

    def _get_default_statistics(self):
        """Get default statistics structure."""
        return {
            "total_games": 0,
            "games_won": 0,
            "games_lost": 0,
            "total_attempts": 0,
            "best_score": None,
            "average_attempts": 0.0,
        }

    def export_to_csv(self, output_path):
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

            logger.info("Exported {} games to {}".format(len(games), output_path))
            return True

        except Exception as e:
            logger.error("Failed to export to CSV: {}".format(e))
            return False

    def import_from_csv(self, input_path):
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
            existing_ids = set(g.get("game_id") for g in existing_games)

            new_games = 0
            for game in imported_games:
                if game.get("game_id") not in existing_ids:
                    existing_games.append(game)
                    new_games += 1

            # Save merged data
            with open(self.games_file, "w", encoding="utf-8") as f:
                json.dump(existing_games, f, indent=2, ensure_ascii=False)

            logger.info("Imported {} new games from {}".format(new_games, input_path))
            return True

        except Exception as e:
            logger.error("Failed to import from CSV: {}".format(e))
            return False

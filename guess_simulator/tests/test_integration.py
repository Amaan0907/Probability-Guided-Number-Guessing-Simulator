
import unittest
import tempfile
import shutil
from pathlib import Path
from guess_simulator.game import GameEngine
from guess_simulator.storage import GameStorage
from guess_simulator.config import ConfigManager


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.storage = GameStorage(data_dir=str(Path(self.test_dir) / "data"))

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)

    def test_complete_game_workflow(self):
        """Test a complete game workflow from start to finish."""
        # Create game
        game = GameEngine(min_number=1, max_number=100, max_attempts=10)

        # Play game
        target = game.target_number
        result = game.make_guess(target)

        # Verify win
        self.assertTrue(result["correct"])
        self.assertTrue(game.won)

        # Save game
        game_data = game.get_game_data()
        success = self.storage.save_game(game_data)
        self.assertTrue(success)

        # Load and verify
        loaded = self.storage.load_game(game_data["game_id"])
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["won"], True)

    def test_multiple_games_statistics(self):
        """Test playing multiple games and calculating statistics."""
        games_data = []

        # Play 5 games
        for i in range(5):
            game = GameEngine(min_number=1, max_number=50, max_attempts=10)

            # Win some, lose some
            if i % 2 == 0:
                game.make_guess(game.target_number)
            else:
                # Make max attempts with wrong guesses
                for _ in range(game.max_attempts):
                    if not game.finished:
                        wrong = 1 if game.target_number != 1 else 2
                        game.make_guess(wrong)

            # Save game
            game_data = game.get_game_data()
            self.storage.save_game(game_data)
            games_data.append(game_data)

        # Load all games
        loaded_games = self.storage.load_all_games()
        self.assertEqual(len(loaded_games), 5)

        # Calculate statistics
        from guess_simulator.game import GameStatistics

        stats = GameStatistics.calculate_statistics(loaded_games)

        self.assertEqual(stats["total_games"], 5)
        self.assertGreater(stats["games_won"], 0)
        self.assertGreater(stats["games_lost"], 0)

    def test_config_integration(self):
        """Test configuration integration with game."""
        # Create config (will use defaults if file doesn't exist)
        config = ConfigManager()

        # Get profile
        profile = config.get_profile("medium")

        # Create game with profile settings
        game = GameEngine(**profile)

        self.assertEqual(game.min_number, profile["min_number"])
        self.assertEqual(game.max_number, profile["max_number"])
        self.assertEqual(game.max_attempts, profile["max_attempts"])


if __name__ == "__main__":
    unittest.main()


import unittest
import tempfile
import shutil
from pathlib import Path
from guess_simulator.storage import GameStorage


class TestGameStorage(unittest.TestCase):
    """Test cases for GameStorage class."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.storage = GameStorage(data_dir=str(Path(self.test_dir) / "data"))

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)

    def test_save_and_load_game(self):
        """Test saving and loading a game."""
        game_data = {
            "game_id": "test-123",
            "attempts": 5,
            "won": True,
            "target_number": 42,
        }

        # Save game
        success = self.storage.save_game(game_data)
        self.assertTrue(success)

        # Load game
        loaded = self.storage.load_game("test-123")
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["game_id"], "test-123")
        self.assertEqual(loaded["attempts"], 5)

    def test_load_all_games(self):
        """Test loading all games."""
        # Save multiple games
        for i in range(3):
            game_data = {"game_id": f"test-{i}", "attempts": i + 1, "won": i % 2 == 0}
            self.storage.save_game(game_data)

        # Load all
        games = self.storage.load_all_games()
        self.assertEqual(len(games), 3)

    def test_export_to_csv(self):
        """Test exporting games to CSV."""
        # Save a game
        game_data = {"game_id": "test-csv", "attempts": 7, "won": True}
        self.storage.save_game(game_data)

        # Export
        csv_path = str(Path(self.test_dir) / "export.csv")
        success = self.storage.export_to_csv(csv_path)
        self.assertTrue(success)
        self.assertTrue(Path(csv_path).exists())

    def test_import_from_csv(self):
        """Test importing games from CSV."""
        # Create and export a game
        game_data = {
            "game_id": "test-import",
            "attempts": 4,
            "won": True,
            "target_number": 50,
        }
        self.storage.save_game(game_data)

        csv_path = str(Path(self.test_dir) / "import.csv")
        self.storage.export_to_csv(csv_path)

        # Create new storage and import
        new_storage = GameStorage(data_dir=str(Path(self.test_dir) / "data2"))

        success = new_storage.import_from_csv(csv_path)
        self.assertTrue(success)

        # Verify imported
        games = new_storage.load_all_games()
        self.assertGreater(len(games), 0)


if __name__ == "__main__":
    unittest.main()

"""
Unit tests for the game logic module.
"""

import unittest
from guess_simulator.game import GameEngine, GameStatistics
from guess_simulator.validator import ValidationError


class TestGameEngine(unittest.TestCase):
    """Test cases for GameEngine class."""

    def setUp(self):
        """Set up test fixtures."""
        self.game = GameEngine(min_number=1, max_number=100, max_attempts=10)

    def test_game_initialization(self):
        """Test game initializes correctly."""
        self.assertEqual(self.game.min_number, 1)
        self.assertEqual(self.game.max_number, 100)
        self.assertEqual(self.game.max_attempts, 10)
        self.assertEqual(self.game.attempts, 0)
        self.assertFalse(self.game.won)
        self.assertFalse(self.game.finished)
        self.assertTrue(1 <= self.game.target_number <= 100)

    def test_valid_guess(self):
        """Test making a valid guess."""
        result = self.game.make_guess(50)
        self.assertIsInstance(result, dict)
        self.assertEqual(self.game.attempts, 1)
        self.assertIn("feedback", result)

    def test_winning_game(self):
        """Test winning the game."""
        target = self.game.target_number
        result = self.game.make_guess(target)

        self.assertTrue(result["correct"])
        self.assertTrue(result["game_over"])
        self.assertTrue(self.game.won)
        self.assertTrue(self.game.finished)

    def test_losing_game(self):
        """Test losing the game."""
        # Make max attempts with wrong guesses
        for i in range(self.game.max_attempts):
            # Guess a number that's definitely wrong
            wrong_guess = 1 if self.game.target_number != 1 else 2
            result = self.game.make_guess(wrong_guess)

        self.assertTrue(result["game_over"])
        self.assertFalse(self.game.won)
        self.assertTrue(self.game.finished)

    def test_guess_history(self):
        """Test guess history is tracked."""
        self.game.make_guess(25)
        self.game.make_guess(75)
        self.game.make_guess(50)

        self.assertEqual(len(self.game.guess_history), 3)
        self.assertEqual(self.game.guess_history, [25, 75, 50])


class TestGameStatistics(unittest.TestCase):
    """Test cases for GameStatistics class."""

    def test_statistics_calculation(self):
        """Test statistics calculation with sample games."""
        games = [
            {"won": True, "finished": True, "attempts": 5},
            {"won": True, "finished": True, "attempts": 7},
            {"won": False, "finished": True, "attempts": 10},
        ]

        stats = GameStatistics.calculate_statistics(games)

        self.assertEqual(stats["total_games"], 3)
        self.assertEqual(stats["games_won"], 2)
        self.assertEqual(stats["games_lost"], 1)
        self.assertEqual(stats["best_score"], 5)
        self.assertEqual(stats["worst_score"], 7)


if __name__ == "__main__":
    unittest.main()

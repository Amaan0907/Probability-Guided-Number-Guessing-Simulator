"""
Game Logic Module
Simple number guessing game with hints.
"""

import random
import time
from .validator import InputValidator, ValidationError
from .logger import logger


def generate_game_id():
    """Generate a unique game ID using timestamp and random number."""
    timestamp = str(int(time.time() * 1000))
    random_part = str(random.randint(100000, 999999))
    return "game-{}-{}".format(timestamp, random_part)


class GameEngine:
    """
    Main game engine for number guessing with simple hints.
    """
    
    def __init__(
        self,
        min_number=1,
        max_number=100,
        max_attempts=10,
        hint_frequency=3,
        probability_threshold=0.6
    ):
        """
        Initialize a new game.
        
        Args:
            min_number: Minimum number in range
            max_number: Maximum number in range
            max_attempts: Maximum number of guessing attempts
            hint_frequency: Provide hints every N attempts
        """
        # Validate and store range
        self.min_number, self.max_number = InputValidator.validate_range(
            min_number, max_number
        )
        
        self.max_attempts = max_attempts
        self.hint_frequency = hint_frequency
        
        # Game state
        self.game_id = generate_game_id()
        self.target_number = random.randint(self.min_number, self.max_number)
        self.attempts = 0
        self.guess_history = []
        self.won = False
        self.finished = False
        self.start_time = time.time()
        self.end_time = None
        
        # Track narrowed range for hints
        self.current_min = self.min_number
        self.current_max = self.max_number
        
        logger.log_game_start(
            self.game_id,
            "custom",
            {
                'min': self.min_number,
                'max': self.max_number,
                'max_attempts': self.max_attempts
            }
        )
    
    def make_guess(self, guess):
        """
        Process a guess and return feedback.
        
        Args:
            guess: The guessed number
            
        Returns:
            Dictionary with guess result and feedback
        """
        # Check if game is already over
        if self.finished:
            raise RuntimeError("Game is already finished!")
        
        # Validate the guess
        guess = InputValidator.validate_number(
            guess,
            self.min_number,
            self.max_number,
            "Guess"
        )
        
        # Update attempts and history
        self.attempts += 1
        self.guess_history.append(guess)
        
        # Update the possible range
        self._update_range(guess)
        
        # Check if guess is correct
        if guess == self.target_number:
            return self._handle_win()
        
        # Check if out of attempts
        if self.attempts >= self.max_attempts:
            return self._handle_loss()
        
        # Generate feedback for wrong guess
        feedback = self._get_feedback(guess)
        hint = self._get_hint(guess)
        
        result = {
            'correct': False,
            'attempts': self.attempts,
            'remaining': self.max_attempts - self.attempts,
            'feedback': feedback,
            'hint': hint,
            'game_over': False,
            'probability_info': self._get_range_info()
        }
        
        logger.log_guess(self.game_id, self.attempts, guess, feedback)
        return result
    
    def _handle_win(self):
        """Handle winning the game."""
        self.won = True
        self.finished = True
        self.end_time = time.time()
        
        result = {
            'correct': True,
            'attempts': self.attempts,
            'message': "🎉 Congratulations! You guessed it in {} attempts!".format(self.attempts),
            'game_over': True,
            'won': True
        }
        
        logger.log_game_end(self.game_id, True, self.attempts, self.target_number)
        return result
    
    def _handle_loss(self):
        """Handle losing the game."""
        self.finished = True
        self.end_time = time.time()
        
        result = {
            'correct': False,
            'attempts': self.attempts,
            'message': "😞 Game Over! The number was {}.".format(self.target_number),
            'game_over': True,
            'won': False,
            'target': self.target_number
        }
        
        logger.log_game_end(self.game_id, False, self.attempts, self.target_number)
        return result
    
    def _get_feedback(self, guess):
        """Get simple higher/lower feedback."""
        if guess < self.target_number:
            return "📈 Too low! Try a higher number."
        else:
            return "📉 Too high! Try a lower number."
    
    def _update_range(self, guess):
        """Update the possible range based on the guess."""
        if guess < self.target_number:
            # Guess was too low, update minimum
            self.current_min = max(self.current_min, guess + 1)
        else:
            # Guess was too high, update maximum
            self.current_max = min(self.current_max, guess - 1)
    
    def _get_hint(self, guess):
        """
        Generate a simple hint based on distance.
        
        Returns:
            Hint string or None
        """
        # Only give hints at specified frequency
        if self.attempts % self.hint_frequency != 0:
            return None
        
        # Calculate how close the guess is
        distance = abs(guess - self.target_number)
        range_size = self.max_number - self.min_number
        
        # Temperature hint based on distance
        if distance <= range_size * 0.1:
            temperature = "🔥 Very Hot!"
        elif distance <= range_size * 0.25:
            temperature = "♨️ Hot!"
        elif distance <= range_size * 0.5:
            temperature = "🌡️ Warm"
        elif distance <= range_size * 0.75:
            temperature = "❄️ Cold"
        else:
            temperature = "🧊 Very Cold!"
        
        # Range hint
        range_hint = "The number is between {} and {}.".format(
            self.current_min, self.current_max
        )
        
        return "{} {}".format(temperature, range_hint)
    
    def _get_range_info(self):
        """Get information about the current possible range."""
        remaining = self.current_max - self.current_min + 1
        
        return {
            'remaining_possibilities': remaining,
            'current_min': self.current_min,
            'current_max': self.current_max
        }
    
    def get_game_data(self):
        """
        Get all game data for saving.
        
        Returns:
            Dictionary with game information
        """
        duration = None
        if self.end_time:
            duration = self.end_time - self.start_time
        
        # Convert timestamp to readable format
        start_time_str = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(self.start_time))
        end_time_str = None
        if self.end_time:
            end_time_str = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(self.end_time))
        
        return {
            'game_id': self.game_id,
            'start_time': start_time_str,
            'end_time': end_time_str,
            'duration_seconds': duration,
            'min_number': self.min_number,
            'max_number': self.max_number,
            'target_number': self.target_number if self.finished else None,
            'max_attempts': self.max_attempts,
            'attempts': self.attempts,
            'guess_history': self.guess_history,
            'won': self.won,
            'finished': self.finished
        }
    
    def get_statistics(self):
        """
        Get game statistics.
        
        Returns:
            Dictionary with game stats
        """
        if not self.finished:
            return {'status': 'in_progress'}
        
        efficiency = (self.attempts / float(self.max_attempts)) * 100
        
        return {
            'status': 'won' if self.won else 'lost',
            'attempts': self.attempts,
            'max_attempts': self.max_attempts,
            'efficiency': round(efficiency, 2),
            'target_number': self.target_number,
            'guess_history': self.guess_history
        }


class GameStatistics:
    """
    Calculate statistics from multiple games.
    """
    
    @staticmethod
    def calculate_statistics(games):
        """
        Calculate overall statistics from game history.
        
        Args:
            games: List of game data dictionaries
            
        Returns:
            Dictionary with statistics
        """
        # Handle empty game list
        if not games:
            return {
                'total_games': 0,
                'games_won': 0,
                'games_lost': 0,
                'win_rate': 0.0,
                'total_attempts': 0,
                'average_attempts': 0.0,
                'best_score': None,
                'worst_score': None
            }
        
        # Count games
        total_games = len(games)
        games_won = sum(1 for g in games if g.get('won'))
        games_lost = total_games - games_won
        
        # Calculate attempts
        finished_games = [g for g in games if g.get('finished')]
        total_attempts = sum(g.get('attempts', 0) for g in finished_games)
        
        # Get scores from won games
        won_games = [g for g in games if g.get('won')]
        attempts_won = [g.get('attempts') for g in won_games if g.get('attempts')]
        
        # Build statistics
        stats = {
            'total_games': total_games,
            'games_won': games_won,
            'games_lost': games_lost,
            'win_rate': round((games_won / float(total_games) * 100), 2) if total_games > 0 else 0.0,
            'total_attempts': total_attempts,
            'average_attempts': round(total_attempts / float(len(finished_games)), 2) if finished_games else 0.0,
            'best_score': min(attempts_won) if attempts_won else None,
            'worst_score': max(attempts_won) if attempts_won else None,
        }
        
        # Add average for won games
        if attempts_won:
            stats['average_attempts_won'] = round(sum(attempts_won) / float(len(attempts_won)), 2)
        else:
            stats['average_attempts_won'] = None
        
        return stats
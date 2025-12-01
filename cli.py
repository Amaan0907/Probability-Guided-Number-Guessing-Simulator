"""



Command Line Interface Module

Main CLI for the Probability-Guided Number Guessing Simulator.

"""

import argparse

import sys

from pathlib import Path

from typing import Optional

from .game import GameEngine, GameStatistics

from .storage import GameStorage

from .config import ConfigManager, ConfigurationError

from .logger import logger

from .validator import InputValidator, ValidationError

class CLI:

    """

    Command-line interface for the game simulator.

    """

    

    def __init__(self):

        """Initialize the CLI."""

        self.config_manager = ConfigManager()

        self.setup_logging()

        self.storage = self.setup_storage()

        self.current_game: Optional[GameEngine] = None

    

    def setup_logging(self):

        """Set up logging based on configuration."""

        config = self.config_manager.get_default_config()

        logger.setup(

            log_file=config['log_file'],

            log_level=config['log_level'],

            console_output=False  # CLI handles its own output

        )

    

    def setup_storage(self) -> GameStorage:

        """Set up storage based on configuration."""

        default_config = self.config_manager.get_default_config()

        

        return GameStorage(

            data_dir=default_config['data_dir']

        )

    

    def play_game(self, args):

        """

        Start and play a new game.

        

        Args:

            args: Command-line arguments

        """

        try:

            # Load configuration profile

            if args.difficulty:

                self.config_manager.set_profile(args.difficulty)

            

            game_config = self.config_manager.get_current_profile()

            

            # Override with custom settings if provided

            if args.min:

                game_config['min_number'] = args.min

            if args.max:

                game_config['max_number'] = args.max

            if args.attempts:

                game_config['max_attempts'] = args.attempts

            

            # Create game

            self.current_game = GameEngine(**game_config)

            

            # Display game info

            print("\n" + "="*60)

            print("🎮 PROBABILITY-GUIDED NUMBER GUESSING SIMULATOR")

            print("="*60)

            print(f"Difficulty: {self.config_manager.current_profile.upper()}")

            print(f"Range: {game_config['min_number']} - {game_config['max_number']}")

            print(f"Maximum Attempts: {game_config['max_attempts']}")

            print(f"Game ID: {self.current_game.game_id}")

            print("="*60 + "\n")

            

            # Game loop

            while not self.current_game.finished:

                try:

                    # Get user input

                    guess_input = input(f"Enter your guess ({self.current_game.min_number}-{self.current_game.max_number}): ").strip()

                    

                    if guess_input.lower() in ['quit', 'exit', 'q']:

                        print("\n👋 Game abandoned. Thanks for playing!")

                        return

                    

                    # Validate and make guess

                    guess = InputValidator.validate_number(

                        guess_input,

                        self.current_game.min_number,

                        self.current_game.max_number,

                        "Guess",

                    )

                    

                    result = self.current_game.make_guess(guess)

                    

                    # Display result

                    print()

                    if result['correct']:

                        print(result['message'])

                        print(f"🏆 Score: {result['attempts']} attempts")

                    elif result['game_over']:

                        print(result['message'])

                    else:

                        print(result['feedback'])

                        if result.get('hint'):

                            print(f"💡 Hint: {result['hint']}")

                        print(f"📊 Attempts: {result['attempts']}/{self.current_game.max_attempts}")

                        

                        # Show probability info if verbose

                        if args.verbose:

                            prob_info = result.get('probability_info', {})

                            print(f"🔍 Remaining possibilities: {prob_info.get('remaining_possibilities', 'N/A')}")

                    print()

                    

                except ValidationError as e:

                    print(f"❌ Invalid input: {e}\n")

                except Exception as e:

                    print(f"❌ Error: {e}\n")

                    logger.exception("Error during gameplay")

            

            # Save game

            if args.save:

                game_data = self.current_game.get_game_data()

                if self.storage.save_game(game_data):

                    print("💾 Game saved successfully!")

                else:

                    print("⚠️ Failed to save game.")

            

            # Display statistics

            stats = self.current_game.get_statistics()

            print("\n" + "="*60)

            print("📈 GAME STATISTICS")

            print("="*60)

            print(f"Status: {stats['status'].upper()}")

            print(f"Attempts: {stats['attempts']}/{self.current_game.max_attempts}")

            print(f"Efficiency: {stats['efficiency']}%")

            print(f"Target Number: {stats['target_number']}")

            print(f"Guess History: {', '.join(map(str, stats['guess_history']))}")

            print("="*60 + "\n")

            

        except ConfigurationError as e:

            print(f"❌ Configuration error: {e}")

            sys.exit(1)

        except Exception as e:

            print(f"❌ Unexpected error: {e}")

            logger.exception("Unexpected error in play_game")

            sys.exit(1)

    

    def show_statistics(self, args):

        """

        Display game statistics.

        

        Args:

            args: Command-line arguments

        """

        try:

            games = self.storage.load_all_games()

            

            if not games:

                print("📊 No games found in history.")

                return

            

            stats = GameStatistics.calculate_statistics(games)

            

            print("\n" + "="*60)

            print("📈 OVERALL STATISTICS")

            print("="*60)

            print(f"Total Games: {stats['total_games']}")

            print(f"Games Won: {stats['games_won']}")

            print(f"Games Lost: {stats['games_lost']}")

            print(f"Win Rate: {stats['win_rate']}%")

            print(f"Total Attempts: {stats['total_attempts']}")

            print(f"Average Attempts: {stats['average_attempts']}")

            print(f"Best Score: {stats['best_score'] or 'N/A'} attempts")

            print(f"Worst Score: {stats['worst_score'] or 'N/A'} attempts")

            if stats.get('average_attempts_won'):

                print(f"Average Attempts (Won Games): {stats['average_attempts_won']}")

            print("="*60 + "\n")

            

            # Show recent games if verbose

            if args.verbose:

                print("📜 RECENT GAMES (Last 5)")

                print("-"*60)

                for game in games[-5:]:

                    status = "WON" if game.get('won') else "LOST"

                    print(f"Game {game.get('game_id', 'N/A')[:8]}: {status} - "

                          f"{game.get('attempts', 'N/A')} attempts")

                print()

            

        except Exception as e:

            print(f"❌ Error loading statistics: {e}")

            logger.exception("Error in show_statistics")

    

    def export_data(self, args):

        """

        Export game data to CSV.

        

        Args:

            args: Command-line arguments

        """

        try:

            output_path = args.output or "game_export.csv"

            

            if self.storage.export_to_csv(output_path):

                print(f"✅ Data exported successfully to: {output_path}")

            else:

                print(f"❌ Failed to export data.")

                

        except Exception as e:

            print(f"❌ Export error: {e}")

            logger.exception("Error in export_data")

    

    def import_data(self, args):

        """

        Import game data from CSV.

        

        Args:

            args: Command-line arguments

        """

        try:

            input_path = args.input

            

            # Validate file exists

            InputValidator.validate_file_path(input_path, must_exist=True, extension='.csv')

            

            if self.storage.import_from_csv(input_path):

                print(f"✅ Data imported successfully from: {input_path}")

            else:

                print(f"❌ Failed to import data.")

                

        except ValidationError as e:

            print(f"❌ Validation error: {e}")

        except Exception as e:

            print(f"❌ Import error: {e}")

            logger.exception("Error in import_data")

    

    def manage_config(self, args):

        """

        Manage configuration profiles.

        

        Args:

            args: Command-line arguments

        """

        try:

            if args.list:

                profiles = self.config_manager.list_profiles()

                print("\n📋 Available Profiles:")

                print("-"*40)

                for profile in profiles:

                    config = self.config_manager.get_profile(profile)

                    print(f"\n{profile.upper()}:")

                    print(f"  Range: {config['min_number']}-{config['max_number']}")

                    print(f"  Max Attempts: {config['max_attempts']}")

                    print(f"  Hint Frequency: Every {config['hint_frequency']} attempts")

                print()

            

            elif args.show:

                profile = args.show

                config = self.config_manager.get_profile(profile)

                print(f"\n⚙️ Profile: {profile.upper()}")

                print("-"*40)

                for key, value in config.items():

                    print(f"{key}: {value}")

                print()

                

        except ConfigurationError as e:

            print(f"❌ Configuration error: {e}")

        except Exception as e:

            print(f"❌ Error: {e}")

            logger.exception("Error in manage_config")

    

def main():

    """Main entry point for the CLI."""

    parser = argparse.ArgumentParser(

        description="Probability-Guided Number Guessing Simulator",

        formatter_class=argparse.RawDescriptionHelpFormatter,

        epilog="""

Examples:

  guess-sim play                    # Play with default settings

  guess-sim play -d hard            # Play on hard difficulty

  guess-sim play --min 1 --max 500  # Custom range

  guess-sim stats                   # View statistics

  guess-sim export -o games.csv     # Export to CSV

  guess-sim import -i games.csv     # Import from CSV

  guess-sim config --list           # List all profiles

        """

    )

    

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    

    # Play command

    play_parser = subparsers.add_parser('play', help='Start a new game')

    play_parser.add_argument('-d', '--difficulty', choices=['easy', 'medium', 'hard', 'expert'],

                            help='Difficulty level')

    play_parser.add_argument('--min', type=int, help='Minimum number')

    play_parser.add_argument('--max', type=int, help='Maximum number')

    play_parser.add_argument('-a', '--attempts', type=int, help='Maximum attempts')

    play_parser.add_argument('-s', '--save', action='store_true', help='Save game after completion')

    play_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    

    # Stats command

    stats_parser = subparsers.add_parser('stats', help='View statistics')

    stats_parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed statistics')

    

    # Export command

    export_parser = subparsers.add_parser('export', help='Export game data')

    export_parser.add_argument('-o', '--output', help='Output file path')

    

    # Import command

    import_parser = subparsers.add_parser('import', help='Import game data')

    import_parser.add_argument('-i', '--input', required=True, help='Input file path')

    

    # Config command

    config_parser = subparsers.add_parser('config', help='Manage configuration')

    config_parser.add_argument('--list', action='store_true', help='List all profiles')

    config_parser.add_argument('--show', help='Show specific profile')

    

    args = parser.parse_args()

    

    if not args.command:

        parser.print_help()

        sys.exit(0)

    

    # Create CLI instance and run command

    cli = CLI()

    

    if args.command == 'play':

        cli.play_game(args)

    elif args.command == 'stats':

        cli.show_statistics(args)

    elif args.command == 'export':

        cli.export_data(args)

    elif args.command == 'import':

        cli.import_data(args)

    elif args.command == 'config':

        cli.manage_config(args)

if __name__ == "__main__":

    main()

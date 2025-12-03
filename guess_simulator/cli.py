"""
Command Line Interface Module
Main CLI for the Probability-Guided Number Guessing Simulator.
"""

import argparse
import sys
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
        self.current_game = None

    def setup_logging(self):
        """Set up logging based on configuration."""
        config = self.config_manager.get_default_config()
        logger.setup(
            log_file=config["log_file"],
            log_level=config["log_level"],
            console_output=False,  # CLI handles its own output
        )

    def setup_storage(self):
        """Set up storage based on configuration."""
        default_config = self.config_manager.get_default_config()

        return GameStorage(data_dir=default_config["data_dir"])

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
                game_config["min_number"] = args.min
            if args.max:
                game_config["max_number"] = args.max
            if args.attempts:
                game_config["max_attempts"] = args.attempts

            # Create game
            self.current_game = GameEngine(**game_config)

            # Display game info
            print("\n" + "=" * 60)
            print("🎮 PROBABILITY-GUIDED NUMBER GUESSING SIMULATOR")
            print("=" * 60)
            print("Difficulty: {}".format(self.config_manager.current_profile.upper()))
            print(
                "Range: {} - {}".format(
                    game_config["min_number"], game_config["max_number"]
                )
            )
            print("Maximum Attempts: {}".format(game_config["max_attempts"]))
            print("Game ID: {}".format(self.current_game.game_id))
            print("=" * 60 + "\n")

            # Game loop
            while not self.current_game.finished:
                try:
                    # Get user input
                    guess_input = input(
                        "Enter your guess ({}-{}): ".format(
                            self.current_game.min_number, self.current_game.max_number
                        )
                    ).strip()

                    if guess_input.lower() in ["quit", "exit", "q"]:
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
                    if result["correct"]:
                        print(result["message"])
                        print("🏆 Score: {} attempts".format(result["attempts"]))
                    elif result["game_over"]:
                        print(result["message"])
                    else:
                        print(result["feedback"])
                        if result.get("hint"):
                            print("💡 Hint: {}".format(result["hint"]))
                        print(
                            "📊 Attempts: {}/{}".format(
                                result["attempts"], self.current_game.max_attempts
                            )
                        )

                        # Show probability info if verbose
                        if args.verbose:
                            prob_info = result.get("probability_info", {})
                            print(
                                "🔍 Remaining possibilities: {}".format(
                                    prob_info.get("remaining_possibilities", "N/A")
                                )
                            )
                    print()

                except ValidationError as e:
                    print("❌ Invalid input: {}\n".format(e))
                except Exception as e:
                    print("❌ Error: {}\n".format(e))
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
            print("\n" + "=" * 60)
            print("📈 GAME STATISTICS")
            print("=" * 60)
            print("Status: {}".format(stats["status"].upper()))
            print(
                "Attempts: {}/{}".format(
                    stats["attempts"], self.current_game.max_attempts
                )
            )
            print("Efficiency: {}%".format(stats["efficiency"]))
            print("Target Number: {}".format(stats["target_number"]))
            print(
                "Guess History: {}".format(", ".join(map(str, stats["guess_history"])))
            )
            print("=" * 60 + "\n")

        except ConfigurationError as e:
            print("❌ Configuration error: {}".format(e))
            sys.exit(1)
        except Exception as e:
            print("❌ Unexpected error: {}".format(e))
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

            print("\n" + "=" * 60)
            print("📈 OVERALL STATISTICS")
            print("=" * 60)
            print("Total Games: {}".format(stats["total_games"]))
            print("Games Won: {}".format(stats["games_won"]))
            print("Games Lost: {}".format(stats["games_lost"]))
            print("Win Rate: {}%".format(stats["win_rate"]))
            print("Total Attempts: {}".format(stats["total_attempts"]))
            print("Average Attempts: {}".format(stats["average_attempts"]))
            print("Best Score: {} attempts".format(stats["best_score"] or "N/A"))
            print("Worst Score: {} attempts".format(stats["worst_score"] or "N/A"))
            if stats.get("average_attempts_won"):
                print(
                    "Average Attempts (Won Games): {}".format(
                        stats["average_attempts_won"]
                    )
                )
            print("=" * 60 + "\n")

            # Show recent games if verbose
            if args.verbose:
                print("📜 RECENT GAMES (Last 5)")
                print("-" * 60)
                for game in games[-5:]:
                    status = "WON" if game.get("won") else "LOST"
                    game_id_short = game.get("game_id", "N/A")[:8]
                    print(
                        "Game {}: {} - {} attempts".format(
                            game_id_short, status, game.get("attempts", "N/A")
                        )
                    )
                print()

        except Exception as e:
            print("❌ Error loading statistics: {}".format(e))
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
                print("✅ Data exported successfully to: {}".format(output_path))
            else:
                print("❌ Failed to export data.")

        except Exception as e:
            print("❌ Export error: {}".format(e))
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
            InputValidator.validate_file_path(
                input_path, must_exist=True, extension=".csv"
            )

            if self.storage.import_from_csv(input_path):
                print("✅ Data imported successfully from: {}".format(input_path))
            else:
                print("❌ Failed to import data.")

        except ValidationError as e:
            print("❌ Validation error: {}".format(e))
        except Exception as e:
            print("❌ Import error: {}".format(e))
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
                print("-" * 40)
                for profile in profiles:
                    config = self.config_manager.get_profile(profile)
                    print("\n{}:".format(profile.upper()))
                    print(
                        "  Range: {}-{}".format(
                            config["min_number"], config["max_number"]
                        )
                    )
                    print("  Max Attempts: {}".format(config["max_attempts"]))
                    print(
                        "  Hint Frequency: Every {} attempts".format(
                            config["hint_frequency"]
                        )
                    )
                print()

            elif args.show:
                profile = args.show
                config = self.config_manager.get_profile(profile)
                print("\n⚙️ Profile: {}".format(profile.upper()))
                print("-" * 40)
                for key, value in config.items():
                    print("{}: {}".format(key, value))
                print()

        except ConfigurationError as e:
            print("❌ Configuration error: {}".format(e))
        except Exception as e:
            print("❌ Error: {}".format(e))
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
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Play command
    play_parser = subparsers.add_parser("play", help="Start a new game")
    play_parser.add_argument(
        "-d",
        "--difficulty",
        choices=["easy", "medium", "hard", "expert"],
        help="Difficulty level",
    )
    play_parser.add_argument("--min", type=int, help="Minimum number")
    play_parser.add_argument("--max", type=int, help="Maximum number")
    play_parser.add_argument("-a", "--attempts", type=int, help="Maximum attempts")
    play_parser.add_argument(
        "-s", "--save", action="store_true", help="Save game after completion"
    )
    play_parser.add_argument(
        "-v", "--verbose", action="store_true", help="Verbose output"
    )

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="View statistics")
    stats_parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show detailed statistics"
    )

    # Export command
    export_parser = subparsers.add_parser("export", help="Export game data")
    export_parser.add_argument("-o", "--output", help="Output file path")

    # Import command
    import_parser = subparsers.add_parser("import", help="Import game data")
    import_parser.add_argument("-i", "--input", required=True, help="Input file path")

    # Config command
    config_parser = subparsers.add_parser("config", help="Manage configuration")
    config_parser.add_argument("--list", action="store_true", help="List all profiles")
    config_parser.add_argument("--show", help="Show specific profile")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Create CLI instance and run command
    cli = CLI()

    if args.command == "play":
        cli.play_game(args)
    elif args.command == "stats":
        cli.show_statistics(args)
    elif args.command == "export":
        cli.export_data(args)
    elif args.command == "import":
        cli.import_data(args)
    elif args.command == "config":
        cli.manage_config(args)


if __name__ == "__main__":
    main()

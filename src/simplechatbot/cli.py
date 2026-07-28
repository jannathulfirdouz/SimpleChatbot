"""CLI interface entry point for SimpleChatbot.

This module provides a beautiful terminal-based chat interface using
the Rich library for enhanced formatting, colors, and styling.
It serves as the main entry point for the CLI chatbot experience.
"""

import sys

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

from simplechatbot.chatbot import SimpleChatbot
from simplechatbot.config import AVAILABLE_MODELS

console = Console()


def display_banner() -> None:
    """Display the application banner with branding."""
    banner_text = Text()
    banner_text.append("SimpleChatbot", style="bold bright_cyan")
    banner_text.append(" - Powered by ", style="dim")
    banner_text.append("Amazon Bedrock", style="bold yellow")

    console.print()
    console.print(
        Panel(
            banner_text,
            title="[bold]Build the Builder Workshop[/bold]",
            subtitle="[dim]Press Ctrl+C to exit[/dim]",
            border_style="bright_cyan",
            padding=(1, 2),
        )
    )
    console.print()


def display_help() -> None:
    """Display available commands in a formatted table."""
    table = Table(
        title="Available Commands",
        border_style="dim",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("Command", style="green", min_width=20)
    table.add_column("Description", style="white")

    commands = [
        ("/quit", "Exit the chatbot"),
        ("/clear", "Clear conversation history"),
        ("/model", "Show current model information"),
        ("/models", "List all available models"),
        ("/switch <key>", "Switch to a different model"),
        ("/help", "Show this help message"),
    ]

    for cmd, desc in commands:
        table.add_row(cmd, desc)

    console.print(table)
    console.print()


def display_models(current_key: str) -> None:
    """Display available models in a formatted table.

    Args:
        current_key: The key of the currently active model.
    """
    table = Table(
        title="Available Anthropic Models",
        border_style="dim",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("Key", style="green", min_width=18)
    table.add_column("Name", style="white", min_width=20)
    table.add_column("Description", style="dim")
    table.add_column("Active", justify="center")

    for key, model in AVAILABLE_MODELS.items():
        active = "[bold green]●[/bold green]" if key == current_key else ""
        table.add_row(key, model["name"], model["description"], active)

    console.print(table)
    console.print()


def main() -> None:
    """Main entry point for the CLI chatbot.

    Initializes the chatbot and runs an interactive loop with
    Rich-formatted output for a polished terminal experience.
    """
    display_banner()
    display_help()

    # Initialize the chatbot
    try:
        chatbot = SimpleChatbot()
    except ConnectionError as e:
        console.print(
            Panel(
                f"[bold red]Initialization Error[/bold red]\n\n{e}",
                border_style="red",
                title="Error",
            )
        )
        sys.exit(1)
    except ValueError as e:
        console.print(f"[bold red]Configuration Error:[/bold red] {e}")
        sys.exit(1)

    # Display current model info
    model_info = chatbot.get_current_model_info()
    console.print(
        f"[dim]Using model:[/dim] [bold cyan]{model_info['name']}[/bold cyan]"
    )
    console.print(f"[dim]Model ID:[/dim] {model_info['model_id']}")
    console.print()

    # Main chat loop
    while True:
        try:
            # Get user input
            user_input = Prompt.ask("[bold green]You[/bold green]")

            if not user_input.strip():
                continue

            # Handle commands
            if user_input.startswith("/"):
                parts = user_input.strip().split(maxsplit=1)
                command = parts[0].lower()

                if command == "/quit":
                    console.print("\n[dim]Goodbye! Thanks for chatting.[/dim]\n")
                    break

                elif command == "/clear":
                    chatbot.clear_history()
                    console.print("[dim italic]Conversation history cleared.[/dim italic]\n")
                    continue

                elif command == "/model":
                    info = chatbot.get_current_model_info()
                    console.print(
                        Panel(
                            f"[bold]{info['name']}[/bold]\n"
                            f"[dim]ID:[/dim] {info['model_id']}\n"
                            f"[dim]Description:[/dim] {info['description']}",
                            title="Current Model",
                            border_style="cyan",
                        )
                    )
                    console.print()
                    continue

                elif command == "/models":
                    display_models(chatbot.model_key)
                    continue

                elif command == "/switch":
                    if len(parts) < 2:
                        console.print(
                            "[yellow]Usage:[/yellow] /switch <model-key>\n"
                            "[dim]Use /models to see available keys.[/dim]\n"
                        )
                        continue
                    model_key = parts[1].strip()
                    try:
                        name = chatbot.set_model(model_key)
                        console.print(
                            f"[bold green]Switched to:[/bold green] {name}\n"
                        )
                    except ValueError as e:
                        console.print(f"[bold red]Error:[/bold red] {e}\n")
                    continue

                elif command == "/help":
                    display_help()
                    continue

                else:
                    console.print(
                        "[yellow]Unknown command.[/yellow] Type [green]/help[/green] for available commands.\n"
                    )
                    continue

            # Get response from the model
            with console.status("[bold cyan]Thinking...[/bold cyan]", spinner="dots"):
                response = chatbot.get_response(user_input)

            # Display the response with Markdown rendering
            console.print()
            console.print(
                Panel(
                    Markdown(response),
                    title="[bold bright_cyan]Assistant[/bold bright_cyan]",
                    border_style="bright_cyan",
                    padding=(0, 1),
                )
            )
            console.print()

        except RuntimeError as e:
            console.print(f"\n[bold red]Error:[/bold red] {e}\n")

        except KeyboardInterrupt:
            console.print("\n\n[dim]Goodbye! Thanks for chatting.[/dim]\n")
            break

        except EOFError:
            console.print("\n\n[dim]Goodbye! Thanks for chatting.[/dim]\n")
            break


if __name__ == "__main__":
    main()

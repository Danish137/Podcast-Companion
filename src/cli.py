"""
Fermi Companion - Interactive CLI
Simple terminal interface for testing the companion logic without starting the API.
"""

from src.companion import FermiCompanion, ConversationState
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
import sys

console = Console()

def main():
    console.print(Panel.fit("[bold blue]Fermi Companion - Test Interface[/bold blue]", border_style="blue"))
    console.print("Type 'quit' or 'exit' to end the session.\\n")
    
    companion = FermiCompanion()
    state = ConversationState()
    
    while True:
        try:
            user_input = Prompt.ask("[bold green]You[/bold green]")
            if user_input.lower() in ["quit", "exit"]:
                break
                
            if not user_input.strip():
                continue
                
            with console.status("[cyan]Thinking...[/cyan]"):
                response = companion.process_message(user_input, state)
            
            console.print(Panel(Markdown(response), title="Fermi Companion", border_style="cyan", padding=(1, 2)))
            console.print()
            
        except KeyboardInterrupt:
            console.print("\\n[yellow]Session ended by user.[/yellow]")
            break
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")

if __name__ == "__main__":
    main()

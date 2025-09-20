#!/usr/bin/env python3

import sys
import os
import signal
from pathlib import Path

# readline is not available on Windows, but it's not needed with prompt-toolkit
try:
    import readline
except ImportError:
    pass  # readline not available on this platform
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.shortcuts import CompleteStyle
import colorama
from colorama import Fore, Back, Style

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from .terminal_engine import TerminalEngine


class PyTerminalCompleter(Completer):
    """
    Auto-completion for the Python terminal.
    """
    
    def __init__(self, terminal_engine):
        self.terminal = terminal_engine
    
    def get_completions(self, document, complete_event):
        # Get the current text before cursor
        text = document.text_before_cursor
        words = text.split()
        
        if not words:
            # No text yet, suggest commands
            for command in self.terminal.builtin_commands.keys():
                yield Completion(command)
        elif len(words) == 1:
            # Complete command name
            partial_command = words[0]
            for command in self.terminal.builtin_commands.keys():
                if command.startswith(partial_command):
                    yield Completion(command, start_position=-len(partial_command))
        else:
            # Complete file/directory names for commands that expect them
            command = words[0]
            if command in ['ls', 'cd', 'cat', 'cp', 'mv', 'rm', 'find', 'grep', 'head', 'tail', 'touch']:
                # Get the last word (partial file/directory name)
                partial_path = words[-1] if words else ""
                
                try:
                    # Determine directory to search in
                    if '/' in partial_path or '\\' in partial_path:
                        # Path contains directory separator
                        path_parts = partial_path.replace('\\', '/').split('/')
                        if len(path_parts) > 1:
                            search_dir = self.terminal.current_directory / Path('/'.join(path_parts[:-1]))
                            partial_name = path_parts[-1]
                        else:
                            search_dir = self.terminal.current_directory
                            partial_name = partial_path
                    else:
                        search_dir = self.terminal.current_directory
                        partial_name = partial_path
                    
                    if search_dir.exists() and search_dir.is_dir():
                        for item in search_dir.iterdir():
                            if item.name.startswith(partial_name):
                                completion_text = item.name
                                if item.is_dir():
                                    completion_text += '/'
                                yield Completion(
                                    completion_text,
                                    start_position=-len(partial_name)
                                )
                except Exception:
                    pass


class PyTerminalInterface:
    """
    Interactive command-line interface for the Python terminal.
    """
    
    def __init__(self):
        # Initialize colorama for cross-platform color support
        colorama.init(autoreset=True)
        
        self.terminal_engine = TerminalEngine()
        self.history = InMemoryHistory()
        self.completer = PyTerminalCompleter(self.terminal_engine)
        self.running = True
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        if hasattr(signal, 'SIGTSTP'):
            signal.signal(signal.SIGTSTP, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C and Ctrl+Z signals."""
        if signum == signal.SIGINT:
            print("\nKeyboardInterrupt")
            # Don't exit, just show new prompt
        elif hasattr(signal, 'SIGTSTP') and signum == signal.SIGTSTP:
            print("\nStopped")
    
    def _print_welcome(self):
        """Print welcome message."""
        print(f"{Fore.CYAN}{Style.BRIGHT}")
        print("╔══════════════════════════════════════════════════════════════════════════════╗")
        print("║                              PyTerminal v1.0                                ║")
        print("║                         Python-based Terminal Emulator                      ║")
        print("╠══════════════════════════════════════════════════════════════════════════════╣")
        print("║  Features:                                                                   ║")
        print("║    • File operations (ls, cd, mkdir, rm, cp, mv, etc.)                     ║")
        print("║    • System monitoring (ps, top, free, df, etc.)                           ║")
        print("║    • Command history and auto-completion                                     ║")
        print("║    • Environment management                                                  ║")
        print("║                                                                              ║")
        print("║  Type 'help' for available commands or 'exit' to quit.                     ║")
        print("╚══════════════════════════════════════════════════════════════════════════════╝")
        print(f"{Style.RESET_ALL}")
        print()
    
    def _format_prompt(self):
        """Format the command prompt with colors."""
        prompt_str = self.terminal_engine.get_prompt()
        # Add colors to the prompt
        colored_prompt = f"{Fore.GREEN}{Style.BRIGHT}PyTerminal {Fore.BLUE}{prompt_str}{Style.RESET_ALL}"
        return colored_prompt
    
    def _print_output(self, stdout: str, stderr: str, exit_code: int):
        """Print command output with appropriate colors."""
        if stdout:
            print(stdout)
        
        if stderr:
            print(f"{Fore.RED}{stderr}{Style.RESET_ALL}")
    
    def run_interactive(self):
        """Run the interactive terminal."""
        self._print_welcome()
        
        try:
            while self.running:
                try:
                    # Get command input with auto-completion
                    command_line = prompt(
                        self._format_prompt(),
                        history=self.history,
                        auto_suggest=AutoSuggestFromHistory(),
                        completer=self.completer,
                        complete_style=CompleteStyle.READLINE_LIKE
                    )
                    
                    if command_line.strip():
                        # Execute command
                        exit_code, stdout, stderr = self.terminal_engine.execute_command(command_line)
                        
                        # Print output
                        self._print_output(stdout, stderr, exit_code)
                        
                except KeyboardInterrupt:
                    print()  # New line after ^C
                    continue
                except EOFError:
                    # Ctrl+D pressed
                    print("\nExiting...")
                    break
                    
        except Exception as e:
            print(f"{Fore.RED}Fatal error: {str(e)}{Style.RESET_ALL}")
            return 1
        
        return 0
    
    def run_command(self, command: str):
        """Run a single command (for non-interactive use)."""
        try:
            exit_code, stdout, stderr = self.terminal_engine.execute_command(command)
            self._print_output(stdout, stderr, exit_code)
            return exit_code
        except Exception as e:
            print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
            return 1


def main():
    """Main entry point."""
    interface = PyTerminalInterface()
    
    # Check if running interactively or with command arguments
    if len(sys.argv) > 1:
        # Non-interactive mode: run single command
        command = ' '.join(sys.argv[1:])
        return interface.run_command(command)
    else:
        # Interactive mode
        return interface.run_interactive()


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)
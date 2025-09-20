#!/usr/bin/env python3
"""
PyTerminal Launcher
Simple script to run the Python-based terminal.
"""

import sys
import os

# Add src to Python path and initialize logging before any other imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from src.log_config import initialize_logging
initialize_logging()

try:
    from main import main
    if __name__ == "__main__":
        main()
except ImportError as e:
    print(f"Import error: {e}")
    print("Falling back to direct terminal engine...")
    
    # Fallback: run terminal engine directly
    from terminal_engine import TerminalEngine
    
    print("🐍 Python Terminal")
    print("Type 'help' for commands or 'exit' to quit.")
    print("Try natural language commands like 'create a file called test.txt'")
    print()
    
    terminal = TerminalEngine()
    
    try:
        while True:
            try:
                command = input(terminal.get_prompt())
                if command.strip():
                    exit_code, stdout, stderr = terminal.execute_command(command)
                    
                    if stdout:
                        print(stdout)
                    if stderr:
                        print(f"\033[91m{stderr}\033[0m")  # Red color for errors
                        
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit.")
                continue
            except EOFError:
                print("\nExiting...")
                break
                
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
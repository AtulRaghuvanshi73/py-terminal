#!/usr/bin/env python3

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import terminal engine directly
from terminal_engine import TerminalEngine


def test_basic_commands():
    """Test basic terminal commands."""
    print("Testing Python Terminal...")
    
    terminal = TerminalEngine()
    
    # Test basic commands
    test_commands = [
        "pwd",
        "help",
        "ls",
        "whoami",
        "date"
    ]
    
    for cmd in test_commands:
        print(f"\n--- Testing: {cmd} ---")
        exit_code, stdout, stderr = terminal.execute_command(cmd)
        print(f"Exit code: {exit_code}")
        if stdout:
            print(f"Output: {stdout}")
        if stderr:
            print(f"Error: {stderr}")


def test_ai_commands():
    """Test AI natural language commands."""
    print("\n\nTesting AI Commands...")
    
    terminal = TerminalEngine()
    
    # Test AI interpretation
    ai_queries = [
        "show me all files",
        "where am I", 
        "create a new file called test.txt",
    ]
    
    for query in ai_queries:
        print(f"\n--- Testing AI: {query} ---")
        exit_code, stdout, stderr = terminal.execute_command(query)
        print(f"Exit code: {exit_code}")
        if stdout:
            print(f"Output: {stdout}")
        if stderr:
            print(f"Error: {stderr}")


if __name__ == "__main__":
    test_basic_commands()
    test_ai_commands()
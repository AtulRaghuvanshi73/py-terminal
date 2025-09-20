#!/usr/bin/env python3

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from terminal_engine import TerminalEngine


def demo_commands():
    """Demonstrate various terminal commands."""
    print("🚀 Python Terminal Demo")
    print("=" * 50)
    
    terminal = TerminalEngine()
    
    demo_commands = [
        ("pwd", "Show current directory"),
        ("ls -la", "List all files with details"),
        ("whoami", "Show current user"),
        ("date", "Show current date and time"),
        ("free -h", "Show memory usage"),
        ("df -h", "Show disk usage"), 
        ("ps", "Show running processes"),
        ("create a new file called demo.txt", "AI: Create file using natural language"),
        ("show me all files", "AI: List files using natural language"),
        ("ai help", "Show AI capabilities"),
    ]
    
    for cmd, description in demo_commands:
        print(f"\n📝 {description}")
        print(f"💻 Command: {cmd}")
        print("-" * 40)
        
        exit_code, stdout, stderr = terminal.execute_command(cmd)
        
        if stdout:
            # Limit output length for demo
            output_lines = stdout.split('\n')
            if len(output_lines) > 10:
                print('\n'.join(output_lines[:10]))
                print(f"... ({len(output_lines) - 10} more lines)")
            else:
                print(stdout)
        
        if stderr:
            print(f"❌ Error: {stderr}")
        
        print(f"✅ Exit code: {exit_code}")
        print()


if __name__ == "__main__":
    demo_commands()
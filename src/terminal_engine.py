import os
import sys
import shlex
import subprocess
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
import platform

from commands.file_operations import FileOperations
from commands.system_commands import SystemCommands
from system_monitor import SystemMonitor
from ai_interpreter import AICommandInterpreter


class TerminalEngine:
    """
    Core terminal engine that processes commands and manages terminal state.
    """
    
    def __init__(self):
        self.current_directory = Path.cwd()
        self.home_directory = Path.home()
        self.command_history = []
        self.environment_vars = dict(os.environ)
        self.aliases = {}
        
        # Initialize command modules
        self.file_ops = FileOperations(self)
        self.system_commands = SystemCommands(self)
        self.system_monitor = SystemMonitor()
        self.ai_interpreter = AICommandInterpreter()
        
        # Built-in commands mapping
        self.builtin_commands = {
            # File operations
            'ls': self.file_ops.ls,
            'cd': self.file_ops.cd,
            'pwd': self.file_ops.pwd,
            'mkdir': self.file_ops.mkdir,
            'rmdir': self.file_ops.rmdir,
            'rm': self.file_ops.rm,
            'cp': self.file_ops.cp,
            'mv': self.file_ops.mv,
            'touch': self.file_ops.touch,
            'cat': self.file_ops.cat,
            'head': self.file_ops.head,
            'tail': self.file_ops.tail,
            'find': self.file_ops.find,
            'grep': self.file_ops.grep,
            
            # System commands
            'ps': self.system_commands.ps,
            'kill': self.system_commands.kill,
            'jobs': self.system_commands.jobs,
            'bg': self.system_commands.bg,
            'fg': self.system_commands.fg,
            'env': self.system_commands.env,
            'export': self.system_commands.export,
            'alias': self.system_commands.alias,
            'unalias': self.system_commands.unalias,
            'which': self.system_commands.which,
            'whoami': self.system_commands.whoami,
            'date': self.system_commands.date,
            'uptime': self.system_commands.uptime,
            
            # System monitoring
            'top': self.system_monitor.top,
            'htop': self.system_monitor.htop,
            'free': self.system_monitor.free,
            'df': self.system_monitor.df,
            'du': self.system_monitor.du,
            'lscpu': self.system_monitor.lscpu,
            'lsblk': self.system_monitor.lsblk,
            
            # Terminal built-ins
            'help': self.help,
            'exit': self.exit,
            'clear': self.clear,
            'history': self.history,
            'ai': self.ai_command,
        }
    
    def execute_command(self, command_line: str) -> Tuple[int, str, str]:
        """
        Execute a command and return exit code, stdout, and stderr.
        
        Args:
            command_line: The complete command line to execute
            
        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        if not command_line.strip():
            return 0, "", ""
        
        # Add to history
        self.command_history.append(command_line)
        
        try:
            # Check if this might be a natural language query
            # (contains common natural language indicators)
            natural_language_indicators = [
                ' a ', ' the ', ' and ', ' or ', ' to ', ' from ', ' in ', ' of ',
                'create', 'make', 'show me', 'list all', 'find all', 'what is',
                'where am', 'how much', 'search for'
            ]
            
            is_natural_language = any(
                indicator in command_line.lower() for indicator in natural_language_indicators
            )
            
            # Try AI interpretation first if it looks like natural language
            if is_natural_language:
                success, ai_command, explanation = self.ai_interpreter.interpret(command_line)
                if success:
                    print(f"\n🤖 AI Interpreter: {explanation}\n")
                    return self.execute_command(ai_command)  # Recursively execute the interpreted command
            
            # Parse command line
            args = self.parse_command_line(command_line)
            if not args:
                return 0, "", ""
            
            command = args[0]
            
            # Check for aliases
            if command in self.aliases:
                alias_command = self.aliases[command]
                # Replace the command with its alias and re-parse
                new_command_line = alias_command + " " + " ".join(args[1:])
                args = self.parse_command_line(new_command_line)
                command = args[0]
            
            # Execute built-in commands
            if command in self.builtin_commands:
                return self.builtin_commands[command](args[1:])
            
            # Execute external commands
            return self.execute_external_command(args)
            
        except Exception as e:
            error_msg = f"PyTerminal: {str(e)}"
            return 1, "", error_msg
    
    def parse_command_line(self, command_line: str) -> List[str]:
        """
        Parse command line into arguments, handling quotes and escapes.
        """
        try:
            return shlex.split(command_line)
        except ValueError as e:
            raise ValueError(f"Invalid command syntax: {e}")
    
    def execute_external_command(self, args: List[str]) -> Tuple[int, str, str]:
        """
        Execute external system commands.
        """
        try:
            # Change to current directory for the subprocess
            result = subprocess.run(
                args,
                cwd=str(self.current_directory),
                capture_output=True,
                text=True,
                env=self.environment_vars
            )
            return result.returncode, result.stdout, result.stderr
            
        except FileNotFoundError:
            error_msg = f"PyTerminal: command not found: {args[0]}"
            return 127, "", error_msg
        except Exception as e:
            error_msg = f"PyTerminal: error executing command: {str(e)}"
            return 1, "", error_msg
    
    def get_prompt(self) -> str:
        """
        Generate the terminal prompt string.
        """
        user = os.getenv('USER', os.getenv('USERNAME', 'user'))
        hostname = platform.node()
        
        # Shorten current directory path
        current_path = str(self.current_directory)
        home_path = str(self.home_directory)
        
        if current_path.startswith(home_path):
            display_path = "~" + current_path[len(home_path):]
        else:
            display_path = current_path
        
        return f"{user}@{hostname}:{display_path}$ "
    
    # Built-in command implementations
    def help(self, args: List[str]) -> Tuple[int, str, str]:
        """Display help information."""
        help_text = """
PyTerminal - Python-based Terminal

Built-in Commands:
  File Operations:
    ls [path]         - List directory contents
    cd [path]         - Change directory
    pwd               - Print working directory
    mkdir <dir>       - Create directory
    rmdir <dir>       - Remove empty directory
    rm <file>         - Remove file/directory
    cp <src> <dst>    - Copy file/directory
    mv <src> <dst>    - Move/rename file/directory
    touch <file>      - Create empty file or update timestamp
    cat <file>        - Display file contents
    head <file>       - Display first lines of file
    tail <file>       - Display last lines of file
    find <pattern>    - Find files/directories
    grep <pattern>    - Search text patterns in files

  System Commands:
    ps                - Show running processes
    kill <pid>        - Terminate process
    env               - Show environment variables
    export <var>=<val> - Set environment variable
    alias <name>=<cmd> - Create command alias
    which <cmd>       - Show command location
    date              - Show current date/time
    whoami            - Show current user

  System Monitoring:
    top               - Show system processes
    free              - Show memory usage
    df                - Show disk usage
    du <path>         - Show directory usage
    lscpu             - Show CPU information

  Terminal:
    help              - Show this help
    history           - Show command history
    clear             - Clear screen
    exit              - Exit terminal
    ai <query>        - Natural language command interface

  AI Features:
    Just type natural language! For example:
    "create a new file called test.txt"
    "show me all files"
    "copy file1.txt to backup.txt"
    
Type 'ai help' for AI capabilities or 'command --help' for specific command help.
        """
        return 0, help_text.strip(), ""
    
    def exit(self, args: List[str]) -> Tuple[int, str, str]:
        """Exit the terminal."""
        exit_code = 0
        if args:
            try:
                exit_code = int(args[0])
            except ValueError:
                return 1, "", "exit: invalid exit code"
        
        sys.exit(exit_code)
    
    def clear(self, args: List[str]) -> Tuple[int, str, str]:
        """Clear the terminal screen."""
        if platform.system() == "Windows":
            os.system('cls')
        else:
            os.system('clear')
        return 0, "", ""
    
    def history(self, args: List[str]) -> Tuple[int, str, str]:
        """Display command history."""
        if not self.command_history:
            return 0, "No commands in history.", ""
        
        history_output = []
        for i, cmd in enumerate(self.command_history[-50:], 1):  # Show last 50 commands
            history_output.append(f"{i:4d}  {cmd}")
        
        return 0, "\n".join(history_output), ""
    
    def ai_command(self, args: List[str]) -> Tuple[int, str, str]:
        """AI command interface for natural language queries."""
        if not args:
            help_text = self.ai_interpreter.explain_capabilities()
            return 0, help_text, ""
        
        query = " ".join(args)
        
        if query.lower() in ['help', '--help', '-h']:
            help_text = self.ai_interpreter.explain_capabilities()
            return 0, help_text, ""
        
        # Interpret the natural language query
        success, command, explanation = self.ai_interpreter.interpret(query)
        
        if success:
            print(f"\n🤖 AI Interpreter: {explanation}\n")
            # Ask for confirmation before executing
            try:
                response = input("Execute this command? (y/N): ").strip().lower()
                if response in ['y', 'yes']:
                    return self.execute_command(command)
                else:
                    return 0, "Command execution cancelled.", ""
            except (KeyboardInterrupt, EOFError):
                return 0, "Command execution cancelled.", ""
        else:
            return 1, "", f"Could not interpret: '{query}'"

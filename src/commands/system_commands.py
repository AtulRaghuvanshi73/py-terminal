import os
import signal
import platform
import getpass
import shutil
from datetime import datetime
from typing import List, Tuple, Dict
import psutil


class SystemCommands:
    """
    System-level commands for process management and environment handling.
    """
    
    def __init__(self, terminal_engine):
        self.terminal = terminal_engine
        self.background_jobs = {}
        self.job_counter = 0
    
    def ps(self, args: List[str]) -> Tuple[int, str, str]:
        """Show running processes."""
        show_all = False
        show_full = False
        
        for arg in args:
            if arg.startswith('-'):
                if 'a' in arg or 'A' in arg:
                    show_all = True
                if 'f' in arg:
                    show_full = True
        
        try:
            processes = []
            current_user = getpass.getuser()
            
            # Header
            if show_full:
                header = f"{'PID':>7} {'USER':<10} {'CPU%':>5} {'MEM%':>5} {'COMMAND'}"
            else:
                header = f"{'PID':>7} {'TTY':<8} {'TIME':>8} {'CMD'}"
            
            processes.append(header)
            
            for proc in psutil.process_iter(['pid', 'username', 'name', 'cmdline', 'cpu_percent', 'memory_percent']):
                try:
                    pinfo = proc.info
                    
                    # Filter by user unless showing all
                    if not show_all and pinfo['username'] != current_user:
                        continue
                    
                    pid = pinfo['pid']
                    username = pinfo['username'] or 'unknown'
                    name = pinfo['name'] or 'unknown'
                    
                    if show_full:
                        cpu_percent = proc.cpu_percent()
                        memory_percent = pinfo['memory_percent'] or 0
                        cmdline = ' '.join(pinfo['cmdline']) if pinfo['cmdline'] else name
                        
                        # Truncate long command lines
                        if len(cmdline) > 50:
                            cmdline = cmdline[:47] + "..."
                        
                        process_line = f"{pid:>7} {username:<10} {cpu_percent:>4.1f} {memory_percent:>4.1f} {cmdline}"
                    else:
                        # Simplified format
                        process_line = f"{pid:>7} {'pts/0':<8} {'00:00:00':>8} {name}"
                    
                    processes.append(process_line)
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            return 0, "\n".join(processes), ""
            
        except Exception as e:
            return 1, "", f"ps: error: {str(e)}"
    
    def kill(self, args: List[str]) -> Tuple[int, str, str]:
        """Terminate processes by PID."""
        if not args:
            return 1, "", "kill: missing process ID"
        
        signal_num = signal.SIGTERM  # Default signal
        pids = []
        
        for arg in args:
            if arg.startswith('-'):
                # Signal specification
                try:
                    if arg[1:].isdigit():
                        signal_num = int(arg[1:])
                    else:
                        # Named signal like -KILL, -TERM
                        sig_name = arg[1:].upper()
                        if sig_name.startswith('SIG'):
                            sig_name = sig_name[3:]
                        signal_num = getattr(signal, f'SIG{sig_name}')
                except (ValueError, AttributeError):
                    return 1, "", f"kill: invalid signal specification: {arg}"
            else:
                try:
                    pids.append(int(arg))
                except ValueError:
                    return 1, "", f"kill: invalid process ID: {arg}"
        
        if not pids:
            return 1, "", "kill: missing process ID"
        
        errors = []
        for pid in pids:
            try:
                os.kill(pid, signal_num)
            except ProcessLookupError:
                errors.append(f"kill: ({pid}) - No such process")
            except PermissionError:
                errors.append(f"kill: ({pid}) - Operation not permitted")
            except Exception as e:
                errors.append(f"kill: ({pid}) - {str(e)}")
        
        if errors:
            return 1, "", "\n".join(errors)
        return 0, "", ""
    
    def jobs(self, args: List[str]) -> Tuple[int, str, str]:
        """Show active background jobs."""
        if not self.background_jobs:
            return 0, "", ""
        
        jobs_list = []
        for job_id, job_info in self.background_jobs.items():
            status = "Running" if job_info['process'].poll() is None else "Done"
            jobs_list.append(f"[{job_id}]  {status:<10} {job_info['command']}")
        
        return 0, "\n".join(jobs_list), ""
    
    def bg(self, args: List[str]) -> Tuple[int, str, str]:
        """Put job in background (simplified implementation)."""
        return 0, "bg: command not fully implemented in this version", ""
    
    def fg(self, args: List[str]) -> Tuple[int, str, str]:
        """Bring job to foreground (simplified implementation)."""
        return 0, "fg: command not fully implemented in this version", ""
    
    def env(self, args: List[str]) -> Tuple[int, str, str]:
        """Display environment variables."""
        env_vars = []
        for key, value in sorted(self.terminal.environment_vars.items()):
            env_vars.append(f"{key}={value}")
        
        return 0, "\n".join(env_vars), ""
    
    def export(self, args: List[str]) -> Tuple[int, str, str]:
        """Set environment variables."""
        if not args:
            # Show exported variables
            return self.env([])
        
        for arg in args:
            if '=' in arg:
                key, value = arg.split('=', 1)
                self.terminal.environment_vars[key] = value
                os.environ[key] = value
            else:
                # Export existing variable
                if arg in self.terminal.environment_vars:
                    os.environ[arg] = self.terminal.environment_vars[arg]
                else:
                    return 1, "", f"export: {arg}: not found"
        
        return 0, "", ""
    
    def alias(self, args: List[str]) -> Tuple[int, str, str]:
        """Create command aliases."""
        if not args:
            # Show all aliases
            if not self.terminal.aliases:
                return 0, "", ""
            
            aliases = []
            for name, command in self.terminal.aliases.items():
                aliases.append(f"alias {name}='{command}'")
            return 0, "\n".join(aliases), ""
        
        for arg in args:
            if '=' in arg:
                name, command = arg.split('=', 1)
                # Remove quotes if present
                if command.startswith('"') and command.endswith('"'):
                    command = command[1:-1]
                elif command.startswith("'") and command.endswith("'"):
                    command = command[1:-1]
                
                self.terminal.aliases[name] = command
            else:
                # Show specific alias
                if arg in self.terminal.aliases:
                    return 0, f"alias {arg}='{self.terminal.aliases[arg]}'", ""
                else:
                    return 1, "", f"alias: {arg}: not found"
        
        return 0, "", ""
    
    def unalias(self, args: List[str]) -> Tuple[int, str, str]:
        """Remove command aliases."""
        if not args:
            return 1, "", "unalias: missing alias name"
        
        errors = []
        for arg in args:
            if arg == '-a':
                # Remove all aliases
                self.terminal.aliases.clear()
            else:
                if arg in self.terminal.aliases:
                    del self.terminal.aliases[arg]
                else:
                    errors.append(f"unalias: {arg}: not found")
        
        if errors:
            return 1, "", "\n".join(errors)
        return 0, "", ""
    
    def which(self, args: List[str]) -> Tuple[int, str, str]:
        """Show the location of a command."""
        if not args:
            return 1, "", "which: missing command name"
        
        results = []
        for command in args:
            # Check built-in commands first
            if command in self.terminal.builtin_commands:
                results.append(f"{command}: shell builtin")
                continue
            
            # Check aliases
            if command in self.terminal.aliases:
                results.append(f"{command}: aliased to '{self.terminal.aliases[command]}'")
                continue
            
            # Check system PATH
            command_path = shutil.which(command)
            if command_path:
                results.append(command_path)
            else:
                results.append(f"{command}: not found")
        
        return 0, "\n".join(results), ""
    
    def whoami(self, args: List[str]) -> Tuple[int, str, str]:
        """Display current username."""
        try:
            username = getpass.getuser()
            return 0, username, ""
        except Exception as e:
            return 1, "", f"whoami: {str(e)}"
    
    def date(self, args: List[str]) -> Tuple[int, str, str]:
        """Display current date and time."""
        try:
            now = datetime.now()
            
            if args and args[0].startswith('+'):
                # Custom format
                format_str = args[0][1:]  # Remove the '+'
                formatted_date = now.strftime(format_str)
                return 0, formatted_date, ""
            else:
                # Default format
                formatted_date = now.strftime("%a %b %d %H:%M:%S %Z %Y")
                return 0, formatted_date, ""
                
        except Exception as e:
            return 1, "", f"date: {str(e)}"
    
    def uptime(self, args: List[str]) -> Tuple[int, str, str]:
        """Show system uptime and load average."""
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            current_time = datetime.now()
            uptime_duration = current_time - boot_time
            
            # Format uptime
            days = uptime_duration.days
            hours, remainder = divmod(uptime_duration.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            
            uptime_str = f"up {days} days, {hours}:{minutes:02d}"
            
            # Get load average (Unix-like systems)
            try:
                load_avg = os.getloadavg()
                load_str = f"load average: {load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}"
            except (AttributeError, OSError):
                # Windows doesn't have getloadavg
                load_str = "load average: unavailable"
            
            # Get number of users (simplified)
            users = len(set(proc.username() for proc in psutil.process_iter() if proc.username()))
            user_str = f"{users} users" if users != 1 else "1 user"
            
            current_time_str = current_time.strftime("%H:%M:%S")
            
            result = f" {current_time_str} {uptime_str}, {user_str}, {load_str}"
            return 0, result, ""
            
        except Exception as e:
            return 1, "", f"uptime: {str(e)}"
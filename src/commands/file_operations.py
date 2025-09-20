import os
import shutil
import stat
import time
import fnmatch
import re
from pathlib import Path
from typing import List, Tuple, Optional
from datetime import datetime


class FileOperations:
    """
    File and directory operations for the Python terminal.
    """
    
    def __init__(self, terminal_engine):
        self.terminal = terminal_engine
    
    def ls(self, args: List[str]) -> Tuple[int, str, str]:
        """List directory contents."""
        # Parse arguments
        show_all = False
        long_format = False
        human_readable = False
        target_path = None
        
        for arg in args:
            if arg.startswith('-'):
                if 'a' in arg:
                    show_all = True
                if 'l' in arg:
                    long_format = True
                if 'h' in arg:
                    human_readable = True
            else:
                target_path = arg
        
        if target_path is None:
            target_path = self.terminal.current_directory
        else:
            target_path = self._resolve_path(target_path)
        
        try:
            if not target_path.exists():
                return 1, "", f"ls: cannot access '{target_path}': No such file or directory"
            
            if target_path.is_file():
                # If it's a file, just show the file
                if long_format:
                    return 0, self._format_file_long(target_path, human_readable), ""
                else:
                    return 0, str(target_path.name), ""
            
            # List directory contents
            entries = []
            for item in target_path.iterdir():
                if not show_all and item.name.startswith('.'):
                    continue
                entries.append(item)
            
            entries.sort(key=lambda x: x.name.lower())
            
            if long_format:
                output_lines = []
                for entry in entries:
                    output_lines.append(self._format_file_long(entry, human_readable))
                return 0, "\n".join(output_lines), ""
            else:
                # Simple format
                names = [entry.name for entry in entries]
                return 0, "  ".join(names), ""
                
        except PermissionError:
            return 1, "", f"ls: cannot open directory '{target_path}': Permission denied"
        except Exception as e:
            return 1, "", f"ls: error: {str(e)}"
    
    def _format_file_long(self, path: Path, human_readable: bool) -> str:
        """Format file information in long format."""
        try:
            stat_info = path.stat()
            
            # File type and permissions
            mode = stat_info.st_mode
            if stat.S_ISDIR(mode):
                file_type = 'd'
            elif stat.S_ISLNK(mode):
                file_type = 'l'
            else:
                file_type = '-'
            
            # Permissions
            perms = ''
            for who in "USR", "GRP", "OTH":
                for what in "R", "W", "X":
                    if mode & getattr(stat, f"S_I{what}{who}"):
                        perms += what.lower()
                    else:
                        perms += '-'
            
            # File size
            size = stat_info.st_size
            if human_readable:
                size_str = self._human_readable_size(size)
            else:
                size_str = str(size)
            
            # Modification time
            mtime = datetime.fromtimestamp(stat_info.st_mtime)
            time_str = mtime.strftime("%b %d %H:%M")
            
            return f"{file_type}{perms} {stat_info.st_nlink:3d} {size_str:>8} {time_str} {path.name}"
            
        except Exception:
            return f"?????????? ? ? ? {path.name}"
    
    def _human_readable_size(self, size: int) -> str:
        """Convert size to human readable format."""
        for unit in ['B', 'K', 'M', 'G', 'T']:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}P"
    
    def cd(self, args: List[str]) -> Tuple[int, str, str]:
        """Change directory."""
        if not args:
            # No arguments, go to home directory
            target = self.terminal.home_directory
        else:
            target = self._resolve_path(args[0])
        
        try:
            if not target.exists():
                return 1, "", f"cd: no such file or directory: {target}"
            
            if not target.is_dir():
                return 1, "", f"cd: not a directory: {target}"
            
            # Change directory
            os.chdir(target)
            self.terminal.current_directory = target.resolve()
            
            return 0, "", ""
            
        except PermissionError:
            return 1, "", f"cd: permission denied: {target}"
        except Exception as e:
            return 1, "", f"cd: {str(e)}"
    
    def pwd(self, args: List[str]) -> Tuple[int, str, str]:
        """Print working directory."""
        return 0, str(self.terminal.current_directory), ""
    
    def mkdir(self, args: List[str]) -> Tuple[int, str, str]:
        """Create directories."""
        if not args:
            return 1, "", "mkdir: missing operand"
        
        parents = False
        directories = []
        
        for arg in args:
            if arg.startswith('-'):
                if 'p' in arg:
                    parents = True
            else:
                directories.append(arg)
        
        if not directories:
            return 1, "", "mkdir: missing operand"
        
        errors = []
        for dir_name in directories:
            target = self._resolve_path(dir_name)
            try:
                if parents:
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.mkdir()
            except FileExistsError:
                errors.append(f"mkdir: cannot create directory '{dir_name}': File exists")
            except PermissionError:
                errors.append(f"mkdir: cannot create directory '{dir_name}': Permission denied")
            except Exception as e:
                errors.append(f"mkdir: cannot create directory '{dir_name}': {str(e)}")
        
        if errors:
            return 1, "", "\n".join(errors)
        return 0, "", ""
    
    def rmdir(self, args: List[str]) -> Tuple[int, str, str]:
        """Remove empty directories."""
        if not args:
            return 1, "", "rmdir: missing operand"
        
        errors = []
        for dir_name in args:
            target = self._resolve_path(dir_name)
            try:
                target.rmdir()
            except FileNotFoundError:
                errors.append(f"rmdir: failed to remove '{dir_name}': No such file or directory")
            except OSError as e:
                if e.errno == 39:  # Directory not empty
                    errors.append(f"rmdir: failed to remove '{dir_name}': Directory not empty")
                else:
                    errors.append(f"rmdir: failed to remove '{dir_name}': {str(e)}")
            except Exception as e:
                errors.append(f"rmdir: failed to remove '{dir_name}': {str(e)}")
        
        if errors:
            return 1, "", "\n".join(errors)
        return 0, "", ""
    
    def rm(self, args: List[str]) -> Tuple[int, str, str]:
        """Remove files and directories."""
        if not args:
            return 1, "", "rm: missing operand"
        
        recursive = False
        force = False
        files = []
        
        for arg in args:
            if arg.startswith('-'):
                if 'r' in arg or 'R' in arg:
                    recursive = True
                if 'f' in arg:
                    force = True
            else:
                files.append(arg)
        
        if not files:
            return 1, "", "rm: missing operand"
        
        errors = []
        for file_name in files:
            target = self._resolve_path(file_name)
            try:
                if not target.exists():
                    if not force:
                        errors.append(f"rm: cannot remove '{file_name}': No such file or directory")
                    continue
                
                if target.is_dir():
                    if not recursive:
                        errors.append(f"rm: cannot remove '{file_name}': Is a directory")
                        continue
                    shutil.rmtree(target)
                else:
                    target.unlink()
                    
            except PermissionError:
                if not force:
                    errors.append(f"rm: cannot remove '{file_name}': Permission denied")
            except Exception as e:
                if not force:
                    errors.append(f"rm: cannot remove '{file_name}': {str(e)}")
        
        if errors:
            return 1, "", "\n".join(errors)
        return 0, "", ""
    
    def cp(self, args: List[str]) -> Tuple[int, str, str]:
        """Copy files and directories."""
        if len(args) < 2:
            return 1, "", "cp: missing destination file operand"
        
        recursive = False
        sources = []
        
        for arg in args[:-1]:
            if arg.startswith('-'):
                if 'r' in arg or 'R' in arg:
                    recursive = True
            else:
                sources.append(arg)
        
        destination = args[-1]
        dest_path = self._resolve_path(destination)
        
        if not sources:
            return 1, "", "cp: missing source file operand"
        
        errors = []
        for source in sources:
            src_path = self._resolve_path(source)
            
            try:
                if not src_path.exists():
                    errors.append(f"cp: cannot stat '{source}': No such file or directory")
                    continue
                
                # Determine final destination
                if dest_path.is_dir():
                    final_dest = dest_path / src_path.name
                else:
                    final_dest = dest_path
                
                if src_path.is_dir():
                    if not recursive:
                        errors.append(f"cp: -r not specified; omitting directory '{source}'")
                        continue
                    shutil.copytree(src_path, final_dest, dirs_exist_ok=True)
                else:
                    shutil.copy2(src_path, final_dest)
                    
            except Exception as e:
                errors.append(f"cp: cannot copy '{source}': {str(e)}")
        
        if errors:
            return 1, "", "\n".join(errors)
        return 0, "", ""
    
    def mv(self, args: List[str]) -> Tuple[int, str, str]:
        """Move/rename files and directories."""
        if len(args) < 2:
            return 1, "", "mv: missing destination file operand"
        
        source = args[0]
        destination = args[1]
        
        src_path = self._resolve_path(source)
        dest_path = self._resolve_path(destination)
        
        try:
            if not src_path.exists():
                return 1, "", f"mv: cannot stat '{source}': No such file or directory"
            
            # If destination is a directory, move into it
            if dest_path.is_dir():
                dest_path = dest_path / src_path.name
            
            src_path.rename(dest_path)
            return 0, "", ""
            
        except Exception as e:
            return 1, "", f"mv: cannot move '{source}': {str(e)}"
    
    def touch(self, args: List[str]) -> Tuple[int, str, str]:
        """Create empty files or update timestamps."""
        if not args:
            return 1, "", "touch: missing file operand"
        
        errors = []
        for file_name in args:
            target = self._resolve_path(file_name)
            try:
                target.touch()
            except Exception as e:
                errors.append(f"touch: cannot touch '{file_name}': {str(e)}")
        
        if errors:
            return 1, "", "\n".join(errors)
        return 0, "", ""
    
    def cat(self, args: List[str]) -> Tuple[int, str, str]:
        """Display file contents."""
        if not args:
            return 1, "", "cat: missing file operand"
        
        output = []
        errors = []
        
        for file_name in args:
            target = self._resolve_path(file_name)
            try:
                if target.is_dir():
                    errors.append(f"cat: {file_name}: Is a directory")
                    continue
                
                with open(target, 'r', encoding='utf-8', errors='replace') as f:
                    output.append(f.read())
                    
            except FileNotFoundError:
                errors.append(f"cat: {file_name}: No such file or directory")
            except PermissionError:
                errors.append(f"cat: {file_name}: Permission denied")
            except Exception as e:
                errors.append(f"cat: {file_name}: {str(e)}")
        
        result_output = "".join(output) if output else ""
        result_error = "\n".join(errors) if errors else ""
        return_code = 1 if errors and not output else 0
        
        return return_code, result_output, result_error
    
    def head(self, args: List[str]) -> Tuple[int, str, str]:
        """Display first lines of files."""
        lines = 10  # Default number of lines
        files = []
        
        i = 0
        while i < len(args):
            arg = args[i]
            if arg == '-n' and i + 1 < len(args):
                try:
                    lines = int(args[i + 1])
                    i += 2
                except ValueError:
                    return 1, "", f"head: invalid number of lines: '{args[i + 1]}'"
            elif arg.startswith('-n'):
                try:
                    lines = int(arg[2:])
                    i += 1
                except ValueError:
                    return 1, "", f"head: invalid number of lines: '{arg[2:]}'"
            else:
                files.append(arg)
                i += 1
        
        if not files:
            return 1, "", "head: missing file operand"
        
        output = []
        errors = []
        
        for file_name in files:
            target = self._resolve_path(file_name)
            try:
                if target.is_dir():
                    errors.append(f"head: {file_name}: Is a directory")
                    continue
                
                with open(target, 'r', encoding='utf-8', errors='replace') as f:
                    file_lines = []
                    for _ in range(lines):
                        line = f.readline()
                        if not line:
                            break
                        file_lines.append(line.rstrip('\n'))
                    
                    if len(files) > 1:
                        output.append(f"==> {file_name} <==")
                    output.extend(file_lines)
                    
            except FileNotFoundError:
                errors.append(f"head: {file_name}: No such file or directory")
            except PermissionError:
                errors.append(f"head: {file_name}: Permission denied")
            except Exception as e:
                errors.append(f"head: {file_name}: {str(e)}")
        
        result_output = "\n".join(output) if output else ""
        result_error = "\n".join(errors) if errors else ""
        return_code = 1 if errors and not output else 0
        
        return return_code, result_output, result_error
    
    def tail(self, args: List[str]) -> Tuple[int, str, str]:
        """Display last lines of files."""
        lines = 10  # Default number of lines
        files = []
        
        i = 0
        while i < len(args):
            arg = args[i]
            if arg == '-n' and i + 1 < len(args):
                try:
                    lines = int(args[i + 1])
                    i += 2
                except ValueError:
                    return 1, "", f"tail: invalid number of lines: '{args[i + 1]}'"
            elif arg.startswith('-n'):
                try:
                    lines = int(arg[2:])
                    i += 1
                except ValueError:
                    return 1, "", f"tail: invalid number of lines: '{arg[2:]}'"
            else:
                files.append(arg)
                i += 1
        
        if not files:
            return 1, "", "tail: missing file operand"
        
        output = []
        errors = []
        
        for file_name in files:
            target = self._resolve_path(file_name)
            try:
                if target.is_dir():
                    errors.append(f"tail: {file_name}: Is a directory")
                    continue
                
                with open(target, 'r', encoding='utf-8', errors='replace') as f:
                    file_lines = f.readlines()
                    last_lines = file_lines[-lines:] if len(file_lines) > lines else file_lines
                    
                    if len(files) > 1:
                        output.append(f"==> {file_name} <==")
                    output.extend(line.rstrip('\n') for line in last_lines)
                    
            except FileNotFoundError:
                errors.append(f"tail: {file_name}: No such file or directory")
            except PermissionError:
                errors.append(f"tail: {file_name}: Permission denied")
            except Exception as e:
                errors.append(f"tail: {file_name}: {str(e)}")
        
        result_output = "\n".join(output) if output else ""
        result_error = "\n".join(errors) if errors else ""
        return_code = 1 if errors and not output else 0
        
        return return_code, result_output, result_error
    
    def find(self, args: List[str]) -> Tuple[int, str, str]:
        """Find files and directories."""
        if not args:
            search_path = self.terminal.current_directory
            pattern = "*"
        elif len(args) == 1:
            if args[0].startswith('/') or args[0].startswith('.'):
                search_path = self._resolve_path(args[0])
                pattern = "*"
            else:
                search_path = self.terminal.current_directory
                pattern = args[0]
        else:
            search_path = self._resolve_path(args[0])
            pattern = args[1]
        
        try:
            matches = []
            for root, dirs, files in os.walk(search_path):
                root_path = Path(root)
                
                # Check directories
                for d in dirs:
                    if fnmatch.fnmatch(d, pattern):
                        matches.append(str(root_path / d))
                
                # Check files
                for f in files:
                    if fnmatch.fnmatch(f, pattern):
                        matches.append(str(root_path / f))
            
            return 0, "\n".join(sorted(matches)), ""
            
        except Exception as e:
            return 1, "", f"find: {str(e)}"
    
    def grep(self, args: List[str]) -> Tuple[int, str, str]:
        """Search for patterns in files."""
        if not args:
            return 1, "", "grep: missing pattern"
        
        pattern = args[0]
        files = args[1:] if len(args) > 1 else ['-']  # stdin if no files
        
        case_insensitive = False
        line_numbers = False
        
        # Parse options (simplified)
        actual_files = []
        for arg in files:
            if arg.startswith('-'):
                if 'i' in arg:
                    case_insensitive = True
                if 'n' in arg:
                    line_numbers = True
            else:
                actual_files.append(arg)
        
        if not actual_files:
            return 1, "", "grep: no files specified"
        
        try:
            flags = re.IGNORECASE if case_insensitive else 0
            regex = re.compile(pattern, flags)
            
            output = []
            found_match = False
            
            for file_name in actual_files:
                target = self._resolve_path(file_name)
                
                try:
                    with open(target, 'r', encoding='utf-8', errors='replace') as f:
                        for line_num, line in enumerate(f, 1):
                            if regex.search(line):
                                found_match = True
                                line = line.rstrip('\n')
                                
                                if len(actual_files) > 1:
                                    prefix = f"{file_name}:"
                                else:
                                    prefix = ""
                                
                                if line_numbers:
                                    prefix += f"{line_num}:"
                                
                                output.append(f"{prefix}{line}")
                                
                except FileNotFoundError:
                    return 1, "", f"grep: {file_name}: No such file or directory"
                except PermissionError:
                    return 1, "", f"grep: {file_name}: Permission denied"
            
            return_code = 0 if found_match else 1
            return return_code, "\n".join(output), ""
            
        except re.error as e:
            return 1, "", f"grep: invalid pattern: {str(e)}"
        except Exception as e:
            return 1, "", f"grep: {str(e)}"
    
    def _resolve_path(self, path_str: str) -> Path:
        """Resolve a path string to an absolute Path object."""
        path = Path(path_str)
        
        if path.is_absolute():
            return path
        else:
            return self.terminal.current_directory / path
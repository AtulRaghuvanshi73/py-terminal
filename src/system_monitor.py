import psutil
import platform
import time
from typing import List, Tuple
from datetime import datetime


class SystemMonitor:
    """
    System monitoring utilities for CPU, memory, disk, and process monitoring.
    """
    
    def __init__(self):
        pass
    
    def top(self, args: List[str]) -> Tuple[int, str, str]:
        """Show top processes (simplified version)."""
        try:
            # System information
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            output = []
            
            # Header with system stats
            current_time = datetime.now().strftime("%H:%M:%S")
            uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
            uptime_str = f"{uptime.days} days, {uptime.seconds // 3600}:{(uptime.seconds % 3600) // 60:02d}"
            
            output.append(f"top - {current_time} up {uptime_str}")
            output.append(f"CPU: {cpu_percent:.1f}%")
            output.append(f"Mem: {memory.used // (1024**3):.1f}G used, {memory.available // (1024**3):.1f}G avail, {memory.total // (1024**3):.1f}G total")
            output.append(f"Swap: {swap.used // (1024**3):.1f}G used, {swap.free // (1024**3):.1f}G free, {swap.total // (1024**3):.1f}G total")
            output.append("")
            
            # Process header
            output.append(f"{'PID':>7} {'USER':<10} {'CPU%':>5} {'MEM%':>5} {'VSZ':>8} {'RSS':>8} {'COMMAND'}")
            
            # Get processes sorted by CPU usage
            processes = []
            for proc in psutil.process_iter(['pid', 'username', 'cpu_percent', 'memory_percent', 'name', 'memory_info']):
                try:
                    pinfo = proc.info
                    if pinfo['cpu_percent'] is not None:
                        processes.append(pinfo)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
            
            # Show top 20 processes
            for pinfo in processes[:20]:
                pid = pinfo['pid']
                username = (pinfo['username'] or 'unknown')[:10]
                cpu_percent = pinfo['cpu_percent'] or 0
                memory_percent = pinfo['memory_percent'] or 0
                name = pinfo['name'] or 'unknown'
                
                # Memory info
                try:
                    mem_info = pinfo['memory_info']
                    vms = mem_info.vms // 1024 if mem_info else 0
                    rss = mem_info.rss // 1024 if mem_info else 0
                except:
                    vms = rss = 0
                
                process_line = f"{pid:>7} {username:<10} {cpu_percent:>4.1f} {memory_percent:>4.1f} {vms:>8} {rss:>8} {name}"
                output.append(process_line)
            
            return 0, "\n".join(output), ""
            
        except Exception as e:
            return 1, "", f"top: error: {str(e)}"
    
    def htop(self, args: List[str]) -> Tuple[int, str, str]:
        """Enhanced process viewer (simplified)."""
        # For now, just call top
        return self.top(args)
    
    def free(self, args: List[str]) -> Tuple[int, str, str]:
        """Display memory usage."""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            human_readable = '-h' in args
            
            output = []
            
            if human_readable:
                # Human readable format
                def format_bytes(bytes_val):
                    for unit in ['B', 'K', 'M', 'G', 'T']:
                        if bytes_val < 1024:
                            return f"{bytes_val:.1f}{unit}"
                        bytes_val /= 1024
                    return f"{bytes_val:.1f}P"
                
                output.append(f"{'':>15} {'total':>8} {'used':>8} {'free':>8} {'shared':>8} {'buff/cache':>10} {'available':>10}")
                
                mem_line = (f"{'Mem:':>15} {format_bytes(memory.total):>8} {format_bytes(memory.used):>8} "
                          f"{format_bytes(memory.free):>8} {format_bytes(getattr(memory, 'shared', 0)):>8} "
                          f"{format_bytes(getattr(memory, 'buffers', 0) + getattr(memory, 'cached', 0)):>10} "
                          f"{format_bytes(memory.available):>10}")
                
                swap_line = (f"{'Swap:':>15} {format_bytes(swap.total):>8} {format_bytes(swap.used):>8} "
                           f"{format_bytes(swap.free):>8} {'0B':>8} {'0B':>10} {'0B':>10}")
                
            else:
                # Default format (KB)
                output.append(f"{'':>15} {'total':>10} {'used':>10} {'free':>10} {'shared':>10} {'buff/cache':>12} {'available':>12}")
                
                mem_line = (f"{'Mem:':>15} {memory.total // 1024:>10} {memory.used // 1024:>10} "
                          f"{memory.free // 1024:>10} {getattr(memory, 'shared', 0) // 1024:>10} "
                          f"{(getattr(memory, 'buffers', 0) + getattr(memory, 'cached', 0)) // 1024:>12} "
                          f"{memory.available // 1024:>12}")
                
                swap_line = (f"{'Swap:':>15} {swap.total // 1024:>10} {swap.used // 1024:>10} "
                           f"{swap.free // 1024:>10} {0:>10} {0:>12} {0:>12}")
            
            output.append(mem_line)
            output.append(swap_line)
            
            return 0, "\n".join(output), ""
            
        except Exception as e:
            return 1, "", f"free: error: {str(e)}"
    
    def df(self, args: List[str]) -> Tuple[int, str, str]:
        """Display filesystem disk space usage."""
        try:
            human_readable = '-h' in args
            
            def format_bytes(bytes_val):
                if human_readable:
                    for unit in ['B', 'K', 'M', 'G', 'T']:
                        if bytes_val < 1024:
                            return f"{bytes_val:.1f}{unit}"
                        bytes_val /= 1024
                    return f"{bytes_val:.1f}P"
                else:
                    return str(bytes_val // 1024)  # KB
            
            output = []
            
            if human_readable:
                output.append(f"{'Filesystem':<20} {'Size':>6} {'Used':>6} {'Avail':>6} {'Use%':>5} {'Mounted on'}")
            else:
                output.append(f"{'Filesystem':<20} {'1K-blocks':>10} {'Used':>10} {'Available':>10} {'Use%':>5} {'Mounted on'}")
            
            # Get disk partitions
            partitions = psutil.disk_partitions()
            
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    
                    filesystem = partition.device[:19] if len(partition.device) > 19 else partition.device
                    size = format_bytes(usage.total)
                    used = format_bytes(usage.used)
                    available = format_bytes(usage.free)
                    use_percent = f"{(usage.used / usage.total * 100):.0f}%" if usage.total > 0 else "0%"
                    mountpoint = partition.mountpoint
                    
                    if human_readable:
                        line = f"{filesystem:<20} {size:>6} {used:>6} {available:>6} {use_percent:>5} {mountpoint}"
                    else:
                        line = f"{filesystem:<20} {size:>10} {used:>10} {available:>10} {use_percent:>5} {mountpoint}"
                    
                    output.append(line)
                    
                except PermissionError:
                    continue
                except Exception:
                    continue
            
            return 0, "\n".join(output), ""
            
        except Exception as e:
            return 1, "", f"df: error: {str(e)}"
    
    def du(self, args: List[str]) -> Tuple[int, str, str]:
        """Display directory disk usage."""
        try:
            import os
            from pathlib import Path
            
            # Parse arguments
            path = "." if not args or args[0].startswith('-') else args[0]
            human_readable = '-h' in args
            summarize = '-s' in args
            
            def get_dir_size(dir_path):
                """Calculate total size of directory."""
                total_size = 0
                try:
                    for dirpath, dirnames, filenames in os.walk(dir_path):
                        for filename in filenames:
                            try:
                                file_path = os.path.join(dirpath, filename)
                                total_size += os.path.getsize(file_path)
                            except (OSError, IOError):
                                continue
                except (OSError, IOError):
                    pass
                return total_size
            
            def format_size(size):
                if human_readable:
                    for unit in ['B', 'K', 'M', 'G', 'T']:
                        if size < 1024:
                            return f"{size:.1f}{unit}"
                        size /= 1024
                    return f"{size:.1f}P"
                else:
                    return str(size // 1024)  # KB
            
            target_path = Path(path).resolve()
            
            if not target_path.exists():
                return 1, "", f"du: cannot access '{path}': No such file or directory"
            
            output = []
            
            if target_path.is_file():
                size = target_path.stat().st_size
                output.append(f"{format_size(size)}\t{path}")
            else:
                if summarize:
                    # Just show total for the directory
                    total_size = get_dir_size(target_path)
                    output.append(f"{format_size(total_size)}\t{path}")
                else:
                    # Show size for each subdirectory
                    try:
                        for item in target_path.iterdir():
                            if item.is_dir():
                                dir_size = get_dir_size(item)
                                output.append(f"{format_size(dir_size)}\t{item}")
                            else:
                                file_size = item.stat().st_size
                                output.append(f"{format_size(file_size)}\t{item}")
                    except PermissionError:
                        return 1, "", f"du: cannot access '{path}': Permission denied"
            
            return 0, "\n".join(output), ""
            
        except Exception as e:
            return 1, "", f"du: error: {str(e)}"
    
    def lscpu(self, args: List[str]) -> Tuple[int, str, str]:
        """Display CPU information."""
        try:
            output = []
            
            # Basic CPU info
            output.append(f"Architecture: {platform.machine()}")
            output.append(f"CPU(s): {psutil.cpu_count()}")
            output.append(f"Thread(s) per core: {psutil.cpu_count() // psutil.cpu_count(logical=False) if psutil.cpu_count(logical=False) else 1}")
            output.append(f"Core(s) per socket: {psutil.cpu_count(logical=False) or 'Unknown'}")
            
            # CPU frequencies
            try:
                cpu_freq = psutil.cpu_freq()
                if cpu_freq:
                    output.append(f"CPU max MHz: {cpu_freq.max:.0f}")
                    output.append(f"CPU min MHz: {cpu_freq.min:.0f}")
                    output.append(f"CPU current MHz: {cpu_freq.current:.0f}")
            except:
                pass
            
            # Platform info
            output.append(f"Model name: {platform.processor()}")
            output.append(f"System: {platform.system()}")
            output.append(f"Release: {platform.release()}")
            
            # CPU usage per core
            cpu_percents = psutil.cpu_percent(interval=1, percpu=True)
            for i, percent in enumerate(cpu_percents):
                output.append(f"CPU {i}: {percent:.1f}%")
            
            return 0, "\n".join(output), ""
            
        except Exception as e:
            return 1, "", f"lscpu: error: {str(e)}"
    
    def lsblk(self, args: List[str]) -> Tuple[int, str, str]:
        """List block devices."""
        try:
            output = []
            
            output.append(f"{'NAME':<20} {'SIZE':>8} {'TYPE':<8} {'MOUNTPOINT'}")
            
            partitions = psutil.disk_partitions()
            devices = {}
            
            # Group partitions by device
            for partition in partitions:
                device_name = partition.device
                
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    size = usage.total
                    
                    # Format size
                    size_str = self._format_bytes_simple(size)
                    
                    fstype = partition.fstype or 'unknown'
                    mountpoint = partition.mountpoint
                    
                    # Determine device type
                    if 'cdrom' in device_name.lower() or 'dvd' in device_name.lower():
                        dev_type = 'rom'
                    elif 'loop' in device_name.lower():
                        dev_type = 'loop'
                    else:
                        dev_type = 'disk'
                    
                    line = f"{device_name:<20} {size_str:>8} {dev_type:<8} {mountpoint}"
                    output.append(line)
                    
                except (PermissionError, OSError):
                    continue
            
            return 0, "\n".join(output), ""
            
        except Exception as e:
            return 1, "", f"lsblk: error: {str(e)}"
    
    def _format_bytes_simple(self, bytes_val):
        """Simple byte formatter for lsblk."""
        for unit in ['B', 'K', 'M', 'G', 'T']:
            if bytes_val < 1024:
                return f"{bytes_val:.1f}{unit}"
            bytes_val /= 1024
        return f"{bytes_val:.1f}P"
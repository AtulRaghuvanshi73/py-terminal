# PyTerminal

A Python terminal emulator that behaves like a standard system shell, with support for file operations, system monitoring, and optional natural-language command interpretation.

## Overview

PyTerminal is a command-line terminal written entirely in Python. It provides a familiar set of shell commands for file and directory management, process and resource monitoring, environment variables, and command aliases. It runs on Windows, Linux, and macOS, and can execute external system commands in addition to its built-in set.

The terminal also accepts plain-English instructions. When a Google Gemini API key is configured, requests are interpreted by the model; otherwise the terminal falls back to built-in pattern matching.

## Features

- File operations: `ls`, `cd`, `pwd`, `mkdir`, `rm`, `cp`, `mv`, `touch`, `cat`, `head`, `tail`, `find`, `grep`
- System monitoring for CPU, memory, disk, and processes (`free`, `df`, `ps`, `top`, `lscpu`)
- Natural-language command interpretation via Gemini, with a pattern-matching fallback
- Command history and recall
- Tab completion for command names and file paths
- Colorized output
- Environment-variable management and user-defined aliases
- Execution of external system commands
- Cross-platform support for Windows, Linux, and macOS

## Installation

```bash
git clone <repository-url>
cd python-terminal
pip install -r requirements.txt
python run_terminal.py
```

Individual commands can also be passed directly to the launcher:

```bash
python run_terminal.py "ls -la"
python run_terminal.py "create a file called test.txt"
```

## Natural-language commands

In addition to standard syntax, PyTerminal accepts instructions written in plain English and maps them to the corresponding command:

| Instruction | Equivalent command |
| --- | --- |
| "create a new file called example.txt" | `touch example.txt` |
| "show me all files" | `ls -la` |
| "where am I" | `pwd` |
| "show system memory usage" | `free -h` |
| "create a folder called documents and move file.txt into it" | `mkdir documents && mv file.txt documents/` |

### Enabling Gemini

Natural-language interpretation uses Google's Gemini model when an API key is available:

1. Obtain an API key from Google AI Studio.
2. Set it as an environment variable:

   ```bash
   export GEMINI_API_KEY=your_key_here
   ```

If no key is set, natural-language input is interpreted using built-in pattern matching instead.

## Usage examples

### Standard commands

```bash
PyTerminal> pwd
/home/user/projects

PyTerminal> ls -la
-rw-r--r-- 1 user user 1024 Jan 01 12:00 file.txt
drwxr-xr-x 2 user user 4096 Jan 01 12:00 documents

PyTerminal> cd documents
PyTerminal> mkdir new_project
PyTerminal> touch README.md
```

### Natural-language commands

```bash
PyTerminal> show me all files
Interpreted as: ls -la

PyTerminal> create a folder called backup
Interpreted as: mkdir backup

PyTerminal> copy file.txt to backup folder
Interpreted as: cp file.txt backup/
```

### System monitoring

```bash
PyTerminal> free -h     # Memory usage
PyTerminal> df -h       # Disk usage
PyTerminal> ps -af      # Running processes
PyTerminal> top         # System overview
PyTerminal> lscpu       # CPU information
```

## Project structure

```
python-terminal/
├── src/
│   ├── terminal_engine.py      # Core command processor
│   ├── main.py                 # Interactive CLI interface
│   ├── ai_interpreter.py       # Natural-language interpretation
│   ├── system_monitor.py       # System monitoring utilities
│   └── commands/
│       ├── file_operations.py  # File and directory commands
│       └── system_commands.py  # Process and environment commands
├── tests/                      # Test suite
├── docs/                       # Documentation
├── requirements.txt            # Python dependencies
├── run_terminal.py             # Launcher script
├── demo.py                     # Feature demonstration
└── README.md
```

### Components

- `TerminalEngine` — processes built-in and external commands
- `FileOperations` — file and directory manipulation
- `SystemCommands` — process management, environment variables, and aliases
- `SystemMonitor` — resource usage and system information
- `AICommandInterpreter` — translates natural language into commands
- `PyTerminalInterface` — interactive interface with completion and history

## Requirements

Python 3.7 or later. Dependencies are listed in `requirements.txt`.

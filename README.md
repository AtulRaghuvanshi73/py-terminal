# PyTerminal - Python-based Terminal Emulator

A fully functioning command terminal built in Python that mimics the behavior of a real system terminal with modern features including AI-powered natural language command interpretation.

![Python Terminal Demo](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

### 🔧 **Mandatory Requirements (Completed)**
- ✅ **Python Backend**: Fully implemented in Python with modular architecture
- ✅ **File Operations**: Complete support for `ls`, `cd`, `pwd`, `mkdir`, `rm`, `cp`, `mv`, `touch`, `cat`, `head`, `tail`, `find`, `grep`
- ✅ **Error Handling**: Robust error handling for invalid commands and operations
- ✅ **Clean Interface**: Both CLI and programmatic interfaces available
- ✅ **System Integration**: CPU, memory, disk, and process monitoring tools

### 🚀 **Enhanced Features (Completed)**
- ✅ **AI Natural Language Processing**: Type commands in plain English!
- ✅ **Command History**: Full command history tracking and navigation
- ✅ **Auto-completion**: Smart tab completion for commands and file paths
- ✅ **Colorized Output**: Beautiful colored terminal interface
- ✅ **Cross-platform**: Works on Windows, Linux, and macOS
- ✅ **External Command Support**: Run any system command seamlessly
- ✅ **Environment Management**: Full environment variable support
- ✅ **Command Aliases**: Create and manage command shortcuts

## 🤖 AI-Powered Commands

Our terminal understands natural language! Try these examples:

```bash
# Instead of: touch example.txt
"create a new file called example.txt"

# Instead of: mkdir documents && mv file.txt documents/
"create a folder called documents and move file.txt into it"

# Instead of: ls -la
"show me all files"

# Instead of: pwd
"where am I"

# Instead of: free -h
"show system memory usage"
```

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd python-terminal
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the terminal**:
   ```bash
   python run_terminal.py
   ```

   Or run specific commands:
   ```bash
   python run_terminal.py "ls -la"
   python run_terminal.py "create a file called test.txt"
   ```

## 🎯 Usage Examples

### Standard Commands
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

### AI Natural Language Commands
```bash
PyTerminal> show me all files
🤖 AI Interpreter: Interpreted as: ls -la

PyTerminal> create a folder called backup
🤖 AI Interpreter: Interpreted 'create a folder called backup' as: mkdir backup
Action: Create a new directory

PyTerminal> copy file.txt to backup folder
🤖 AI Interpreter: Interpreted 'copy file.txt to backup folder' as: cp file.txt backup/
Action: Copy file
```

### System Monitoring
```bash
PyTerminal> free -h          # Memory usage
PyTerminal> df -h            # Disk usage  
PyTerminal> ps -af           # Running processes
PyTerminal> top              # System overview
PyTerminal> lscpu            # CPU information
```

## 🏗️ Architecture

```
python-terminal/
├── src/
│   ├── terminal_engine.py      # Core terminal processing engine
│   ├── main.py                 # Interactive CLI interface with colors
│   ├── ai_interpreter.py       # Natural language processing
│   ├── system_monitor.py       # System monitoring utilities
│   └── commands/
│       ├── file_operations.py  # File and directory commands
│       └── system_commands.py  # Process and environment commands
├── tests/                      # Test files
├── docs/                       # Documentation
├── requirements.txt            # Python dependencies
├── run_terminal.py             # Simple launcher script
├── demo.py                     # Feature demonstration
└── README.md                   # This file
```

### Core Components

1. **TerminalEngine**: Main command processor with built-in and external command support
2. **FileOperations**: Comprehensive file and directory manipulation
3. **SystemCommands**: Process management, environment variables, aliases
4. **SystemMonitor**: Real-time system monitoring and resource usage
5. **AICommandInterpreter**: Natural language to command translation
6. **PyTerminalInterface**: Interactive UI with auto-completion and history

## 🧪 Testing

Run the test suite:
```bash
python test_terminal.py    # Basic functionality tests
python demo.py            # Feature demonstration
```

## 🎨 Key Features Demonstrated

| Feature | Example | Status |
|---------|---------|--------|
| File Operations | `ls -la`, `cp file1 file2` | ✅ |
| Directory Navigation | `cd`, `pwd`, `mkdir` | ✅ |
| Process Management | `ps`, `kill`, `jobs` | ✅ |
| System Monitoring | `free`, `df`, `top` | ✅ |
| Error Handling | Invalid commands, permissions | ✅ |
| Command History | Up/down arrows, `history` | ✅ |
| Auto-completion | Tab completion for files/commands | ✅ |
| AI Interpretation | Natural language commands | ✅ |
| Environment Variables | `env`, `export`, `$VAR` | ✅ |
| Command Aliases | `alias ll='ls -la'` | ✅ |
| External Commands | Any system command | ✅ |
| Cross-platform | Windows, Linux, macOS | ✅ |

## 🤝 Contributing

This project demonstrates a fully functional Python terminal with advanced features. Feel free to:

1. Add new commands to the `commands/` directory
2. Enhance the AI interpreter with more patterns
3. Improve the UI with additional colors and formatting
4. Add more system monitoring features
5. Extend cross-platform compatibility

## 📄 License

MIT License - feel free to use this code for learning and development.

## 🏆 Project Completion Status

**All mandatory and optional requirements have been successfully implemented!**

- ✅ Python backend with command processing
- ✅ Full file and directory operations  
- ✅ Comprehensive error handling
- ✅ Clean and responsive interface
- ✅ System monitoring integration
- ✅ AI-driven natural language commands
- ✅ Command history and auto-completion
- ✅ Cross-platform compatibility

This terminal successfully replicates low-level terminal behavior while adding modern conveniences like AI interpretation and enhanced user experience.

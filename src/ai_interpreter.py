import re
import json
from typing import List, Tuple, Optional, Dict, Any


class AICommandInterpreter:
    """
    AI-driven command interpreter that converts natural language queries
    into terminal commands.
    
    Note: This is a simplified implementation using pattern matching.
    In a production environment, you would integrate with a proper NLP
    service like OpenAI GPT, Google's Language API, or train a custom model.
    """
    
    def __init__(self):
        # Define patterns for natural language to command mapping
        self.patterns = self._initialize_patterns()
        
    def _initialize_patterns(self) -> List[Dict[str, Any]]:
        """Initialize natural language patterns and their corresponding commands."""
        return [
            # File creation patterns
            {
                'patterns': [
                    r'create (?:a )?(?:new )?file (?:called |named )?["\']?([^"\']+)["\']?',
                    r'make (?:a )?(?:new )?file ["\']?([^"\']+)["\']?',
                    r'touch (?:a )?(?:file )?["\']?([^"\']+)["\']?',
                ],
                'command_template': 'touch {0}',
                'description': 'Create a new file'
            },
            
            # Directory creation patterns
            {
                'patterns': [
                    r'create (?:a )?(?:new )?(?:directory|folder|dir) (?:called |named )?["\']?([^"\']+)["\']?',
                    r'make (?:a )?(?:new )?(?:directory|folder|dir) ["\']?([^"\']+)["\']?',
                    r'mkdir ["\']?([^"\']+)["\']?',
                ],
                'command_template': 'mkdir {0}',
                'description': 'Create a new directory'
            },
            
            # File listing patterns
            {
                'patterns': [
                    r'(?:list|show|display) (?:the )?(?:files|contents) (?:in |of )?(?:this )?(?:directory|folder)?',
                    r'(?:what|which) files are (?:in |here|there)',
                    r'show me (?:the )?(?:files|contents)',
                    r'list (?:all )?(?:files|everything)',
                ],
                'command_template': 'ls -la',
                'description': 'List directory contents'
            },
            
            # Directory navigation patterns
            {
                'patterns': [
                    r'(?:go to|navigate to|change to|cd to) (?:the )?(?:directory|folder) ["\']?([^"\']+)["\']?',
                    r'(?:enter|open) (?:the )?(?:directory|folder) ["\']?([^"\']+)["\']?',
                    r'cd ["\']?([^"\']+)["\']?',
                ],
                'command_template': 'cd {0}',
                'description': 'Change directory'
            },
            
            # File copying patterns
            {
                'patterns': [
                    r'copy (?:the )?file ["\']?([^"\']+)["\']? to ["\']?([^"\']+)["\']?',
                    r'duplicate ["\']?([^"\']+)["\']? (?:as |to )["\']?([^"\']+)["\']?',
                    r'cp ["\']?([^"\']+)["\']? ["\']?([^"\']+)["\']?',
                ],
                'command_template': 'cp {0} {1}',
                'description': 'Copy file'
            },
            
            # File moving patterns
            {
                'patterns': [
                    r'move (?:the )?file ["\']?([^"\']+)["\']? to ["\']?([^"\']+)["\']?',
                    r'rename ["\']?([^"\']+)["\']? (?:as |to )["\']?([^"\']+)["\']?',
                    r'mv ["\']?([^"\']+)["\']? ["\']?([^"\']+)["\']?',
                ],
                'command_template': 'mv {0} {1}',
                'description': 'Move/rename file'
            },
            
            # File deletion patterns
            {
                'patterns': [
                    r'delete (?:the )?file ["\']?([^"\']+)["\']?',
                    r'remove (?:the )?file ["\']?([^"\']+)["\']?',
                    r'rm ["\']?([^"\']+)["\']?',
                ],
                'command_template': 'rm {0}',
                'description': 'Delete file'
            },
            
            # Directory deletion patterns
            {
                'patterns': [
                    r'delete (?:the )?(?:directory|folder) ["\']?([^"\']+)["\']?',
                    r'remove (?:the )?(?:directory|folder) ["\']?([^"\']+)["\']?',
                    r'rmdir ["\']?([^"\']+)["\']?',
                ],
                'command_template': 'rm -r {0}',
                'description': 'Delete directory'
            },
            
            # File content viewing patterns
            {
                'patterns': [
                    r'(?:show|display|view|read) (?:the )?(?:contents of |file )["\']?([^"\']+)["\']?',
                    r'cat ["\']?([^"\']+)["\']?',
                    r'what(?:\'s| is) in (?:the )?file ["\']?([^"\']+)["\']?',
                ],
                'command_template': 'cat {0}',
                'description': 'Display file contents'
            },
            
            # Process listing patterns
            {
                'patterns': [
                    r'(?:show|list|display) (?:all )?(?:running )?processes',
                    r'what processes are running',
                    r'ps aux',
                ],
                'command_template': 'ps -af',
                'description': 'List running processes'
            },
            
            # System information patterns
            {
                'patterns': [
                    r'show (?:me )?(?:system|memory) (?:info|information|usage)',
                    r'how much memory (?:am I|are we) using',
                    r'memory status',
                ],
                'command_template': 'free -h',
                'description': 'Show memory usage'
            },
            
            # Disk usage patterns
            {
                'patterns': [
                    r'(?:show|display) disk (?:usage|space)',
                    r'how much (?:disk )?space (?:do I have|is left|is available)',
                    r'df -h',
                ],
                'command_template': 'df -h',
                'description': 'Show disk usage'
            },
            
            # Current directory patterns
            {
                'patterns': [
                    r'(?:where am I|what(?:\'s| is) (?:my )?current (?:directory|location))',
                    r'(?:show|print) (?:current )?(?:directory|working directory)',
                    r'pwd',
                ],
                'command_template': 'pwd',
                'description': 'Show current directory'
            },
            
            # Complex operations patterns
            {
                'patterns': [
                    r'create (?:a )?(?:new )?(?:directory|folder) (?:called |named )?["\']?([^"\']+)["\']? and move ["\']?([^"\']+)["\']? (?:into it|there)',
                    r'make (?:a )?(?:directory|folder) ["\']?([^"\']+)["\']? and put ["\']?([^"\']+)["\']? in it',
                ],
                'command_template': 'mkdir {0} && mv {1} {0}/',
                'description': 'Create directory and move file into it'
            },
            
            # Search patterns
            {
                'patterns': [
                    r'find (?:all )?files (?:called |named |with name )?["\']?([^"\']+)["\']?',
                    r'search for (?:files )?["\']?([^"\']+)["\']?',
                    r'locate ["\']?([^"\']+)["\']?',
                ],
                'command_template': 'find . -name "*{0}*"',
                'description': 'Find files by name'
            },
            
            # Text search patterns
            {
                'patterns': [
                    r'search for ["\']?([^"\']+)["\']? in (?:file )?["\']?([^"\']+)["\']?',
                    r'find ["\']?([^"\']+)["\']? in ["\']?([^"\']+)["\']?',
                    r'grep ["\']?([^"\']+)["\']? ["\']?([^"\']+)["\']?',
                ],
                'command_template': 'grep "{0}" {1}',
                'description': 'Search for text in file'
            }
        ]
    
    def interpret(self, natural_language_query: str) -> Tuple[bool, str, str]:
        """
        Interpret a natural language query and convert it to a terminal command.
        
        Args:
            natural_language_query: The natural language input from user
            
        Returns:
            Tuple of (success, command, explanation)
        """
        query = natural_language_query.strip().lower()
        
        if not query:
            return False, "", "Empty query"
        
        # Try to match against known patterns
        for pattern_group in self.patterns:
            for pattern in pattern_group['patterns']:
                match = re.search(pattern, query, re.IGNORECASE)
                if match:
                    try:
                        # Extract captured groups
                        groups = match.groups()
                        
                        # Format the command template with captured groups
                        command = pattern_group['command_template'].format(*groups)
                        
                        explanation = (
                            f"Interpreted '{natural_language_query}' as: {command}\n"
                            f"Action: {pattern_group['description']}"
                        )
                        
                        return True, command, explanation
                        
                    except (IndexError, ValueError) as e:
                        continue
        
        # If no pattern matches, try some basic keyword detection
        fallback_command, fallback_explanation = self._fallback_interpretation(query)
        if fallback_command:
            return True, fallback_command, fallback_explanation
        
        # No interpretation found
        return False, "", f"Could not interpret: '{natural_language_query}'"
    
    def _fallback_interpretation(self, query: str) -> Tuple[str, str]:
        """
        Fallback interpretation for queries that don't match specific patterns.
        """
        # Simple keyword-based fallbacks
        keywords_commands = [
            (['help', 'commands', 'what can you do'], 'help', 'Show available commands'),
            (['list', 'show', 'files'], 'ls', 'List files in current directory'),
            (['processes', 'running'], 'ps', 'Show running processes'),
            (['memory', 'ram'], 'free', 'Show memory usage'),
            (['disk', 'space'], 'df', 'Show disk usage'),
            (['where', 'location', 'directory'], 'pwd', 'Show current directory'),
            (['clear', 'clean'], 'clear', 'Clear the terminal screen'),
        ]
        
        for keywords, command, description in keywords_commands:
            if any(keyword in query for keyword in keywords):
                return command, f"Interpreted as: {command} - {description}"
        
        return "", ""
    
    def get_suggestions(self, partial_query: str) -> List[str]:
        """
        Get suggestions for natural language queries based on partial input.
        """
        suggestions = [
            "create a new file called example.txt",
            "create a new folder called documents",
            "list all files",
            "show me the files",
            "copy file.txt to backup.txt",
            "move file.txt to documents folder",
            "delete the file temp.txt",
            "show the contents of readme.txt",
            "find files named test",
            "search for 'hello' in file.txt",
            "show system memory usage",
            "show disk usage",
            "what processes are running",
            "where am I",
            "create a folder called projects and move main.py there"
        ]
        
        if not partial_query:
            return suggestions[:5]  # Return first 5 suggestions
        
        # Filter suggestions based on partial input
        matching_suggestions = [
            suggestion for suggestion in suggestions
            if partial_query.lower() in suggestion.lower()
        ]
        
        return matching_suggestions[:10]  # Return up to 10 matching suggestions
    
    def explain_capabilities(self) -> str:
        """
        Return a description of AI interpreter capabilities.
        """
        return """
AI Command Interpreter Capabilities:

File Operations:
  • "create a new file called example.txt"
  • "make a folder named documents"
  • "copy file1.txt to file2.txt"
  • "move document.txt to archive folder"
  • "delete the file temp.txt"

Directory Operations:
  • "go to the documents folder"
  • "list all files"
  • "show me what's in this directory"
  • "create a folder and move file.txt into it"

File Content:
  • "show the contents of readme.txt"
  • "search for 'hello' in file.txt"
  • "find files named test"

System Information:
  • "show memory usage"
  • "what processes are running"
  • "show disk usage"
  • "where am I"

You can use natural language instead of remembering command syntax!
        """.strip()
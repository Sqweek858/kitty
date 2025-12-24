#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      TERMINAL SESSION MANAGER                                ║
║            Command Execution, Output Management, Shell Integration          ║
╚══════════════════════════════════════════════════════════════════════════════╝

This module handles terminal session management:
    - Command execution with real-time output
    - Output buffer with persistent display
    - Process management and job control
    - Environment variable management
    - Working directory tracking
    - Command aliases and shell functions
    - Output filtering and formatting
    - Logging and session recording
"""

import os
import sys
import subprocess
import threading
import queue
import time
import shlex
from typing import List, Dict, Optional, Callable, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import deque
import select
import fcntl
import termios
import pty


# ═══════════════════════════════════════════════════════════════════════════════
# OUTPUT LINE TYPES
# ═══════════════════════════════════════════════════════════════════════════════

class OutputType(Enum):
    """Type of output line"""
    COMMAND = auto()      # User command
    STDOUT = auto()       # Standard output
    STDERR = auto()       # Standard error
    SYSTEM = auto()       # System message
    ERROR = auto()        # Error message
    SUCCESS = auto()      # Success message
    INFO = auto()         # Information message
    WARNING = auto()      # Warning message
    PROMPT = auto()       # Command prompt


@dataclass
class OutputLine:
    """Represents a line of terminal output"""
    text: str
    output_type: OutputType
    timestamp: float
    command_id: Optional[int] = None  # Associate with command
    metadata: Dict[str, Any] = field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════════════════════
# COMMAND EXECUTION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class CommandResult:
    """Result of command execution"""
    command: str
    exit_code: int
    stdout: List[str]
    stderr: List[str]
    execution_time: float
    success: bool


class CommandExecutor:
    """Executes shell commands and captures output"""
    
    def __init__(self):
        self.running_processes: Dict[int, subprocess.Popen] = {}
        self.next_process_id = 0
        
    def execute_sync(self, command: str, cwd: Optional[str] = None,
                    env: Optional[Dict[str, str]] = None,
                    timeout: Optional[float] = None) -> CommandResult:
        """Execute command synchronously"""
        start_time = time.time()
        
        try:
            # Use shell=True to support pipes, redirects, etc.
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=cwd,
                env=env or os.environ.copy(),
                text=True
            )
            
            stdout, stderr = process.communicate(timeout=timeout)
            execution_time = time.time() - start_time
            
            stdout_lines = stdout.splitlines() if stdout else []
            stderr_lines = stderr.splitlines() if stderr else []
            
            return CommandResult(
                command=command,
                exit_code=process.returncode,
                stdout=stdout_lines,
                stderr=stderr_lines,
                execution_time=execution_time,
                success=(process.returncode == 0)
            )
        
        except subprocess.TimeoutExpired:
            process.kill()
            execution_time = time.time() - start_time
            return CommandResult(
                command=command,
                exit_code=-1,
                stdout=[],
                stderr=["Command timed out"],
                execution_time=execution_time,
                success=False
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            return CommandResult(
                command=command,
                exit_code=-1,
                stdout=[],
                stderr=[f"Error: {str(e)}"],
                execution_time=execution_time,
                success=False
            )
    
    def execute_async(self, command: str, 
                     output_callback: Callable[[str, OutputType], None],
                     completion_callback: Optional[Callable[[CommandResult], None]] = None,
                     cwd: Optional[str] = None,
                     env: Optional[Dict[str, str]] = None) -> int:
        """
        Execute command asynchronously with real-time output.
        Returns process ID.
        """
        process_id = self.next_process_id
        self.next_process_id += 1
        
        def run_command():
            start_time = time.time()
            stdout_lines = []
            stderr_lines = []
            
            try:
                process = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=cwd,
                    env=env or os.environ.copy(),
                    text=True,
                    bufsize=1  # Line buffered
                )
                
                self.running_processes[process_id] = process
                
                # Read output in real-time
                while True:
                    # Check if process is still running
                    if process.poll() is not None:
                        # Process finished, read remaining output
                        remaining_stdout = process.stdout.read()
                        remaining_stderr = process.stderr.read()
                        
                        if remaining_stdout:
                            for line in remaining_stdout.splitlines():
                                stdout_lines.append(line)
                                output_callback(line, OutputType.STDOUT)
                        
                        if remaining_stderr:
                            for line in remaining_stderr.splitlines():
                                stderr_lines.append(line)
                                output_callback(line, OutputType.STDERR)
                        
                        break
                    
                    # Read stdout
                    try:
                        line = process.stdout.readline()
                        if line:
                            line = line.rstrip('\n')
                            stdout_lines.append(line)
                            output_callback(line, OutputType.STDOUT)
                    except:
                        pass
                    
                    # Read stderr
                    try:
                        line = process.stderr.readline()
                        if line:
                            line = line.rstrip('\n')
                            stderr_lines.append(line)
                            output_callback(line, OutputType.STDERR)
                    except:
                        pass
                    
                    time.sleep(0.01)  # Small delay
                
                execution_time = time.time() - start_time
                result = CommandResult(
                    command=command,
                    exit_code=process.returncode,
                    stdout=stdout_lines,
                    stderr=stderr_lines,
                    execution_time=execution_time,
                    success=(process.returncode == 0)
                )
                
                if completion_callback:
                    completion_callback(result)
            
            except Exception as e:
                execution_time = time.time() - start_time
                error_msg = f"Error executing command: {str(e)}"
                output_callback(error_msg, OutputType.ERROR)
                
                result = CommandResult(
                    command=command,
                    exit_code=-1,
                    stdout=stdout_lines,
                    stderr=[error_msg],
                    execution_time=execution_time,
                    success=False
                )
                
                if completion_callback:
                    completion_callback(result)
            
            finally:
                if process_id in self.running_processes:
                    del self.running_processes[process_id]
        
        thread = threading.Thread(target=run_command, daemon=True)
        thread.start()
        
        return process_id
    
    def kill_process(self, process_id: int) -> bool:
        """Kill a running process"""
        if process_id in self.running_processes:
            try:
                self.running_processes[process_id].kill()
                return True
            except:
                return False
        return False
    
    def is_running(self, process_id: int) -> bool:
        """Check if process is still running"""
        return process_id in self.running_processes


# ═══════════════════════════════════════════════════════════════════════════════
# OUTPUT BUFFER
# ═══════════════════════════════════════════════════════════════════════════════

class OutputBuffer:
    """Manages terminal output with persistent display"""
    
    def __init__(self, max_lines: int = 10000):
        self.lines: deque[OutputLine] = deque(maxlen=max_lines)
        self.scroll_position = 0  # 0 = at bottom, positive = scrolled up
        self.auto_scroll = True
        self.next_command_id = 0
        
        # Filtering
        self.show_timestamps = False
        self.output_filter: Optional[Callable[[OutputLine], bool]] = None
    
    def add_line(self, text: str, output_type: OutputType, 
                command_id: Optional[int] = None):
        """Add a line to the output buffer"""
        line = OutputLine(
            text=text,
            output_type=output_type,
            timestamp=time.time(),
            command_id=command_id
        )
        
        self.lines.append(line)
        
        # Auto-scroll if enabled
        if self.auto_scroll:
            self.scroll_position = 0
    
    def add_command(self, command: str) -> int:
        """Add a command to the buffer and return command ID"""
        command_id = self.next_command_id
        self.next_command_id += 1
        
        self.add_line(f"$ {command}", OutputType.COMMAND, command_id)
        return command_id
    
    def add_result(self, result: CommandResult, command_id: int):
        """Add command result to buffer"""
        # Add stdout
        for line in result.stdout:
            self.add_line(line, OutputType.STDOUT, command_id)
        
        # Add stderr
        for line in result.stderr:
            self.add_line(line, OutputType.STDERR, command_id)
        
        # Add status message
        if result.success:
            status = f"[✓] Command completed in {result.execution_time:.2f}s"
            self.add_line(status, OutputType.SUCCESS, command_id)
        else:
            status = f"[✗] Command failed with exit code {result.exit_code}"
            self.add_line(status, OutputType.ERROR, command_id)
    
    def get_visible_lines(self, viewport_height: int) -> List[OutputLine]:
        """Get lines visible in viewport"""
        total_lines = len(self.lines)
        
        if total_lines == 0:
            return []
        
        # Calculate visible range
        end_index = total_lines - self.scroll_position
        start_index = max(0, end_index - viewport_height)
        
        # Apply filter if set
        visible = list(self.lines)[start_index:end_index]
        
        if self.output_filter:
            visible = [line for line in visible if self.output_filter(line)]
        
        return visible
    
    def scroll_up(self, lines: int = 1):
        """Scroll up by lines"""
        max_scroll = len(self.lines)
        self.scroll_position = min(max_scroll, self.scroll_position + lines)
        self.auto_scroll = False
    
    def scroll_down(self, lines: int = 1):
        """Scroll down by lines"""
        self.scroll_position = max(0, self.scroll_position - lines)
        
        if self.scroll_position == 0:
            self.auto_scroll = True
    
    def scroll_to_bottom(self):
        """Scroll to bottom"""
        self.scroll_position = 0
        self.auto_scroll = True
    
    def scroll_to_top(self):
        """Scroll to top"""
        self.scroll_position = len(self.lines)
        self.auto_scroll = False
    
    def clear(self):
        """Clear all output"""
        self.lines.clear()
        self.scroll_position = 0
        self.auto_scroll = True
    
    def search(self, term: str) -> List[OutputLine]:
        """Search for lines containing term"""
        results = []
        for line in self.lines:
            if term.lower() in line.text.lower():
                results.append(line)
        return results


# ═══════════════════════════════════════════════════════════════════════════════
# ENVIRONMENT MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

class EnvironmentManager:
    """Manages environment variables and working directory"""
    
    def __init__(self):
        self.env = os.environ.copy()
        self.cwd = os.getcwd()
        self.aliases: Dict[str, str] = {}
        
        # Track directory history
        self.dir_history: deque[str] = deque(maxlen=100)
        self.dir_history.append(self.cwd)
    
    def set_var(self, name: str, value: str):
        """Set environment variable"""
        self.env[name] = value
    
    def get_var(self, name: str) -> Optional[str]:
        """Get environment variable"""
        return self.env.get(name)
    
    def unset_var(self, name: str):
        """Unset environment variable"""
        if name in self.env:
            del self.env[name]
    
    def get_all_vars(self) -> Dict[str, str]:
        """Get all environment variables"""
        return self.env.copy()
    
    def change_dir(self, path: str) -> bool:
        """Change working directory"""
        try:
            # Expand user and environment variables
            path = os.path.expanduser(path)
            path = os.path.expandvars(path)
            
            # Handle relative paths
            if not os.path.isabs(path):
                path = os.path.join(self.cwd, path)
            
            # Normalize path
            path = os.path.normpath(path)
            
            if os.path.isdir(path):
                self.cwd = path
                self.dir_history.append(path)
                return True
            else:
                return False
        except:
            return False
    
    def get_cwd(self) -> str:
        """Get current working directory"""
        return self.cwd
    
    def set_alias(self, name: str, command: str):
        """Set command alias"""
        self.aliases[name] = command
    
    def get_alias(self, name: str) -> Optional[str]:
        """Get command alias"""
        return self.aliases.get(name)
    
    def expand_alias(self, command: str) -> str:
        """Expand aliases in command"""
        parts = shlex.split(command)
        if parts and parts[0] in self.aliases:
            alias_cmd = self.aliases[parts[0]]
            return alias_cmd + ' ' + ' '.join(parts[1:])
        return command


# ═══════════════════════════════════════════════════════════════════════════════
# BUILTIN COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

class BuiltinCommands:
    """Handles built-in shell commands"""
    
    def __init__(self, env_manager: EnvironmentManager, output_buffer: OutputBuffer):
        self.env = env_manager
        self.output = output_buffer
        
        self.builtins = {
            'cd': self._cmd_cd,
            'pwd': self._cmd_pwd,
            'export': self._cmd_export,
            'alias': self._cmd_alias,
            'unalias': self._cmd_unalias,
            'history': self._cmd_history,
            'clear': self._cmd_clear,
            'exit': self._cmd_exit,
            'help': self._cmd_help,
        }
    
    def is_builtin(self, command: str) -> bool:
        """Check if command is a builtin"""
        parts = shlex.split(command)
        return len(parts) > 0 and parts[0] in self.builtins
    
    def execute(self, command: str) -> CommandResult:
        """Execute builtin command"""
        start_time = time.time()
        parts = shlex.split(command)
        
        if not parts:
            return CommandResult(
                command=command,
                exit_code=0,
                stdout=[],
                stderr=[],
                execution_time=0,
                success=True
            )
        
        cmd_name = parts[0]
        args = parts[1:]
        
        if cmd_name in self.builtins:
            try:
                result = self.builtins[cmd_name](args)
                execution_time = time.time() - start_time
                
                return CommandResult(
                    command=command,
                    exit_code=0 if result['success'] else 1,
                    stdout=result.get('stdout', []),
                    stderr=result.get('stderr', []),
                    execution_time=execution_time,
                    success=result['success']
                )
            except Exception as e:
                execution_time = time.time() - start_time
                return CommandResult(
                    command=command,
                    exit_code=1,
                    stdout=[],
                    stderr=[f"Error: {str(e)}"],
                    execution_time=execution_time,
                    success=False
                )
        
        return CommandResult(
            command=command,
            exit_code=1,
            stdout=[],
            stderr=[f"Unknown builtin: {cmd_name}"],
            execution_time=0,
            success=False
        )
    
    def _cmd_cd(self, args: List[str]) -> Dict:
        """Change directory"""
        if not args:
            path = os.path.expanduser('~')
        else:
            path = args[0]
        
        if self.env.change_dir(path):
            return {'success': True, 'stdout': []}
        else:
            return {'success': False, 'stderr': [f"cd: {path}: No such file or directory"]}
    
    def _cmd_pwd(self, args: List[str]) -> Dict:
        """Print working directory"""
        return {'success': True, 'stdout': [self.env.get_cwd()]}
    
    def _cmd_export(self, args: List[str]) -> Dict:
        """Export environment variable"""
        if not args:
            # List all variables
            lines = [f"{k}={v}" for k, v in sorted(self.env.get_all_vars().items())]
            return {'success': True, 'stdout': lines}
        
        for arg in args:
            if '=' in arg:
                name, value = arg.split('=', 1)
                self.env.set_var(name, value)
            else:
                return {'success': False, 'stderr': [f"export: invalid argument: {arg}"]}
        
        return {'success': True, 'stdout': []}
    
    def _cmd_alias(self, args: List[str]) -> Dict:
        """Set or list aliases"""
        if not args:
            # List all aliases
            lines = [f"alias {k}='{v}'" for k, v in sorted(self.env.aliases.items())]
            return {'success': True, 'stdout': lines}
        
        for arg in args:
            if '=' in arg:
                name, value = arg.split('=', 1)
                value = value.strip("'\"")
                self.env.set_alias(name, value)
            else:
                alias = self.env.get_alias(arg)
                if alias:
                    return {'success': True, 'stdout': [f"alias {arg}='{alias}'"]}
                else:
                    return {'success': False, 'stderr': [f"alias: {arg}: not found"]}
        
        return {'success': True, 'stdout': []}
    
    def _cmd_unalias(self, args: List[str]) -> Dict:
        """Remove alias"""
        if not args:
            return {'success': False, 'stderr': ['unalias: usage: unalias name']}
        
        for name in args:
            if name in self.env.aliases:
                del self.env.aliases[name]
            else:
                return {'success': False, 'stderr': [f"unalias: {name}: not found"]}
        
        return {'success': True, 'stdout': []}
    
    def _cmd_history(self, args: List[str]) -> Dict:
        """Show command history"""
        # This would need access to InputContext's history
        return {'success': True, 'stdout': ['History not available in builtin']}
    
    def _cmd_clear(self, args: List[str]) -> Dict:
        """Clear screen"""
        self.output.clear()
        return {'success': True, 'stdout': []}
    
    def _cmd_exit(self, args: List[str]) -> Dict:
        """Exit shell"""
        # This should be handled by the main application
        return {'success': True, 'stdout': ['Use Ctrl+C or close window to exit']}
    
    def _cmd_help(self, args: List[str]) -> Dict:
        """Show help"""
        help_text = [
            "Built-in commands:",
            "  cd [dir]         Change directory",
            "  pwd              Print working directory",
            "  export [VAR=val] Set environment variable",
            "  alias [name=cmd] Set command alias",
            "  unalias name     Remove alias",
            "  history          Show command history",
            "  clear            Clear screen",
            "  exit             Exit shell",
            "  help             Show this help",
        ]
        return {'success': True, 'stdout': help_text}


# ═══════════════════════════════════════════════════════════════════════════════
# TERMINAL SESSION
# ═══════════════════════════════════════════════════════════════════════════════

class TerminalSession:
    """Complete terminal session manager"""
    
    def __init__(self):
        self.executor = CommandExecutor()
        self.output = OutputBuffer()
        self.env = EnvironmentManager()
        self.builtins = BuiltinCommands(self.env, self.output)
        
        # Callbacks
        self.on_output: Optional[Callable[[str, OutputType], None]] = None
        self.on_command_complete: Optional[Callable[[CommandResult], None]] = None
        
        # Welcome message
        self._show_welcome()
    
    def _show_welcome(self):
        """Show welcome message"""
        welcome = [
            "╔══════════════════════════════════════════════════════════════╗",
            "║          CYBERPUNK TERMINAL - Christmas Edition             ║",
            "║                  Enhanced Shell Experience                   ║",
            "╚══════════════════════════════════════════════════════════════╝",
            "",
            "Type 'help' for available commands.",
            ""
        ]
        
        for line in welcome:
            self.output.add_line(line, OutputType.SYSTEM)
    
    def execute_command(self, command: str) -> int:
        """
        Execute a command.
        Returns command ID.
        """
        command = command.strip()
        
        if not command:
            return -1
        
        # Add command to output
        command_id = self.output.add_command(command)
        
        # Expand aliases
        expanded_command = self.env.expand_alias(command)
        
        # Check for builtin commands
        if self.builtins.is_builtin(expanded_command):
            result = self.builtins.execute(expanded_command)
            self.output.add_result(result, command_id)
            
            if self.on_command_complete:
                self.on_command_complete(result)
            
            return command_id
        
        # Execute external command asynchronously
        def output_callback(line: str, output_type: OutputType):
            self.output.add_line(line, output_type, command_id)
            if self.on_output:
                self.on_output(line, output_type)
        
        def completion_callback(result: CommandResult):
            # Add completion status
            if result.success:
                status = f"[✓] Command completed in {result.execution_time:.2f}s"
                self.output.add_line(status, OutputType.SUCCESS, command_id)
            else:
                status = f"[✗] Command failed with exit code {result.exit_code}"
                self.output.add_line(status, OutputType.ERROR, command_id)
            
            if self.on_command_complete:
                self.on_command_complete(result)
        
        self.executor.execute_async(
            expanded_command,
            output_callback,
            completion_callback,
            cwd=self.env.get_cwd(),
            env=self.env.get_all_vars()
        )
        
        return command_id
    
    def get_output_lines(self, viewport_height: int) -> List[OutputLine]:
        """Get visible output lines"""
        return self.output.get_visible_lines(viewport_height)
    
    def scroll_output(self, delta: int):
        """Scroll output buffer"""
        if delta > 0:
            self.output.scroll_up(delta)
        else:
            self.output.scroll_down(-delta)
    
    def get_prompt(self) -> str:
        """Get command prompt string"""
        cwd = self.env.get_cwd()
        home = os.path.expanduser('~')
        
        # Replace home with ~
        if cwd.startswith(home):
            cwd = '~' + cwd[len(home):]
        
        # Get username and hostname
        user = os.environ.get('USER', 'user')
        hostname = os.environ.get('HOSTNAME', 'localhost')
        
        return f"{user}@{hostname}:{cwd}$ "


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    'OutputType', 'OutputLine',
    'CommandResult', 'CommandExecutor',
    'OutputBuffer',
    'EnvironmentManager',
    'BuiltinCommands',
    'TerminalSession',
]

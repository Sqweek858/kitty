#!/usr/bin/env python3
"""
Brad TUI Ultra - Utilities Module
==================================

Comprehensive utility functions and helper classes for Brad TUI Ultra.
Includes text processing, terminal utilities, performance tools, and more.

Features:
- Text formatting and manipulation
- Terminal capabilities detection
- File system utilities
- Process management
- Performance profiling
- Caching system
- Async helpers
- Data validation
"""

import os
import sys
import re
import time
import subprocess
import tempfile
import hashlib
import pickle
import gzip
import shutil
import fcntl
import termios
import struct
import select
from typing import (
    Any, Optional, List, Tuple, Dict, Callable, Union,
    Iterator, TypeVar, Generic
)
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass
from functools import wraps
import json


# =============================================================================
# TERMINAL UTILITIES
# =============================================================================

class TerminalUtils:
    """Utilities for terminal interaction and detection"""
    
    @staticmethod
    def get_terminal_size() -> Tuple[int, int]:
        """Get terminal size (width, height)"""
        try:
            size = os.get_terminal_size()
            return size.columns, size.lines
        except (AttributeError, OSError):
            # Fallback
            try:
                rows, cols = os.popen('stty size', 'r').read().split()
                return int(cols), int(rows)
            except:
                return 80, 24  # Default
    
    @staticmethod
    def get_terminal_size_px() -> Tuple[int, int]:
        """Get terminal size in pixels (if supported)"""
        try:
            # Try to get pixel size using ioctl
            winsize = struct.pack('HHHH', 0, 0, 0, 0)
            result = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, winsize)
            rows, cols, xpixel, ypixel = struct.unpack('HHHH', result)
            return xpixel, ypixel
        except:
            return 0, 0
    
    @staticmethod
    def supports_true_color() -> bool:
        """Check if terminal supports 24-bit true color"""
        colorterm = os.environ.get('COLORTERM', '')
        return colorterm in ['truecolor', '24bit']
    
    @staticmethod
    def supports_256_color() -> bool:
        """Check if terminal supports 256 colors"""
        term = os.environ.get('TERM', '')
        return '256' in term or TerminalUtils.supports_true_color()
    
    @staticmethod
    def get_color_depth() -> int:
        """Get terminal color depth (8, 256, or 16777216 for true color)"""
        if TerminalUtils.supports_true_color():
            return 16777216
        elif TerminalUtils.supports_256_color():
            return 256
        else:
            return 8
    
    @staticmethod
    def is_ssh_session() -> bool:
        """Check if running in SSH session"""
        return 'SSH_CONNECTION' in os.environ or 'SSH_CLIENT' in os.environ
    
    @staticmethod
    def is_tmux() -> bool:
        """Check if running inside tmux"""
        return 'TMUX' in os.environ
    
    @staticmethod
    def is_screen() -> bool:
        """Check if running inside screen"""
        return 'STY' in os.environ or os.environ.get('TERM', '').startswith('screen')
    
    @staticmethod
    def get_terminal_emulator() -> str:
        """Try to detect terminal emulator"""
        term_program = os.environ.get('TERM_PROGRAM', '')
        if term_program:
            return term_program
        
        term = os.environ.get('TERM', '')
        if 'kitty' in term:
            return 'kitty'
        elif 'alacritty' in term:
            return 'alacritty'
        elif 'konsole' in os.environ.get('KONSOLE_VERSION', ''):
            return 'konsole'
        elif 'GNOME_TERMINAL' in os.environ:
            return 'gnome-terminal'
        
        return 'unknown'
    
    @staticmethod
    def clear_screen() -> None:
        """Clear terminal screen"""
        sys.stdout.write('\x1b[2J\x1b[H')
        sys.stdout.flush()
    
    @staticmethod
    def move_cursor(x: int, y: int) -> None:
        """Move cursor to position"""
        sys.stdout.write(f'\x1b[{y+1};{x+1}H')
        sys.stdout.flush()
    
    @staticmethod
    def hide_cursor() -> None:
        """Hide terminal cursor"""
        sys.stdout.write('\x1b[?25l')
        sys.stdout.flush()
    
    @staticmethod
    def show_cursor() -> None:
        """Show terminal cursor"""
        sys.stdout.write('\x1b[?25h')
        sys.stdout.flush()
    
    @staticmethod
    def set_title(title: str) -> None:
        """Set terminal window title"""
        sys.stdout.write(f'\x1b]0;{title}\x07')
        sys.stdout.flush()
    
    @staticmethod
    def bell() -> None:
        """Ring terminal bell"""
        sys.stdout.write('\x07')
        sys.stdout.flush()


# =============================================================================
# TEXT UTILITIES
# =============================================================================

class TextUtils:
    """Text processing and manipulation utilities"""
    
    @staticmethod
    def strip_ansi(text: str) -> str:
        """Remove ANSI escape codes from text"""
        ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
        return ansi_escape.sub('', text)
    
    @staticmethod
    def visible_length(text: str) -> int:
        """Get visible length of text (excluding ANSI codes)"""
        return len(TextUtils.strip_ansi(text))
    
    @staticmethod
    def truncate(text: str, max_length: int, suffix: str = "...") -> str:
        """Truncate text to maximum visible length"""
        visible_len = TextUtils.visible_length(text)
        if visible_len <= max_length:
            return text
        
        # Strip ANSI, truncate, add suffix
        plain = TextUtils.strip_ansi(text)
        return plain[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def pad_right(text: str, width: int, char: str = " ") -> str:
        """Pad text to width (accounting for ANSI codes)"""
        visible_len = TextUtils.visible_length(text)
        if visible_len >= width:
            return text
        return text + (char * (width - visible_len))
    
    @staticmethod
    def pad_left(text: str, width: int, char: str = " ") -> str:
        """Pad text to width on left side"""
        visible_len = TextUtils.visible_length(text)
        if visible_len >= width:
            return text
        return (char * (width - visible_len)) + text
    
    @staticmethod
    def center(text: str, width: int, char: str = " ") -> str:
        """Center text in width"""
        visible_len = TextUtils.visible_length(text)
        if visible_len >= width:
            return text
        
        padding = width - visible_len
        left_pad = padding // 2
        right_pad = padding - left_pad
        
        return (char * left_pad) + text + (char * right_pad)
    
    @staticmethod
    def wrap_text(text: str, width: int) -> List[str]:
        """Wrap text to width"""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            word_len = len(word)
            if current_length + word_len + len(current_line) <= width:
                current_line.append(word)
                current_length += word_len
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = word_len
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    @staticmethod
    def indent(text: str, spaces: int = 4) -> str:
        """Indent text"""
        indent_str = ' ' * spaces
        lines = text.split('\n')
        return '\n'.join(indent_str + line for line in lines)
    
    @staticmethod
    def slugify(text: str) -> str:
        """Convert text to slug (lowercase, hyphenated)"""
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[\s_-]+', '-', text)
        text = text.strip('-')
        return text
    
    @staticmethod
    def humanize_bytes(size: int) -> str:
        """Convert bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"
    
    @staticmethod
    def humanize_time(seconds: float) -> str:
        """Convert seconds to human readable format"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            return f"{seconds/60:.1f}m"
        elif seconds < 86400:
            return f"{seconds/3600:.1f}h"
        else:
            return f"{seconds/86400:.1f}d"
    
    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """Extract URLs from text"""
        url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        return url_pattern.findall(text)
    
    @staticmethod
    def extract_emails(text: str) -> List[str]:
        """Extract email addresses from text"""
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        return email_pattern.findall(text)


# =============================================================================
# FILE SYSTEM UTILITIES
# =============================================================================

class FileUtils:
    """File system utilities"""
    
    @staticmethod
    def ensure_dir(path: Union[str, Path]) -> Path:
        """Ensure directory exists"""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @staticmethod
    def safe_read(path: Union[str, Path], default: str = "") -> str:
        """Safely read file, return default if error"""
        try:
            with open(path, 'r') as f:
                return f.read()
        except:
            return default
    
    @staticmethod
    def safe_write(path: Union[str, Path], content: str) -> bool:
        """Safely write file, return success status"""
        try:
            path = Path(path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w') as f:
                f.write(content)
            return True
        except:
            return False
    
    @staticmethod
    def atomic_write(path: Union[str, Path], content: str) -> bool:
        """Atomically write file using temporary file"""
        try:
            path = Path(path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write to temporary file
            with tempfile.NamedTemporaryFile(
                mode='w',
                dir=path.parent,
                delete=False
            ) as tmp:
                tmp.write(content)
                tmp_path = tmp.name
            
            # Atomic move
            shutil.move(tmp_path, path)
            return True
        except:
            return False
    
    @staticmethod
    def get_file_hash(path: Union[str, Path], algorithm: str = 'sha256') -> str:
        """Get file hash"""
        hasher = hashlib.new(algorithm)
        
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        
        return hasher.hexdigest()
    
    @staticmethod
    def find_files(
        directory: Union[str, Path],
        pattern: str = "*",
        recursive: bool = True
    ) -> List[Path]:
        """Find files matching pattern"""
        directory = Path(directory)
        
        if recursive:
            return list(directory.rglob(pattern))
        else:
            return list(directory.glob(pattern))
    
    @staticmethod
    def get_size(path: Union[str, Path]) -> int:
        """Get file or directory size"""
        path = Path(path)
        
        if path.is_file():
            return path.stat().st_size
        
        total = 0
        for entry in path.rglob('*'):
            if entry.is_file():
                total += entry.stat().st_size
        
        return total
    
    @staticmethod
    def copy_file(src: Union[str, Path], dst: Union[str, Path]) -> bool:
        """Copy file with error handling"""
        try:
            shutil.copy2(src, dst)
            return True
        except:
            return False
    
    @staticmethod
    def move_file(src: Union[str, Path], dst: Union[str, Path]) -> bool:
        """Move file with error handling"""
        try:
            shutil.move(src, dst)
            return True
        except:
            return False


# =============================================================================
# PROCESS UTILITIES
# =============================================================================

class ProcessUtils:
    """Process management utilities"""
    
    @staticmethod
    def run_command(
        command: Union[str, List[str]],
        timeout: Optional[float] = None,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None
    ) -> Tuple[int, str, str]:
        """
        Run command and return (exit_code, stdout, stderr)
        """
        try:
            if isinstance(command, str):
                command = command.split()
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd,
                env=env
            )
            
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
        except Exception as e:
            return -1, "", str(e)
    
    @staticmethod
    def is_process_running(pid: int) -> bool:
        """Check if process is running"""
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False
    
    @staticmethod
    def get_process_info(pid: int) -> Optional[Dict[str, Any]]:
        """Get process information"""
        try:
            # This is a simplified version
            # In practice, would use psutil or parse /proc
            with open(f'/proc/{pid}/status', 'r') as f:
                info = {}
                for line in f:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        info[key.strip()] = value.strip()
                return info
        except:
            return None
    
    @staticmethod
    def kill_process(pid: int, signal: int = 15) -> bool:
        """Kill process by PID"""
        try:
            os.kill(pid, signal)
            return True
        except:
            return False


# =============================================================================
# CACHE SYSTEM
# =============================================================================

T = TypeVar('T')

class Cache(Generic[T]):
    """Generic cache with expiration"""
    
    def __init__(self, max_size: int = 100, ttl: float = 300):
        """Initialize cache"""
        self.max_size = max_size
        self.ttl = ttl
        self.cache: Dict[str, Tuple[T, float]] = {}
    
    def get(self, key: str) -> Optional[T]:
        """Get value from cache"""
        if key not in self.cache:
            return None
        
        value, timestamp = self.cache[key]
        
        # Check if expired
        if time.time() - timestamp > self.ttl:
            del self.cache[key]
            return None
        
        return value
    
    def set(self, key: str, value: T) -> None:
        """Set value in cache"""
        # Evict oldest if at max size
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache, key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
        
        self.cache[key] = (value, time.time())
    
    def delete(self, key: str) -> None:
        """Delete value from cache"""
        if key in self.cache:
            del self.cache[key]
    
    def clear(self) -> None:
        """Clear entire cache"""
        self.cache.clear()
    
    def cleanup(self) -> None:
        """Remove expired entries"""
        now = time.time()
        expired = [
            k for k, (_, timestamp) in self.cache.items()
            if now - timestamp > self.ttl
        ]
        for key in expired:
            del self.cache[key]


class DiskCache:
    """Persistent disk-based cache"""
    
    def __init__(self, cache_dir: Union[str, Path]):
        """Initialize disk cache"""
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_path(self, key: str) -> Path:
        """Get cache file path for key"""
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        path = self._get_path(key)
        
        if not path.exists():
            return None
        
        try:
            with gzip.open(path, 'rb') as f:
                data = pickle.load(f)
                value, timestamp, ttl = data
                
                # Check expiration
                if ttl and time.time() - timestamp > ttl:
                    path.unlink()
                    return None
                
                return value
        except:
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> bool:
        """Set value in cache"""
        path = self._get_path(key)
        
        try:
            data = (value, time.time(), ttl)
            with gzip.open(path, 'wb') as f:
                pickle.dump(data, f)
            return True
        except:
            return False
    
    def delete(self, key: str) -> None:
        """Delete value from cache"""
        path = self._get_path(key)
        if path.exists():
            path.unlink()
    
    def clear(self) -> None:
        """Clear entire cache"""
        for path in self.cache_dir.glob("*.cache"):
            path.unlink()


# =============================================================================
# PERFORMANCE UTILITIES
# =============================================================================

class Timer:
    """Context manager for timing code execution"""
    
    def __init__(self, name: str = ""):
        """Initialize timer"""
        self.name = name
        self.start_time = 0.0
        self.end_time = 0.0
        self.elapsed = 0.0
    
    def __enter__(self):
        """Start timer"""
        self.start_time = time.time()
        return self
    
    def __exit__(self, *args):
        """Stop timer"""
        self.end_time = time.time()
        self.elapsed = self.end_time - self.start_time
        
        if self.name:
            print(f"{self.name}: {self.elapsed:.4f}s")


def timed(func: Callable) -> Callable:
    """Decorator to time function execution"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"{func.__name__} took {elapsed:.4f}s")
        return result
    return wrapper


class Profiler:
    """Simple profiler for tracking function calls and timing"""
    
    def __init__(self):
        """Initialize profiler"""
        self.stats: Dict[str, Dict[str, Any]] = {}
    
    def record(self, name: str, duration: float) -> None:
        """Record a timing"""
        if name not in self.stats:
            self.stats[name] = {
                'count': 0,
                'total': 0.0,
                'min': float('inf'),
                'max': 0.0,
            }
        
        stats = self.stats[name]
        stats['count'] += 1
        stats['total'] += duration
        stats['min'] = min(stats['min'], duration)
        stats['max'] = max(stats['max'], duration)
    
    def get_stats(self, name: str) -> Optional[Dict[str, Any]]:
        """Get stats for function"""
        if name not in self.stats:
            return None
        
        stats = self.stats[name]
        avg = stats['total'] / stats['count'] if stats['count'] > 0 else 0
        
        return {
            'count': stats['count'],
            'total': stats['total'],
            'average': avg,
            'min': stats['min'],
            'max': stats['max'],
        }
    
    def print_stats(self) -> None:
        """Print all statistics"""
        print("\nProfiler Statistics:")
        print("=" * 70)
        print(f"{'Function':<30} {'Calls':>8} {'Total':>10} {'Avg':>10} {'Min':>10} {'Max':>10}")
        print("-" * 70)
        
        for name in sorted(self.stats.keys()):
            stats = self.get_stats(name)
            if stats:
                print(
                    f"{name:<30} {stats['count']:>8} "
                    f"{stats['total']:>10.4f} {stats['average']:>10.4f} "
                    f"{stats['min']:>10.4f} {stats['max']:>10.4f}"
                )
        
        print("=" * 70)


# =============================================================================
# VALIDATION UTILITIES
# =============================================================================

class Validator:
    """Data validation utilities"""
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Check if string is valid email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if string is valid URL"""
        pattern = r'^https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b'
        return bool(re.match(pattern, url))
    
    @staticmethod
    def is_valid_ipv4(ip: str) -> bool:
        """Check if string is valid IPv4 address"""
        pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        return bool(re.match(pattern, ip))
    
    @staticmethod
    def is_valid_port(port: Union[str, int]) -> bool:
        """Check if port number is valid"""
        try:
            port_int = int(port)
            return 1 <= port_int <= 65535
        except:
            return False
    
    @staticmethod
    def is_valid_path(path: str) -> bool:
        """Check if path is valid"""
        try:
            Path(path)
            return True
        except:
            return False


# =============================================================================
# MAIN (for testing)
# =============================================================================

if __name__ == "__main__":
    print("Brad TUI Ultra - Utilities Module")
    print("=" * 50)
    
    # Test terminal utilities
    print("\nTerminal Information:")
    width, height = TerminalUtils.get_terminal_size()
    print(f"Size: {width}x{height}")
    print(f"True color: {TerminalUtils.supports_true_color()}")
    print(f"Color depth: {TerminalUtils.get_color_depth()}")
    print(f"Emulator: {TerminalUtils.get_terminal_emulator()}")
    print(f"In tmux: {TerminalUtils.is_tmux()}")
    
    # Test text utilities
    print("\nText Utilities:")
    text = "\x1b[31mRed text\x1b[0m"
    print(f"Original: {text}")
    print(f"Stripped: {TextUtils.strip_ansi(text)}")
    print(f"Visible length: {TextUtils.visible_length(text)}")
    
    # Test cache
    print("\nCache Test:")
    cache = Cache[str](max_size=3, ttl=5)
    cache.set("key1", "value1")
    print(f"Get key1: {cache.get('key1')}")
    
    # Test timer
    print("\nTimer Test:")
    with Timer("Test operation") as timer:
        time.sleep(0.1)
    print(f"Elapsed: {timer.elapsed:.4f}s")
    
    print("\n✅ Utilities module test complete")

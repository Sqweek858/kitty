#!/usr/bin/env python3
"""
Brad TUI Ultra - Logging and Monitoring Module
==============================================

Comprehensive logging, monitoring, and telemetry system for Brad TUI Ultra.
Includes structured logging, log rotation, analytics, and performance monitoring.

Features:
- Multi-level logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Structured JSON logging
- Log rotation and compression
- Real-time monitoring
- Performance metrics
- Error tracking
- Event analytics
- Log filtering and searching
"""

import os
import sys
import time
import json
import gzip
import logging
import logging.handlers
from typing import Any, Dict, List, Optional, Callable, Union
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, deque
import threading
import traceback


# =============================================================================
# LOG LEVELS
# =============================================================================

class LogLevel(Enum):
    """Log levels"""
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


class LogCategory(Enum):
    """Log categories for organizing logs"""
    SYSTEM = "system"
    UI = "ui"
    COMMAND = "command"
    PLUGIN = "plugin"
    EFFECT = "effect"
    CONFIG = "config"
    PERFORMANCE = "performance"
    SECURITY = "security"
    NETWORK = "network"
    USER = "user"


# =============================================================================
# LOG ENTRY
# =============================================================================

@dataclass
class LogEntry:
    """Structured log entry"""
    timestamp: float
    level: LogLevel
    category: LogCategory
    message: str
    context: Dict[str, Any] = field(default_factory=dict)
    stack_trace: Optional[str] = None
    thread_id: Optional[int] = None
    process_id: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'timestamp': self.timestamp,
            'datetime': datetime.fromtimestamp(self.timestamp).isoformat(),
            'level': self.level.name,
            'category': self.category.value,
            'message': self.message,
            'context': self.context,
            'stack_trace': self.stack_trace,
            'thread_id': self.thread_id,
            'process_id': self.process_id,
        }
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())
    
    def to_text(self) -> str:
        """Convert to human-readable text"""
        dt = datetime.fromtimestamp(self.timestamp)
        return (
            f"[{dt.strftime('%Y-%m-%d %H:%M:%S')}] "
            f"{self.level.name:<8} "
            f"[{self.category.value}] "
            f"{self.message}"
        )


# =============================================================================
# LOG FORMATTER
# =============================================================================

class LogFormatter:
    """Formats log entries"""
    
    @staticmethod
    def format_text(entry: LogEntry) -> str:
        """Format as plain text"""
        return entry.to_text()
    
    @staticmethod
    def format_json(entry: LogEntry) -> str:
        """Format as JSON"""
        return entry.to_json()
    
    @staticmethod
    def format_colored(entry: LogEntry) -> str:
        """Format with ANSI colors"""
        level_colors = {
            LogLevel.DEBUG: '\x1b[36m',      # Cyan
            LogLevel.INFO: '\x1b[32m',       # Green
            LogLevel.WARNING: '\x1b[33m',    # Yellow
            LogLevel.ERROR: '\x1b[31m',      # Red
            LogLevel.CRITICAL: '\x1b[35m',   # Magenta
        }
        
        color = level_colors.get(entry.level, '')
        reset = '\x1b[0m'
        
        dt = datetime.fromtimestamp(entry.timestamp)
        return (
            f"{color}[{dt.strftime('%Y-%m-%d %H:%M:%S')}] "
            f"{entry.level.name:<8} "
            f"[{entry.category.value}] "
            f"{entry.message}{reset}"
        )


# =============================================================================
# LOG HANDLER
# =============================================================================

class LogHandler:
    """Base class for log handlers"""
    
    def __init__(self, level: LogLevel = LogLevel.INFO):
        """Initialize handler"""
        self.level = level
        self.filters: List[Callable[[LogEntry], bool]] = []
    
    def add_filter(self, filter_func: Callable[[LogEntry], bool]) -> None:
        """Add a filter function"""
        self.filters.append(filter_func)
    
    def should_handle(self, entry: LogEntry) -> bool:
        """Check if entry should be handled"""
        if entry.level.value < self.level.value:
            return False
        
        for filter_func in self.filters:
            if not filter_func(entry):
                return False
        
        return True
    
    def handle(self, entry: LogEntry) -> None:
        """Handle log entry"""
        if self.should_handle(entry):
            self.emit(entry)
    
    def emit(self, entry: LogEntry) -> None:
        """Emit log entry (to be implemented by subclasses)"""
        pass


class ConsoleHandler(LogHandler):
    """Handler that writes to console"""
    
    def __init__(
        self,
        level: LogLevel = LogLevel.INFO,
        colored: bool = True,
        stream = sys.stdout
    ):
        """Initialize console handler"""
        super().__init__(level)
        self.colored = colored
        self.stream = stream
    
    def emit(self, entry: LogEntry) -> None:
        """Write to console"""
        if self.colored:
            text = LogFormatter.format_colored(entry)
        else:
            text = LogFormatter.format_text(entry)
        
        self.stream.write(text + '\n')
        self.stream.flush()


class FileHandler(LogHandler):
    """Handler that writes to file"""
    
    def __init__(
        self,
        filepath: Union[str, Path],
        level: LogLevel = LogLevel.INFO,
        json_format: bool = False,
        max_bytes: int = 10 * 1024 * 1024,  # 10 MB
        backup_count: int = 5
    ):
        """Initialize file handler"""
        super().__init__(level)
        self.filepath = Path(filepath)
        self.json_format = json_format
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        
        # Ensure directory exists
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Open file
        self.file = open(self.filepath, 'a')
    
    def emit(self, entry: LogEntry) -> None:
        """Write to file"""
        if self.json_format:
            text = LogFormatter.format_json(entry)
        else:
            text = LogFormatter.format_text(entry)
        
        self.file.write(text + '\n')
        self.file.flush()
        
        # Check if rotation needed
        if self.filepath.stat().st_size > self.max_bytes:
            self.rotate()
    
    def rotate(self) -> None:
        """Rotate log file"""
        self.file.close()
        
        # Rotate existing backups
        for i in range(self.backup_count - 1, 0, -1):
            old_file = self.filepath.with_suffix(f'.{i}.gz')
            new_file = self.filepath.with_suffix(f'.{i+1}.gz')
            if old_file.exists():
                old_file.rename(new_file)
        
        # Compress current file
        backup_file = self.filepath.with_suffix('.1.gz')
        with open(self.filepath, 'rb') as f_in:
            with gzip.open(backup_file, 'wb') as f_out:
                f_out.writelines(f_in)
        
        # Open new file
        self.file = open(self.filepath, 'w')
    
    def close(self) -> None:
        """Close file"""
        if self.file:
            self.file.close()


class MemoryHandler(LogHandler):
    """Handler that keeps logs in memory"""
    
    def __init__(
        self,
        level: LogLevel = LogLevel.INFO,
        max_entries: int = 1000
    ):
        """Initialize memory handler"""
        super().__init__(level)
        self.max_entries = max_entries
        self.entries: deque = deque(maxlen=max_entries)
    
    def emit(self, entry: LogEntry) -> None:
        """Store in memory"""
        self.entries.append(entry)
    
    def get_entries(
        self,
        level: Optional[LogLevel] = None,
        category: Optional[LogCategory] = None,
        limit: Optional[int] = None
    ) -> List[LogEntry]:
        """Get stored entries with optional filtering"""
        entries = list(self.entries)
        
        if level:
            entries = [e for e in entries if e.level == level]
        
        if category:
            entries = [e for e in entries if e.category == category]
        
        if limit:
            entries = entries[-limit:]
        
        return entries
    
    def clear(self) -> None:
        """Clear all entries"""
        self.entries.clear()


# =============================================================================
# LOGGER
# =============================================================================

class Logger:
    """Main logger class"""
    
    def __init__(self, name: str = "brad_tui"):
        """Initialize logger"""
        self.name = name
        self.handlers: List[LogHandler] = []
        self.enabled = True
    
    def add_handler(self, handler: LogHandler) -> None:
        """Add log handler"""
        self.handlers.append(handler)
    
    def remove_handler(self, handler: LogHandler) -> None:
        """Remove log handler"""
        if handler in self.handlers:
            self.handlers.remove(handler)
    
    def log(
        self,
        level: LogLevel,
        category: LogCategory,
        message: str,
        **context
    ) -> None:
        """Log a message"""
        if not self.enabled:
            return
        
        entry = LogEntry(
            timestamp=time.time(),
            level=level,
            category=category,
            message=message,
            context=context,
            thread_id=threading.get_ident(),
            process_id=os.getpid(),
        )
        
        for handler in self.handlers:
            try:
                handler.handle(entry)
            except Exception as e:
                # Don't let handler errors break logging
                print(f"Error in log handler: {e}", file=sys.stderr)
    
    def debug(self, message: str, category: LogCategory = LogCategory.SYSTEM, **context) -> None:
        """Log debug message"""
        self.log(LogLevel.DEBUG, category, message, **context)
    
    def info(self, message: str, category: LogCategory = LogCategory.SYSTEM, **context) -> None:
        """Log info message"""
        self.log(LogLevel.INFO, category, message, **context)
    
    def warning(self, message: str, category: LogCategory = LogCategory.SYSTEM, **context) -> None:
        """Log warning message"""
        self.log(LogLevel.WARNING, category, message, **context)
    
    def error(self, message: str, category: LogCategory = LogCategory.SYSTEM, **context) -> None:
        """Log error message"""
        # Include stack trace for errors
        entry = LogEntry(
            timestamp=time.time(),
            level=LogLevel.ERROR,
            category=category,
            message=message,
            context=context,
            stack_trace=traceback.format_exc(),
            thread_id=threading.get_ident(),
            process_id=os.getpid(),
        )
        
        for handler in self.handlers:
            try:
                handler.handle(entry)
            except Exception as e:
                print(f"Error in log handler: {e}", file=sys.stderr)
    
    def critical(self, message: str, category: LogCategory = LogCategory.SYSTEM, **context) -> None:
        """Log critical message"""
        entry = LogEntry(
            timestamp=time.time(),
            level=LogLevel.CRITICAL,
            category=category,
            message=message,
            context=context,
            stack_trace=traceback.format_exc(),
            thread_id=threading.get_ident(),
            process_id=os.getpid(),
        )
        
        for handler in self.handlers:
            try:
                handler.handle(entry)
            except Exception as e:
                print(f"Error in log handler: {e}", file=sys.stderr)
    
    def exception(self, message: str, category: LogCategory = LogCategory.SYSTEM, **context) -> None:
        """Log exception with traceback"""
        self.error(message, category, **context)


# =============================================================================
# METRICS COLLECTOR
# =============================================================================

@dataclass
class Metric:
    """Performance metric"""
    name: str
    value: float
    unit: str
    timestamp: float
    tags: Dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    """Collects and aggregates performance metrics"""
    
    def __init__(self):
        """Initialize metrics collector"""
        self.metrics: Dict[str, List[Metric]] = defaultdict(list)
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = {}
        self.timers: Dict[str, List[float]] = defaultdict(list)
    
    def record_metric(self, metric: Metric) -> None:
        """Record a metric"""
        self.metrics[metric.name].append(metric)
    
    def increment_counter(self, name: str, value: int = 1, **tags) -> None:
        """Increment a counter"""
        key = self._make_key(name, tags)
        self.counters[key] += value
    
    def set_gauge(self, name: str, value: float, **tags) -> None:
        """Set a gauge value"""
        key = self._make_key(name, tags)
        self.gauges[key] = value
    
    def record_timer(self, name: str, duration: float, **tags) -> None:
        """Record a timing"""
        key = self._make_key(name, tags)
        self.timers[key].append(duration)
    
    def get_counter(self, name: str, **tags) -> int:
        """Get counter value"""
        key = self._make_key(name, tags)
        return self.counters.get(key, 0)
    
    def get_gauge(self, name: str, **tags) -> Optional[float]:
        """Get gauge value"""
        key = self._make_key(name, tags)
        return self.gauges.get(key)
    
    def get_timer_stats(self, name: str, **tags) -> Optional[Dict[str, float]]:
        """Get timer statistics"""
        key = self._make_key(name, tags)
        timings = self.timers.get(key)
        
        if not timings:
            return None
        
        return {
            'count': len(timings),
            'sum': sum(timings),
            'mean': sum(timings) / len(timings),
            'min': min(timings),
            'max': max(timings),
        }
    
    def _make_key(self, name: str, tags: Dict[str, str]) -> str:
        """Make key from name and tags"""
        if not tags:
            return name
        
        tag_str = ','.join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}[{tag_str}]"
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics"""
        return {
            'counters': dict(self.counters),
            'gauges': dict(self.gauges),
            'timers': {
                name: self.get_timer_stats(name.split('[')[0])
                for name in self.timers.keys()
            },
        }
    
    def reset(self) -> None:
        """Reset all metrics"""
        self.metrics.clear()
        self.counters.clear()
        self.gauges.clear()
        self.timers.clear()


# =============================================================================
# MONITORING SYSTEM
# =============================================================================

class Monitor:
    """System monitoring and health checks"""
    
    def __init__(self):
        """Initialize monitor"""
        self.start_time = time.time()
        self.metrics = MetricsCollector()
        self.health_checks: Dict[str, Callable[[], bool]] = {}
    
    def register_health_check(self, name: str, check_func: Callable[[], bool]) -> None:
        """Register a health check function"""
        self.health_checks[name] = check_func
    
    def check_health(self) -> Dict[str, bool]:
        """Run all health checks"""
        results = {}
        
        for name, check_func in self.health_checks.items():
            try:
                results[name] = check_func()
            except Exception as e:
                results[name] = False
        
        return results
    
    def is_healthy(self) -> bool:
        """Check if system is healthy"""
        results = self.check_health()
        return all(results.values())
    
    def get_uptime(self) -> float:
        """Get system uptime in seconds"""
        return time.time() - self.start_time
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        return {
            'uptime': self.get_uptime(),
            'healthy': self.is_healthy(),
            'health_checks': self.check_health(),
            'metrics': self.metrics.get_all_metrics(),
        }


# =============================================================================
# EVENT TRACKER
# =============================================================================

@dataclass
class Event:
    """System event"""
    name: str
    timestamp: float
    category: str
    data: Dict[str, Any] = field(default_factory=dict)


class EventTracker:
    """Tracks system events for analytics"""
    
    def __init__(self, max_events: int = 10000):
        """Initialize event tracker"""
        self.max_events = max_events
        self.events: deque = deque(maxlen=max_events)
        self.event_counts: Dict[str, int] = defaultdict(int)
    
    def track(self, name: str, category: str = "general", **data) -> None:
        """Track an event"""
        event = Event(
            name=name,
            timestamp=time.time(),
            category=category,
            data=data
        )
        
        self.events.append(event)
        self.event_counts[name] += 1
    
    def get_events(
        self,
        name: Optional[str] = None,
        category: Optional[str] = None,
        since: Optional[float] = None,
        limit: Optional[int] = None
    ) -> List[Event]:
        """Get tracked events with filtering"""
        events = list(self.events)
        
        if name:
            events = [e for e in events if e.name == name]
        
        if category:
            events = [e for e in events if e.category == category]
        
        if since:
            events = [e for e in events if e.timestamp >= since]
        
        if limit:
            events = events[-limit:]
        
        return events
    
    def get_event_count(self, name: str) -> int:
        """Get count for specific event"""
        return self.event_counts.get(name, 0)
    
    def get_all_counts(self) -> Dict[str, int]:
        """Get counts for all events"""
        return dict(self.event_counts)


# =============================================================================
# GLOBAL LOGGER INSTANCE
# =============================================================================

_global_logger: Optional[Logger] = None
_global_monitor: Optional[Monitor] = None
_global_event_tracker: Optional[EventTracker] = None


def get_logger() -> Logger:
    """Get global logger instance"""
    global _global_logger
    
    if _global_logger is None:
        _global_logger = Logger()
        
        # Add console handler
        console = ConsoleHandler(level=LogLevel.INFO)
        _global_logger.add_handler(console)
        
        # Add file handler
        log_dir = Path.home() / '.cache' / 'brad_tui' / 'logs'
        log_file = log_dir / 'brad_tui_ultra.log'
        file_handler = FileHandler(log_file, level=LogLevel.DEBUG)
        _global_logger.add_handler(file_handler)
    
    return _global_logger


def get_monitor() -> Monitor:
    """Get global monitor instance"""
    global _global_monitor
    
    if _global_monitor is None:
        _global_monitor = Monitor()
    
    return _global_monitor


def get_event_tracker() -> EventTracker:
    """Get global event tracker instance"""
    global _global_event_tracker
    
    if _global_event_tracker is None:
        _global_event_tracker = EventTracker()
    
    return _global_event_tracker


# =============================================================================
# MAIN (for testing)
# =============================================================================

if __name__ == "__main__":
    print("Brad TUI Ultra - Logging Module")
    print("=" * 50)
    
    # Create logger
    logger = get_logger()
    
    # Test logging
    logger.debug("Debug message", user_id=123)
    logger.info("Info message", command="ls")
    logger.warning("Warning message", category=LogCategory.UI)
    logger.error("Error message", category=LogCategory.COMMAND)
    
    # Test metrics
    monitor = get_monitor()
    monitor.metrics.increment_counter("commands_executed")
    monitor.metrics.set_gauge("memory_usage", 1024.5, unit="MB")
    monitor.metrics.record_timer("command_duration", 0.123)
    
    print("\nMetrics:")
    print(json.dumps(monitor.get_stats(), indent=2))
    
    # Test events
    tracker = get_event_tracker()
    tracker.track("command_executed", category="command", command="ls")
    tracker.track("key_pressed", category="input", key="Enter")
    
    print(f"\nEvent counts: {tracker.get_all_counts()}")
    
    print("\n✅ Logging module test complete")

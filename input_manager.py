#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        ADVANCED INPUT MANAGER                                ║
║              Keybindings, Text Editing, Command History                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

This module provides comprehensive input handling:
    - Keybinding system with customizable mappings
    - Text editing with full cursor movement
    - Command history with search
    - Multi-key sequences (chords)
    - Macro recording and playback
    - Clipboard operations
    - Undo/redo support
"""

import re
from typing import Dict, List, Optional, Callable, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import deque


# ═══════════════════════════════════════════════════════════════════════════════
# KEY DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════════

class KeyModifier(Enum):
    """Key modifier flags"""
    NONE = 0
    CTRL = 1
    ALT = 2
    SHIFT = 4
    META = 8


@dataclass
class KeyPress:
    """Represents a key press event"""
    key: str
    modifiers: int = 0
    
    def __hash__(self):
        return hash((self.key, self.modifiers))
    
    def __eq__(self, other):
        return self.key == other.key and self.modifiers == other.modifiers
    
    def __str__(self):
        parts = []
        if self.modifiers & KeyModifier.CTRL.value:
            parts.append("Ctrl")
        if self.modifiers & KeyModifier.ALT.value:
            parts.append("Alt")
        if self.modifiers & KeyModifier.SHIFT.value:
            parts.append("Shift")
        if self.modifiers & KeyModifier.META.value:
            parts.append("Meta")
        parts.append(self.key)
        return "+".join(parts)


class KeyParser:
    """Parse raw terminal input into KeyPress objects"""
    
    # Control character mappings
    CTRL_CHARS = {
        '\x01': ('a', KeyModifier.CTRL.value),
        '\x02': ('b', KeyModifier.CTRL.value),
        '\x03': ('c', KeyModifier.CTRL.value),
        '\x04': ('d', KeyModifier.CTRL.value),
        '\x05': ('e', KeyModifier.CTRL.value),
        '\x06': ('f', KeyModifier.CTRL.value),
        '\x07': ('g', KeyModifier.CTRL.value),
        '\x08': ('h', KeyModifier.CTRL.value),  # Backspace
        '\x09': ('i', KeyModifier.CTRL.value),  # Tab
        '\x0a': ('j', KeyModifier.CTRL.value),  # Enter
        '\x0b': ('k', KeyModifier.CTRL.value),
        '\x0c': ('l', KeyModifier.CTRL.value),
        '\x0d': ('m', KeyModifier.CTRL.value),
        '\x0e': ('n', KeyModifier.CTRL.value),
        '\x0f': ('o', KeyModifier.CTRL.value),
        '\x10': ('p', KeyModifier.CTRL.value),
        '\x11': ('q', KeyModifier.CTRL.value),
        '\x12': ('r', KeyModifier.CTRL.value),
        '\x13': ('s', KeyModifier.CTRL.value),
        '\x14': ('t', KeyModifier.CTRL.value),
        '\x15': ('u', KeyModifier.CTRL.value),
        '\x16': ('v', KeyModifier.CTRL.value),
        '\x17': ('w', KeyModifier.CTRL.value),
        '\x18': ('x', KeyModifier.CTRL.value),
        '\x19': ('y', KeyModifier.CTRL.value),
        '\x1a': ('z', KeyModifier.CTRL.value),
        '\x7f': ('BACKSPACE', KeyModifier.NONE.value),
    }
    
    # Special key names
    SPECIAL_KEYS = {
        'KEY_UP': 'UP',
        'KEY_DOWN': 'DOWN',
        'KEY_LEFT': 'LEFT',
        'KEY_RIGHT': 'RIGHT',
        'KEY_HOME': 'HOME',
        'KEY_END': 'END',
        'KEY_PAGEUP': 'PAGEUP',
        'KEY_PAGEDOWN': 'PAGEDOWN',
        'KEY_DELETE': 'DELETE',
        'KEY_INSERT': 'INSERT',
        'KEY_F1': 'F1',
        'KEY_F2': 'F2',
        'KEY_F3': 'F3',
        'KEY_F4': 'F4',
        'KEY_F5': 'F5',
        'KEY_F6': 'F6',
        'KEY_F7': 'F7',
        'KEY_F8': 'F8',
        'KEY_F9': 'F9',
        'KEY_F10': 'F10',
        'KEY_F11': 'F11',
        'KEY_F12': 'F12',
    }
    
    @classmethod
    def parse(cls, raw_key: str) -> KeyPress:
        """Parse raw key input into KeyPress"""
        # Check for control characters
        if raw_key in cls.CTRL_CHARS:
            key, mods = cls.CTRL_CHARS[raw_key]
            return KeyPress(key, mods)
        
        # Check for special keys
        if raw_key in cls.SPECIAL_KEYS:
            return KeyPress(cls.SPECIAL_KEYS[raw_key], KeyModifier.NONE.value)
        
        # Tab is special
        if raw_key == '\t':
            return KeyPress('TAB', KeyModifier.NONE.value)
        
        # Enter/Return
        if raw_key == '\n' or raw_key == '\r':
            return KeyPress('ENTER', KeyModifier.NONE.value)
        
        # Escape
        if raw_key == '\x1b':
            return KeyPress('ESC', KeyModifier.NONE.value)
        
        # Space
        if raw_key == ' ':
            return KeyPress('SPACE', KeyModifier.NONE.value)
        
        # Regular character
        if len(raw_key) == 1 and raw_key.isprintable():
            return KeyPress(raw_key, KeyModifier.NONE.value)
        
        # Unknown key
        return KeyPress('UNKNOWN', KeyModifier.NONE.value)


# ═══════════════════════════════════════════════════════════════════════════════
# KEYBINDING SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class KeyBinding:
    """A keybinding mapping"""
    keys: List[KeyPress]  # Support for chord sequences
    action: Callable[[], bool]  # Return True if handled
    description: str = ""
    enabled: bool = True


class KeyBindingManager:
    """Manages keybindings and dispatches actions"""
    
    def __init__(self):
        self.bindings: Dict[str, KeyBinding] = {}
        self.chord_buffer: List[KeyPress] = []
        self.chord_timeout = 1.0  # Seconds
        self.last_key_time = 0.0
        
    def bind(self, key_sequence: str, action: Callable[[], bool], 
             description: str = "") -> str:
        """
        Bind a key sequence to an action.
        
        Examples:
            "Ctrl+c" - Single key with modifier
            "Ctrl+x Ctrl+s" - Key chord (sequence)
            "Alt+Shift+f" - Multiple modifiers
        
        Returns binding ID
        """
        keys = self._parse_key_sequence(key_sequence)
        binding_id = key_sequence
        
        self.bindings[binding_id] = KeyBinding(
            keys=keys,
            action=action,
            description=description
        )
        
        return binding_id
    
    def unbind(self, binding_id: str):
        """Remove a keybinding"""
        if binding_id in self.bindings:
            del self.bindings[binding_id]
    
    def _parse_key_sequence(self, sequence: str) -> List[KeyPress]:
        """Parse key sequence string into list of KeyPress"""
        chords = sequence.split()
        result = []
        
        for chord in chords:
            parts = chord.split('+')
            
            # Parse modifiers
            modifiers = 0
            key = parts[-1]
            
            for part in parts[:-1]:
                part_lower = part.lower()
                if part_lower == 'ctrl':
                    modifiers |= KeyModifier.CTRL.value
                elif part_lower == 'alt':
                    modifiers |= KeyModifier.ALT.value
                elif part_lower == 'shift':
                    modifiers |= KeyModifier.SHIFT.value
                elif part_lower == 'meta':
                    modifiers |= KeyModifier.META.value
            
            result.append(KeyPress(key, modifiers))
        
        return result
    
    def handle_key(self, raw_key: str, current_time: float) -> bool:
        """
        Handle a key press.
        Returns True if the key was handled by a binding.
        """
        key = KeyParser.parse(raw_key)
        
        # Check chord timeout
        if current_time - self.last_key_time > self.chord_timeout:
            self.chord_buffer.clear()
        
        self.chord_buffer.append(key)
        self.last_key_time = current_time
        
        # Check for matching bindings
        for binding in self.bindings.values():
            if not binding.enabled:
                continue
            
            if self._matches_binding(self.chord_buffer, binding.keys):
                self.chord_buffer.clear()
                return binding.action()
        
        # Check if current buffer could be start of a chord
        if not self._is_potential_chord():
            self.chord_buffer.clear()
        
        return False
    
    def _matches_binding(self, buffer: List[KeyPress], 
                        binding_keys: List[KeyPress]) -> bool:
        """Check if buffer matches binding"""
        if len(buffer) != len(binding_keys):
            return False
        
        for buf_key, bind_key in zip(buffer, binding_keys):
            if buf_key != bind_key:
                return False
        
        return True
    
    def _is_potential_chord(self) -> bool:
        """Check if current buffer could be start of a chord sequence"""
        for binding in self.bindings.values():
            if not binding.enabled:
                continue
            
            # Check if binding starts with current buffer
            if len(binding.keys) >= len(self.chord_buffer):
                matches = True
                for i, key in enumerate(self.chord_buffer):
                    if binding.keys[i] != key:
                        matches = False
                        break
                
                if matches:
                    return True
        
        return False
    
    def get_binding_info(self) -> List[Tuple[str, str]]:
        """Get list of (key_sequence, description) for all bindings"""
        result = []
        for binding_id, binding in self.bindings.items():
            result.append((binding_id, binding.description))
        return sorted(result)


# ═══════════════════════════════════════════════════════════════════════════════
# TEXT BUFFER WITH EDITING
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class EditState:
    """Represents a state in the undo/redo history"""
    text: str
    cursor_pos: int


class TextBuffer:
    """Text buffer with full editing capabilities"""
    
    def __init__(self, text: str = "", max_history: int = 100):
        self.text = text
        self.cursor_pos = len(text)
        
        # Undo/redo
        self.history: deque[EditState] = deque(maxlen=max_history)
        self.history_pos = -1
        self._save_state()
        
        # Clipboard
        self.clipboard = ""
        
        # Selection
        self.selection_start: Optional[int] = None
        self.selection_end: Optional[int] = None
    
    def _save_state(self):
        """Save current state to history"""
        # Remove any states after current position
        while self.history_pos < len(self.history) - 1:
            self.history.pop()
        
        state = EditState(text=self.text, cursor_pos=self.cursor_pos)
        self.history.append(state)
        self.history_pos = len(self.history) - 1
    
    def undo(self) -> bool:
        """Undo last edit"""
        if self.history_pos > 0:
            self.history_pos -= 1
            state = self.history[self.history_pos]
            self.text = state.text
            self.cursor_pos = state.cursor_pos
            return True
        return False
    
    def redo(self) -> bool:
        """Redo edit"""
        if self.history_pos < len(self.history) - 1:
            self.history_pos += 1
            state = self.history[self.history_pos]
            self.text = state.text
            self.cursor_pos = state.cursor_pos
            return True
        return False
    
    def insert(self, char: str):
        """Insert character at cursor"""
        self.text = self.text[:self.cursor_pos] + char + self.text[self.cursor_pos:]
        self.cursor_pos += len(char)
        self._save_state()
    
    def delete_char(self):
        """Delete character at cursor"""
        if self.cursor_pos < len(self.text):
            self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos + 1:]
            self._save_state()
    
    def backspace(self):
        """Delete character before cursor"""
        if self.cursor_pos > 0:
            self.text = self.text[:self.cursor_pos - 1] + self.text[self.cursor_pos:]
            self.cursor_pos -= 1
            self._save_state()
    
    def move_cursor(self, delta: int):
        """Move cursor by delta positions"""
        self.cursor_pos = max(0, min(len(self.text), self.cursor_pos + delta))
    
    def move_to_start(self):
        """Move cursor to start of line"""
        self.cursor_pos = 0
    
    def move_to_end(self):
        """Move cursor to end of line"""
        self.cursor_pos = len(self.text)
    
    def move_word_left(self):
        """Move cursor to start of previous word"""
        if self.cursor_pos == 0:
            return
        
        # Skip whitespace
        while self.cursor_pos > 0 and self.text[self.cursor_pos - 1].isspace():
            self.cursor_pos -= 1
        
        # Skip word characters
        while self.cursor_pos > 0 and not self.text[self.cursor_pos - 1].isspace():
            self.cursor_pos -= 1
    
    def move_word_right(self):
        """Move cursor to start of next word"""
        if self.cursor_pos >= len(self.text):
            return
        
        # Skip word characters
        while self.cursor_pos < len(self.text) and not self.text[self.cursor_pos].isspace():
            self.cursor_pos += 1
        
        # Skip whitespace
        while self.cursor_pos < len(self.text) and self.text[self.cursor_pos].isspace():
            self.cursor_pos += 1
    
    def delete_word(self):
        """Delete word at cursor"""
        start = self.cursor_pos
        self.move_word_right()
        end = self.cursor_pos
        
        if start != end:
            self.text = self.text[:start] + self.text[end:]
            self.cursor_pos = start
            self._save_state()
    
    def delete_to_end(self):
        """Delete from cursor to end of line"""
        if self.cursor_pos < len(self.text):
            self.clipboard = self.text[self.cursor_pos:]
            self.text = self.text[:self.cursor_pos]
            self._save_state()
    
    def delete_to_start(self):
        """Delete from cursor to start of line"""
        if self.cursor_pos > 0:
            self.clipboard = self.text[:self.cursor_pos]
            self.text = self.text[self.cursor_pos:]
            self.cursor_pos = 0
            self._save_state()
    
    def clear(self):
        """Clear all text"""
        self.text = ""
        self.cursor_pos = 0
        self._save_state()
    
    def set_text(self, text: str):
        """Set text content"""
        self.text = text
        self.cursor_pos = len(text)
        self._save_state()
    
    def get_text(self) -> str:
        """Get text content"""
        return self.text


# ═══════════════════════════════════════════════════════════════════════════════
# COMMAND HISTORY
# ═══════════════════════════════════════════════════════════════════════════════

class CommandHistory:
    """Command history with search and navigation"""
    
    def __init__(self, max_size: int = 1000):
        self.history: deque[str] = deque(maxlen=max_size)
        self.position = -1  # -1 means at end (new command)
        self.search_mode = False
        self.search_term = ""
        self.temp_command = ""  # Store current command when navigating history
    
    def add(self, command: str):
        """Add command to history"""
        if command and (not self.history or self.history[-1] != command):
            self.history.append(command)
        self.reset_navigation()
    
    def reset_navigation(self):
        """Reset to end of history"""
        self.position = -1
        self.temp_command = ""
    
    def navigate_up(self) -> Optional[str]:
        """Navigate to previous command"""
        if not self.history:
            return None
        
        if self.position == -1:
            # Store current command
            self.position = len(self.history) - 1
        elif self.position > 0:
            self.position -= 1
        
        return self.history[self.position] if self.position >= 0 else None
    
    def navigate_down(self) -> Optional[str]:
        """Navigate to next command"""
        if self.position == -1:
            return None
        
        self.position += 1
        
        if self.position >= len(self.history):
            result = self.temp_command
            self.reset_navigation()
            return result
        
        return self.history[self.position]
    
    def search(self, term: str) -> List[str]:
        """Search history for commands matching term"""
        if not term:
            return list(self.history)
        
        results = []
        for cmd in reversed(self.history):
            if term.lower() in cmd.lower():
                results.append(cmd)
        
        return results
    
    def get_all(self) -> List[str]:
        """Get all history entries"""
        return list(self.history)
    
    def clear(self):
        """Clear all history"""
        self.history.clear()
        self.reset_navigation()


# ═══════════════════════════════════════════════════════════════════════════════
# AUTOCOMPLETE ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class AutocompleteEngine:
    """Fuzzy autocomplete with scoring"""
    
    def __init__(self):
        self.suggestions: List[str] = []
        self.max_results = 10
    
    def set_suggestions(self, suggestions: List[str]):
        """Set available suggestions"""
        self.suggestions = list(set(suggestions))  # Remove duplicates
    
    def add_suggestion(self, suggestion: str):
        """Add a single suggestion"""
        if suggestion not in self.suggestions:
            self.suggestions.append(suggestion)
    
    def get_completions(self, prefix: str, max_results: Optional[int] = None) -> List[Tuple[str, float]]:
        """
        Get completions for prefix with relevance scores.
        Returns list of (suggestion, score) tuples sorted by score (descending).
        """
        if not prefix:
            return []
        
        results = []
        prefix_lower = prefix.lower()
        
        for suggestion in self.suggestions:
            score = self._calculate_score(prefix_lower, suggestion.lower())
            if score > 0:
                results.append((suggestion, score))
        
        # Sort by score (descending)
        results.sort(key=lambda x: x[1], reverse=True)
        
        # Limit results
        limit = max_results or self.max_results
        return results[:limit]
    
    def _calculate_score(self, prefix: str, text: str) -> float:
        """Calculate relevance score for text given prefix"""
        if not prefix or not text:
            return 0.0
        
        # Exact match
        if text == prefix:
            return 1.0
        
        # Starts with prefix (high score)
        if text.startswith(prefix):
            return 0.9
        
        # Contains prefix as substring
        if prefix in text:
            # Score based on position
            pos = text.index(prefix)
            position_factor = 1.0 - (pos / len(text))
            return 0.7 * position_factor
        
        # Fuzzy match (subsequence)
        if self._is_subsequence(prefix, text):
            # Calculate how closely matched
            ratio = len(prefix) / len(text)
            return 0.5 * ratio
        
        return 0.0
    
    def _is_subsequence(self, subseq: str, text: str) -> bool:
        """Check if subseq is a subsequence of text"""
        it = iter(text)
        return all(char in it for char in subseq)


# ═══════════════════════════════════════════════════════════════════════════════
# INPUT CONTEXT MANAGER
# ═══════════════════════════════════════════════════════════════════════════════

class InputContext:
    """
    High-level input manager combining all input systems.
    Manages text editing, history, keybindings, and autocomplete.
    """
    
    def __init__(self):
        self.text_buffer = TextBuffer()
        self.history = CommandHistory()
        self.keybindings = KeyBindingManager()
        self.autocomplete = AutocompleteEngine()
        
        # Callbacks
        self.on_submit: Optional[Callable[[str], None]] = None
        self.on_change: Optional[Callable[[str], None]] = None
        self.on_autocomplete_request: Optional[Callable[[], None]] = None
        
        # State
        self.in_history_navigation = False
        
        # Setup default keybindings
        self._setup_default_bindings()
    
    def _setup_default_bindings(self):
        """Setup default keybindings"""
        # Navigation
        self.keybindings.bind("LEFT", lambda: self._move_cursor(-1), "Move cursor left")
        self.keybindings.bind("RIGHT", lambda: self._move_cursor(1), "Move cursor right")
        self.keybindings.bind("HOME", lambda: self._move_to_start(), "Move to start")
        self.keybindings.bind("END", lambda: self._move_to_end(), "Move to end")
        self.keybindings.bind("Ctrl+a", lambda: self._move_to_start(), "Move to start")
        self.keybindings.bind("Ctrl+e", lambda: self._move_to_end(), "Move to end")
        
        # Word movement
        self.keybindings.bind("Ctrl+LEFT", lambda: self._move_word_left(), "Move word left")
        self.keybindings.bind("Ctrl+RIGHT", lambda: self._move_word_right(), "Move word right")
        
        # Editing
        self.keybindings.bind("BACKSPACE", lambda: self._backspace(), "Delete character before cursor")
        self.keybindings.bind("DELETE", lambda: self._delete(), "Delete character at cursor")
        self.keybindings.bind("Ctrl+d", lambda: self._delete(), "Delete character at cursor")
        self.keybindings.bind("Ctrl+h", lambda: self._backspace(), "Delete character before cursor")
        self.keybindings.bind("Ctrl+w", lambda: self._delete_word(), "Delete word before cursor")
        self.keybindings.bind("Ctrl+k", lambda: self._delete_to_end(), "Delete to end of line")
        self.keybindings.bind("Ctrl+u", lambda: self._delete_to_start(), "Delete to start of line")
        
        # History
        self.keybindings.bind("UP", lambda: self._history_prev(), "Previous command")
        self.keybindings.bind("DOWN", lambda: self._history_next(), "Next command")
        self.keybindings.bind("Ctrl+p", lambda: self._history_prev(), "Previous command")
        self.keybindings.bind("Ctrl+n", lambda: self._history_next(), "Next command")
        
        # Undo/Redo
        self.keybindings.bind("Ctrl+z", lambda: self._undo(), "Undo")
        self.keybindings.bind("Ctrl+y", lambda: self._redo(), "Redo")
        
        # Autocomplete
        self.keybindings.bind("TAB", lambda: self._request_autocomplete(), "Autocomplete")
        
        # Submit
        self.keybindings.bind("ENTER", lambda: self._submit(), "Submit command")
        
        # Clear
        self.keybindings.bind("Ctrl+l", lambda: self._clear(), "Clear line")
    
    def handle_key(self, raw_key: str, current_time: float) -> bool:
        """Handle a key press"""
        import time as time_module
        
        # Try keybindings first
        if self.keybindings.handle_key(raw_key, current_time):
            return True
        
        # Regular character input
        key = KeyParser.parse(raw_key)
        if len(key.key) == 1 and key.key.isprintable() and key.modifiers == 0:
            self.text_buffer.insert(key.key)
            self.in_history_navigation = False
            if self.on_change:
                self.on_change(self.text_buffer.get_text())
            return True
        
        return False
    
    # Action methods
    def _move_cursor(self, delta: int) -> bool:
        self.text_buffer.move_cursor(delta)
        return True
    
    def _move_to_start(self) -> bool:
        self.text_buffer.move_to_start()
        return True
    
    def _move_to_end(self) -> bool:
        self.text_buffer.move_to_end()
        return True
    
    def _move_word_left(self) -> bool:
        self.text_buffer.move_word_left()
        return True
    
    def _move_word_right(self) -> bool:
        self.text_buffer.move_word_right()
        return True
    
    def _backspace(self) -> bool:
        self.text_buffer.backspace()
        if self.on_change:
            self.on_change(self.text_buffer.get_text())
        return True
    
    def _delete(self) -> bool:
        self.text_buffer.delete_char()
        if self.on_change:
            self.on_change(self.text_buffer.get_text())
        return True
    
    def _delete_word(self) -> bool:
        self.text_buffer.delete_word()
        if self.on_change:
            self.on_change(self.text_buffer.get_text())
        return True
    
    def _delete_to_end(self) -> bool:
        self.text_buffer.delete_to_end()
        if self.on_change:
            self.on_change(self.text_buffer.get_text())
        return True
    
    def _delete_to_start(self) -> bool:
        self.text_buffer.delete_to_start()
        if self.on_change:
            self.on_change(self.text_buffer.get_text())
        return True
    
    def _history_prev(self) -> bool:
        if not self.in_history_navigation:
            self.history.temp_command = self.text_buffer.get_text()
            self.in_history_navigation = True
        
        cmd = self.history.navigate_up()
        if cmd is not None:
            self.text_buffer.set_text(cmd)
            if self.on_change:
                self.on_change(cmd)
        return True
    
    def _history_next(self) -> bool:
        cmd = self.history.navigate_down()
        if cmd is not None:
            self.text_buffer.set_text(cmd)
            if self.on_change:
                self.on_change(cmd)
        
        if self.history.position == -1:
            self.in_history_navigation = False
        
        return True
    
    def _undo(self) -> bool:
        self.text_buffer.undo()
        if self.on_change:
            self.on_change(self.text_buffer.get_text())
        return True
    
    def _redo(self) -> bool:
        self.text_buffer.redo()
        if self.on_change:
            self.on_change(self.text_buffer.get_text())
        return True
    
    def _request_autocomplete(self) -> bool:
        if self.on_autocomplete_request:
            self.on_autocomplete_request()
        return True
    
    def _submit(self) -> bool:
        text = self.text_buffer.get_text()
        if text.strip():
            self.history.add(text)
            if self.on_submit:
                self.on_submit(text)
        self.text_buffer.clear()
        self.in_history_navigation = False
        return True
    
    def _clear(self) -> bool:
        self.text_buffer.clear()
        if self.on_change:
            self.on_change("")
        return True
    
    def get_text(self) -> str:
        """Get current text"""
        return self.text_buffer.get_text()
    
    def get_cursor_pos(self) -> int:
        """Get cursor position"""
        return self.text_buffer.cursor_pos
    
    def set_text(self, text: str):
        """Set text"""
        self.text_buffer.set_text(text)


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    'KeyModifier', 'KeyPress', 'KeyParser',
    'KeyBinding', 'KeyBindingManager',
    'TextBuffer', 'EditState',
    'CommandHistory',
    'AutocompleteEngine',
    'InputContext',
]

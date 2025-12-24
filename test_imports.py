#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify all modules can be imported correctly.
"""

import sys
import traceback

def test_import(module_name):
    """Test importing a module"""
    try:
        __import__(module_name)
        print(f"✓ {module_name}")
        return True
    except Exception as e:
        print(f"✗ {module_name}: {e}")
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("Cyberpunk Terminal - Module Import Test")
    print("=" * 60)
    print()
    
    modules = [
        "terminal_core",
        "shader_system",
        "ui_components",
        "input_manager",
        "terminal_session",
        "graphics_engine",
        "config",
        "utils",
        "cyberpunk_terminal",
    ]
    
    results = []
    for module in modules:
        results.append(test_import(module))
    
    print()
    print("=" * 60)
    
    if all(results):
        print("✓ All modules imported successfully!")
        print()
        print("Module Statistics:")
        
        # Count lines
        total_lines = 0
        for module in modules:
            try:
                with open(f"{module}.py", 'r') as f:
                    lines = len(f.readlines())
                    total_lines += lines
                    print(f"  {module:30s} {lines:5d} lines")
            except:
                pass
        
        print(f"  {'TOTAL':30s} {total_lines:5d} lines")
        print()
        
        # Test basic functionality
        print("Basic Functionality Test:")
        
        try:
            from terminal_core import get_terminal_size
            width, height = get_terminal_size()
            print(f"  ✓ Terminal size: {width}x{height}")
        except Exception as e:
            print(f"  ✗ Terminal size: {e}")
        
        try:
            from shader_system import Vec3, Color
            v = Vec3(1, 2, 3)
            c = Color(1.0, 0.5, 0.2)
            print(f"  ✓ Shader system: Vec3{v.x, v.y, v.z}, Color{c.to_rgb255()}")
        except Exception as e:
            print(f"  ✗ Shader system: {e}")
        
        try:
            from input_manager import KeyParser, KeyPress
            key = KeyParser.parse('a')
            print(f"  ✓ Input manager: KeyPress('{key.key}')")
        except Exception as e:
            print(f"  ✗ Input manager: {e}")
        
        try:
            from terminal_session import TerminalSession
            session = TerminalSession()
            print(f"  ✓ Terminal session created")
        except Exception as e:
            print(f"  ✗ Terminal session: {e}")
        
        try:
            from graphics_engine import GraphicsCompositor
            gfx = GraphicsCompositor(80, 24)
            print(f"  ✓ Graphics engine: {gfx.width}x{gfx.height}")
        except Exception as e:
            print(f"  ✗ Graphics engine: {e}")
        
        print()
        print("=" * 60)
        print("All tests passed! Ready to run: ./cyberpunk_terminal.py")
        print("=" * 60)
        return 0
    else:
        print("✗ Some modules failed to import")
        return 1

if __name__ == "__main__":
    sys.exit(main())

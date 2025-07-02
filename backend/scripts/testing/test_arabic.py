#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test Arabic text rendering"""

import sys
import json

def test_arabic():
    print("🔍 Testing Arabic Text Rendering")
    print("=" * 40)
    
    # Test direct Arabic
    print("\n1. Direct Arabic text:")
    print("   مرحبا بكم في الكويت")
    
    # Test from variable
    arabic_text = "مطعم لبناني في السالمية"
    print("\n2. Arabic from variable:")
    print(f"   {arabic_text}")
    
    # Test JSON encoding/decoding
    data = {
        "english": "Lebanese Restaurant",
        "arabic": "مطعم لبناني",
        "location": "السالمية"
    }
    
    print("\n3. Arabic in JSON:")
    print(f"   {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    # Test encoding info
    print("\n4. System encoding info:")
    print(f"   stdout encoding: {sys.stdout.encoding}")
    print(f"   filesystem encoding: {sys.getfilesystemencoding()}")
    print(f"   default encoding: {sys.getdefaultencoding()}")
    
    # Test with arabic-reshaper
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
        
        text = "مرحبا بكم في مطعم بيت بيروت"
        reshaped = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped)
        
        print("\n5. With arabic-reshaper:")
        print(f"   Original: {text}")
        print(f"   Reshaped: {reshaped}")
        print(f"   Bidi: {bidi_text}")
    except ImportError:
        print("\n5. arabic-reshaper not installed")

if __name__ == "__main__":
    test_arabic()
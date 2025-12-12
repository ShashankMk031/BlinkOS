#!/usr/bin/env python3
"""
Quick setup verification script
"""

def test_imports():
    print("Testing imports...")
    
    try:
        import cv2
        print(f"✓ OpenCV {cv2.__version__}")
    except ImportError as e:
        print(f"✗ OpenCV failed: {e}")
    
    try:
        import mediapipe as mp
        print(f"✓ MediaPipe {mp.__version__}")
    except ImportError as e:
        print(f"✗ MediaPipe failed: {e}")
    
    try:
        import pyautogui
        print(f"✓ PyAutoGUI {pyautogui.__version__}")
    except ImportError as e:
        print(f"✗ PyAutoGUI failed: {e}")
    
    try:
        import speech_recognition as sr
        print(f"✓ SpeechRecognition {sr.__version__}")
    except ImportError as e:
        print(f"✗ SpeechRecognition failed: {e}")
    
    try:
        import pyttsx3
        print("✓ pyttsx3")
    except ImportError as e:
        print(f"✗ pyttsx3 failed: {e}")
    
    try:
        import numpy as np
        print(f"✓ NumPy {np.__version__}")
    except ImportError as e:
        print(f"✗ NumPy failed: {e}")
    
    print("\n" + "="*50)

def test_camera():
    print("Testing camera access...")
    import cv2
    
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        print("✓ Camera accessible")
        ret, frame = cap.read()
        if ret:
            print(f"✓ Camera frame captured: {frame.shape}")
        cap.release()
    else:
        print("✗ Camera not accessible - Check permissions!")
    
    print("="*50)

def test_microphone():
    print("Testing microphone access...")
    import speech_recognition as sr
    
    try:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("✓ Microphone accessible")
    except Exception as e:
        print(f"✗ Microphone error: {e}")
        print("  Check permissions in System Settings!")
    
    print("="*50)

if __name__ == "__main__":
    print("BlinkOS - Setup Verification\n")
    test_imports()
    test_camera()
    test_microphone()
    print("\nSetup verification complete!")
    print("\nIf everything shows [OK], you're ready to start coding!")
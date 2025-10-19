#!/usr/bin/env python3
"""
Script to trigger camera and microphone permission requests
"""

print("🎥 Testing Camera Access...")
print("You should see a permission popup - click ALLOW/OK\n")

try:
    import cv2
    cap = cv2.VideoCapture(0)
    
    if cap.isOpened():
        print("✅ Camera permission granted!")
        ret, frame = cap.read()
        if ret:
            print(f"✅ Successfully captured frame: {frame.shape}")
            # Show the frame briefly
            cv2.imshow('Camera Test - Press any key to close', frame)
            cv2.waitKey(2000)  # Wait 2 seconds
            cv2.destroyAllWindows()
        cap.release()
    else:
        print("❌ Camera access denied or not available")
        print("   Go to: System Settings > Privacy & Security > Camera")
        print("   Then turn ON the toggle for Terminal/VS Code")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*50 + "\n")

print("🎤 Testing Microphone Access...")
print("You should see a permission popup - click ALLOW/OK\n")

try:
    import speech_recognition as sr
    
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("✅ Microphone permission granted!")
        print("✅ Microphone is accessible")
        
except Exception as e:
    print(f"❌ Microphone error: {e}")
    print("   Go to: System Settings > Privacy & Security > Microphone")
    print("   Then turn ON the toggle for Terminal/VS Code")

print("\n✨ Permission test complete!")
print("\nNow check System Settings - Terminal/VS Code should appear in the lists.")

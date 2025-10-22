#!/usr/bin/env python3
"""
Eye Tracker Module - Day 3 Complete
Optimized head tracking + blink-to-click
"""

import cv2
import mediapipe as mp
import pyautogui
import numpy as np
from collections import deque
import time
import platform
import subprocess
import os


class EyeTracker:
    
    def __init__(self):
        """Initialize the eye tracker"""
        # MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            static_image_mode=False
        )
        
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Screen dimensions
        self.screen_w, self.screen_h = pyautogui.size()
        print(f"Screen resolution: {self.screen_w}x{self.screen_h}")
        
        # Camera setup
        self.cam = cv2.VideoCapture(0)
        if not self.cam.isOpened():
            raise Exception("Cannot open camera!")
        
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        self.cam_w = int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.cam_h = int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"Camera resolution: {self.cam_w}x{self.cam_h}")
        
        # Face landmarks
        self.NOSE_TIP = 1
        self.RIGHT_EYE = [33, 160, 158, 133, 153, 144]
        self.LEFT_EYE = [362, 385, 387, 263, 373, 380]
        
        # Calibration mode
        self.is_calibrated = False
        self.calibration_samples = []
        self.calibration_mode = False
        self.screen_margin_x = 0.25  # 25% margin on sides
        self.screen_margin_y = 0.20  # 20% margin top/bottom
        
        # FPS
        self.prev_time = 0
        
        # AGGRESSIVE SMOOTHING for stable cursor
        self.smooth_buffer_size = 15  # Increased from 7
        self.gaze_buffer_x = deque(maxlen=self.smooth_buffer_size)
        self.gaze_buffer_y = deque(maxlen=self.smooth_buffer_size)
        
        # Blink detection
        self.blink_threshold = 0.20
        self.blink_counter = 0
        self.blink_frames_required = 3
        
        # Click control
        self.click_enabled = True
        self.last_click_time = 0
        self.click_cooldown = 1.0  # 1 second between clicks
        self.click_count = 0
        self.safe_zone_margin = 50
        
        # Frame counter
        self._frame_count = 0
        
        # PyAutoGUI settings
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0
        
        # Audio feedback
        self.audio_feedback = True
        self.use_sound_effects = False
        
        try:
            self.sound_click = "/System/Library/Sounds/Tink.aiff"
            self.sound_error = "/System/Library/Sounds/Basso.aiff"
            
            if os.path.exists(self.sound_click):
                self.use_sound_effects = True
                print("Sound effects enabled")
        except:
            pass
        
        # Quartz for macOS
        self.use_quartz = platform.system() == 'Darwin'
        if self.use_quartz:
            try:
                from Quartz import (CGEventCreateMouseEvent, CGEventPost, 
                                  kCGEventMouseMoved, kCGHIDEventTap, 
                                  CGEventSourceCreate, kCGEventSourceStateHIDSystemState)
                self.CGEventCreateMouseEvent = CGEventCreateMouseEvent
                self.CGEventPost = CGEventPost
                self.kCGEventMouseMoved = kCGEventMouseMoved
                self.kCGHIDEventTap = kCGHIDEventTap
                self.event_source = CGEventSourceCreate(kCGEventSourceStateHIDSystemState)
                print("Using Quartz for cursor control")
            except Exception as e:
                self.use_quartz = False
        
        print("Eye Tracker initialized!")
        print("\nTIP: For best control, move your HEAD to control the cursor")
        print("   Keep your head ~50cm from camera, well-lit from front\n")
    
    def get_face_position(self, landmarks):
        """Get face position using nose tip"""
        nose = landmarks[self.NOSE_TIP]
        return nose.x, nose.y
    
    def calculate_ear(self, landmarks, eye_indices):
        """Calculate Eye Aspect Ratio for blink detection"""
        points = np.array([[landmarks[i].x, landmarks[i].y, landmarks[i].z] for i in eye_indices])
        
        v1 = np.linalg.norm(points[1] - points[5])
        v2 = np.linalg.norm(points[2] - points[4])
        h = np.linalg.norm(points[0] - points[3])
        
        ear = (v1 + v2) / (2.0 * h + 0.0001)
        return ear
    
    def adjust_blink_threshold(self, current_ear):
        """Auto-adjust blink threshold"""
        if not hasattr(self, '_ear_baseline_samples'):
            self._ear_baseline_samples = []
        
        if current_ear > 0.2:
            self._ear_baseline_samples.append(current_ear)
            
            if len(self._ear_baseline_samples) == 30:
                baseline_ear = np.mean(self._ear_baseline_samples)
                self.blink_threshold = baseline_ear * 0.6
                print(f"Blink threshold: {self.blink_threshold:.3f}")
    
    def map_to_screen(self, face_x, face_y):
        """
        Map face position to screen coordinates
        Uses margins to give more control range
        """
        # Apply margins (you need to move head less for full screen range)
        norm_x = (face_x - self.screen_margin_x) / (1 - 2 * self.screen_margin_x)
        norm_y = (face_y - self.screen_margin_y) / (1 - 2 * self.screen_margin_y)
        
        # Clamp to 0-1
        norm_x = max(0, min(1, norm_x))
        norm_y = max(0, min(1, norm_y))
        
        # Map to screen
        screen_x = int(norm_x * self.screen_w)
        screen_y = int(norm_y * self.screen_h)
        
        return screen_x, screen_y
    
    def smooth_gaze(self, x, y):
        """
        Apply HEAVY smoothing for stable cursor
        Uses larger buffer for smoother movement
        """
        self.gaze_buffer_x.append(x)
        self.gaze_buffer_y.append(y)
        
        # Use weighted average (recent positions weighted more)
        weights = np.linspace(0.5, 1.0, len(self.gaze_buffer_x))
        
        smooth_x = int(np.average(self.gaze_buffer_x, weights=weights))
        smooth_y = int(np.average(self.gaze_buffer_y, weights=weights))
        
        return smooth_x, smooth_y
    
    def move_cursor_fast(self, x, y):
        """Fast cursor movement"""
        if self.use_quartz:
            try:
                mouse_event = self.CGEventCreateMouseEvent(
                    self.event_source, self.kCGEventMouseMoved, (x, y), 0
                )
                self.CGEventPost(self.kCGHIDEventTap, mouse_event)
                return True
            except:
                self.use_quartz = False
        
        try:
            pyautogui.moveTo(x, y, duration=0, _pause=False)
            return True
        except:
            return False
    
    def detect_blink(self, ear_left, ear_right):
        """Detect blink"""
        avg_ear = (ear_left + ear_right) / 2.0
        
        if avg_ear < self.blink_threshold:
            self.blink_counter += 1
        else:
            if self.blink_counter >= self.blink_frames_required:
                self.blink_counter = 0
                return True
            self.blink_counter = 0
        
        return False
    
    def perform_click(self):
        """Perform click with safety checks"""
        current_time = time.time()
        
        # Check cooldown
        if current_time - self.last_click_time < self.click_cooldown:
            return False
        
        try:
            current_x, current_y = pyautogui.position()
            
            # Safety check: avoid window controls
            if current_y < self.safe_zone_margin:
                if current_x < self.safe_zone_margin or current_x > (self.screen_w - self.safe_zone_margin):
                    print("Click blocked - near window controls")
                    self.play_error_sound()
                    return False
            
            # Perform click
            pyautogui.click(current_x, current_y)
            
            self.last_click_time = current_time
            self.click_count += 1
            
            return True
        except Exception as e:
            print(f"Click error: {e}")
            return False
    
    def play_click_sound(self):
        """Play click sound"""
        if not self.audio_feedback:
            return
        
        if self.use_sound_effects:
            try:
                subprocess.Popen(['afplay', self.sound_click], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
            except:
                print('\a')
        else:
            print('\a')
        
        current_pos = pyautogui.position()
        print(f"🖱️ CLICK #{self.click_count} at ({current_pos[0]}, {current_pos[1]})")
    
    def play_error_sound(self):
        """Play error sound"""
        if self.use_sound_effects:
            try:
                subprocess.Popen(['afplay', self.sound_error], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
            except:
                pass
    
    def calculate_fps(self):
        """Calculate FPS"""
        current_time = time.time()
        fps = 1 / (current_time - self.prev_time + 0.0001)
        self.prev_time = current_time
        return int(fps)
    
    def run(self, show_debug=True):
        """Main tracking loop"""
        print("\nStarting Eye Tracker...")
        print("\nCONTROLS:")
        print("  Q - Quit")
        print("  C - Toggle cursor control")
        print("  K - Toggle click on blink")
        print("  A - Toggle audio feedback")
        print("  D - Toggle debug text")
        print("  + - Decrease sensitivity (larger head movements)")
        print("  - - Increase sensitivity (smaller head movements)")
        print("-" * 50)
        
        cursor_control_enabled = True
        show_text_debug = True
        
        while True:
            self._frame_count += 1
            
            ret, frame = self.cam.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_frame)
            fps = self.calculate_fps()
            
            if results.multi_face_landmarks:
                face_landmarks = results.multi_face_landmarks[0]
                landmarks = face_landmarks.landmark
                
                # Get face position
                face_x, face_y = self.get_face_position(landmarks)
                
                # Map to screen
                screen_x, screen_y = self.map_to_screen(face_x, face_y)
                
                # Smooth
                smooth_x, smooth_y = self.smooth_gaze(screen_x, screen_y)
                
                # Move cursor (every 2nd frame)
                if cursor_control_enabled and self._frame_count % 2 == 0:
                    self.move_cursor_fast(smooth_x, smooth_y)
                
                # Blink detection
                ear_right = self.calculate_ear(landmarks, self.RIGHT_EYE)
                ear_left = self.calculate_ear(landmarks, self.LEFT_EYE)
                avg_ear = (ear_left + ear_right) / 2.0
                
                self.adjust_blink_threshold(avg_ear)
                
                if self.detect_blink(ear_left, ear_right):
                    if self.click_enabled:
                        if self.perform_click():
                            self.play_click_sound()
                    else:
                        print("BLINK! (clicking disabled)")
                
                # Draw debug info
                if show_debug:
                    # Draw nose
                    nose = landmarks[self.NOSE_TIP]
                    nose_x = int(nose.x * self.cam_w)
                    nose_y = int(nose.y * self.cam_h)
                    cv2.circle(frame, (nose_x, nose_y), 5, (255, 0, 0), -1)
                    
                    # Draw eyes
                    for eye_idx in self.RIGHT_EYE + self.LEFT_EYE:
                        landmark = landmarks[eye_idx]
                        x = int(landmark.x * self.cam_w)
                        y = int(landmark.y * self.cam_h)
                        cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
                    
                    if show_text_debug:
                        cv2.putText(frame, f"FPS: {fps}", (10, 30),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        cv2.putText(frame, f"Face: ({face_x:.2f}, {face_y:.2f})", (10, 60),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        cv2.putText(frame, f"Screen: ({smooth_x}, {smooth_y})", (10, 90),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        cv2.putText(frame, f"EAR: {avg_ear:.3f}", (10, 120),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        cv2.putText(frame, f"Cursor: {'ON' if cursor_control_enabled else 'OFF'}", (10, 150),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, 
                                   (0, 255, 0) if cursor_control_enabled else (0, 0, 255), 2)
                        cv2.putText(frame, f"Click: {'ON' if self.click_enabled else 'OFF'} (#{self.click_count})", (10, 180),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, 
                                   (0, 255, 0) if self.click_enabled else (0, 0, 255), 2)
                        cv2.putText(frame, f"Sensitivity: {self.screen_margin_x:.2f}", (10, 210),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            else:
                if show_debug:
                    cv2.putText(frame, "NO FACE DETECTED", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    cv2.putText(frame, f"FPS: {fps}", (10, 60),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            if show_debug:
                cv2.imshow('Eye Tracker - BlinkOS (Day 3)', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == ord('Q'):
                print("\n👋 Stopping...")
                break
            elif key == ord('c') or key == ord('C'):
                cursor_control_enabled = not cursor_control_enabled
                print(f"Cursor: {'ON' if cursor_control_enabled else 'OFF'}")
            elif key == ord('k') or key == ord('K'):
                self.click_enabled = not self.click_enabled
                print(f"Click on blink: {'ENABLED' if self.click_enabled else 'DISABLED'}")
            elif key == ord('a') or key == ord('A'):
                self.audio_feedback = not self.audio_feedback
                print(f"Audio: {'ON' if self.audio_feedback else 'OFF'}")
            elif key == ord('d') or key == ord('D'):
                show_text_debug = not show_text_debug
            elif key == ord('+') or key == ord('='):
                self.screen_margin_x = max(0.1, self.screen_margin_x - 0.05)
                self.screen_margin_y = max(0.1, self.screen_margin_y - 0.05)
                print(f"Sensitivity increased: {self.screen_margin_x:.2f}")
            elif key == ord('-') or key == ord('_'):
                self.screen_margin_x = min(0.4, self.screen_margin_x + 0.05)
                self.screen_margin_y = min(0.4, self.screen_margin_y + 0.05)
                print(f"Sensitivity decreased: {self.screen_margin_x:.2f}")
        
        self.cam.release()
        cv2.destroyAllWindows()
        print("Stopped")
    
    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'cam') and self.cam.isOpened():
            self.cam.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    try:
        tracker = EyeTracker()
        tracker.run(show_debug=True)
    except KeyboardInterrupt:
        print("\nInterrupted")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
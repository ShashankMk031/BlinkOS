#!/usr/bin/env python3
"""
Eye Tracker Module - Enhanced with Visual Feedback
Optimized head tracking + blink-to-click + professional visual indicators
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
import math

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from modules.calibration import Calibration
from modules.settings import Settings 


class EyeTracker:
    
    def __init__(self):
        """Initialize the eye tracker with visual enhancements"""
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
        self.settings = Settings() 
        print("Settings loaded") 
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
        self.calibration = Calibration(self.screen_w, self.screen_h)
        self.is_calibrated = self.calibration.load_calibration()
        if self.is_calibrated:
            print(" Calibration loaded - using calibrated mapping")
        else:
            print("  No calibration found - using uncalibrated mode")
            print("   Press 'R' during tracking to run calibration")
        self.calibration_mode = False
        self.screen_margin_x = 0.25
        self.screen_margin_y = 0.20
        
        # FPS
        self.prev_time = 0
        self.fps_history = deque(maxlen=30)
        
        # AGGRESSIVE SMOOTHING for stable cursor
        self.smooth_buffer_size = self.settings.get('eye_tracking','smooth_buffer_size') 
        self.gaze_buffer_x = deque(maxlen=self.smooth_buffer_size)
        self.gaze_buffer_y = deque(maxlen=self.smooth_buffer_size)
        
        # Blink detection
        self.blink_threshold = 0.20
        self.blink_counter = 0
        self.blink_frames_required = 3
        
        # Click control
        self.click_enabled = self.settings.get('eye_tracking','click_enabled') 
        self.last_click_time = 0
        self.click_cooldown = self.settings.get('eye_tracking','click_cooldown') 
        self.click_count = 0
        self.safe_zone_margin = self.settings.get('eye_tracking','safe_zone_margin')
        
        # Frame counter
        self._frame_count = 0
        
        # PyAutoGUI settings
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0
        
        # ==================== VISUAL FEEDBACK FEATURES ====================
        
        # Crosshair settings
        self.show_crosshair = self.settings.get('visual_feedback','show_crosshair') 
        self.crosshair_size = self.settings.get('visual_feedback','crosshair_size')
        self.crosshair_color = (0, 255, 0)
        self.crosshair_thickness = 2
        
        # Click animation
        self.click_animations = []  # List of active animations
        self.click_animation_duration = self.settings.get('visual_feedback','animation_duration') 
        
        # Cursor trail
        self.show_cursor_trail = self.settings.get('visual_feedback','show_cursor_trail')
        self.cursor_trail = deque(maxlen=self.settings.get('visual_feedback','show_cursor_trail'))
        self.trail_fade_speed = 0.8
        
        # Status overlay
        self.show_status_overlay = self.settings.get('visual_feedback', 'show_status_overlay')
        self.tracking_quality = 1.0  # 0.0 to 1.0
        self.quality_history = deque(maxlen=30)
        
        # Face detection confidence
        self.face_detection_confidence = deque(maxlen=10)
        
        # Accuracy indicator
        self.show_accuracy = self.settings.get('visual_feedback', 'show_accuracy_meter')
        self.accuracy_percentage = 80  # Will be calculated
        
        # ==================== END VISUAL FEATURES ====================
        
        # Audio feedback
        self.audio_feedback = self.settings.get('eye_tracking', 'audio_feedback')
        self.use_sound_effects = False
        
        try:
            self.sound_click = "/System/Library/Sounds/Tink.aiff"
            self.sound_error = "/System/Library/Sounds/Basso.aiff"
            
            if os.path.exists(self.sound_click):
                self.use_sound_effects = True
                print(" Sound effects enabled")
        except:
            pass
        
        # Quartz for macOS
        self.use_quartz = self.settings.get('performance', 'enable_quartz') and platform.system() == 'Darwin'
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
                print("  Using Quartz for cursor control")
            except Exception as e:
                self.use_quartz = False
        
        print(" Eye Tracker initialized with visual feedback!")
        print("\n TIP: For best control, move your HEAD to control the cursor")
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
                print(f" Blink threshold adjusted: {self.blink_threshold:.3f}")
    
    def calculate_tracking_quality(self, face_detected, ear_avg):
        """
        Calculate tracking quality score (0.0 to 1.0)
        Based on face detection stability and eye openness
        """
        if not face_detected:
            quality = 0.0
        else:
            # Base quality on EAR (eye openness)
            if ear_avg > self.blink_threshold:
                quality = min(1.0, ear_avg / 0.3)  # Normal range ~0.25-0.35
            else:
                quality = 0.5  # Blinking or partially occluded
        
        self.quality_history.append(quality)
        self.tracking_quality = np.mean(self.quality_history) if self.quality_history else quality
        
        # Update accuracy percentage
        self.accuracy_percentage = int(self.tracking_quality * 100)
    
    def get_quality_color(self):
        """Get color based on tracking quality"""
        if self.tracking_quality > 0.7:
            return (0, 255, 0)  # Green - Excellent
        elif self.tracking_quality > 0.4:
            return (0, 255, 255)  # Yellow - OK
        else:
            return (0, 0, 255)  # Red - Poor
    
    def draw_crosshair(self, frame, x, y):
        """Draw crosshair at cursor position"""
        if not self.show_crosshair:
            return
        
        color = self.get_quality_color()
        size = self.crosshair_size
        thick = self.crosshair_thickness
        
        # Draw cross
        cv2.line(frame, (x - size, y), (x + size, y), color, thick)
        cv2.line(frame, (x, y - size), (x, y + size), color, thick)
        
        # Draw circle
        cv2.circle(frame, (x, y), size // 2, color, thick)
    
    def add_click_animation(self, x, y):
        """Add a click animation at position"""
        self.click_animations.append({
            'x': x,
            'y': y,
            'start_time': time.time(),
            'max_radius': 50
        })
    
    def draw_click_animations(self, frame):
        """Draw all active click animations"""
        current_time = time.time()
        animations_to_remove = []
        
        for i, anim in enumerate(self.click_animations):
            elapsed = current_time - anim['start_time']
            
            if elapsed > self.click_animation_duration:
                animations_to_remove.append(i)
                continue
            
            # Calculate animation progress (0 to 1)
            progress = elapsed / self.click_animation_duration
            
            # Ripple effect
            radius = int(progress * anim['max_radius'])
            opacity = int((1 - progress) * 255)
            
            # Draw expanding circle
            overlay = frame.copy()
            cv2.circle(overlay, (anim['x'], anim['y']), radius, (0, 255, 0), 3)
            
            # Blend with frame
            alpha = (1 - progress) * 0.7
            cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        
        # Remove finished animations
        for i in reversed(animations_to_remove):
            self.click_animations.pop(i)
    
    def draw_cursor_trail(self, frame):
        """Draw cursor trail"""
        if not self.show_cursor_trail or len(self.cursor_trail) < 2:
            return
        
        # Draw trail with fading effect
        for i in range(len(self.cursor_trail) - 1):
            alpha = (i + 1) / len(self.cursor_trail)
            thickness = max(1, int(3 * alpha))
            
            pt1 = self.cursor_trail[i]
            pt2 = self.cursor_trail[i + 1]
            
            color = tuple(int(c * alpha) for c in self.get_quality_color())
            cv2.line(frame, pt1, pt2, color, thickness)
    
    def draw_status_overlay(self, frame, fps, face_detected):
        """Draw status overlay with tracking quality"""
        if not self.show_status_overlay:
            return
        
        # Status bar at top
        bar_height = 40
        overlay = frame.copy()
        
        # Background bar
        cv2.rectangle(overlay, (0, 0), (self.cam_w, bar_height), (40, 40, 40), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Quality indicator circle
        quality_color = self.get_quality_color()
        cv2.circle(frame, (20, 20), 8, quality_color, -1)
        
        # Status text
        if face_detected:
            status_text = f"TRACKING - {self.accuracy_percentage}%"
        else:
            status_text = "NO FACE DETECTED"
        
        cv2.putText(frame, status_text, (35, 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # FPS
        cv2.putText(frame, f"FPS: {fps}", (self.cam_w - 100, 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Click mode indicator
        click_text = "CLICK: ON" if self.click_enabled else "CLICK: OFF"
        click_color = (0, 255, 0) if self.click_enabled else (0, 0, 255)
        cv2.putText(frame, click_text, (self.cam_w // 2 - 50, 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, click_color, 2)
        
        # Calibration status
        if self.is_calibrated:
            calib_text = " CALIBRATED"
            calib_color = (0, 255, 0)
        else:
            calib_text = "⚠ NOT CALIBRATED"
            calib_color = (0, 165, 255)
        
        cv2.putText(frame, calib_text, (10, self.cam_h - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, calib_color, 2)
    
    def draw_accuracy_meter(self, frame):
        """Draw accuracy meter bar"""
        if not self.show_accuracy:
            return
        
        # Meter position (bottom right)
        meter_x = self.cam_w - 150
        meter_y = self.cam_h - 40
        meter_w = 140
        meter_h = 20
        
        # Background
        cv2.rectangle(frame, (meter_x, meter_y), (meter_x + meter_w, meter_y + meter_h),
                     (40, 40, 40), -1)
        
        # Fill based on accuracy
        fill_w = int(meter_w * self.tracking_quality)
        color = self.get_quality_color()
        cv2.rectangle(frame, (meter_x, meter_y), (meter_x + fill_w, meter_y + meter_h),
                     color, -1)
        
        # Border
        cv2.rectangle(frame, (meter_x, meter_y), (meter_x + meter_w, meter_y + meter_h),
                     (200, 200, 200), 2)
        
        # Text
        cv2.putText(frame, f"{self.accuracy_percentage}%", (meter_x + meter_w + 5, meter_y + 15),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    def map_to_screen(self, face_x, face_y):
        """
        Map face position to screen coordinates
        Uses calibration if available
        """
        if self.is_calibrated:
            face_pos = np.array([[face_x, face_y]])
            screen_coords = self.calibration.apply_calibration(face_pos)
            screen_x = int(screen_coords[0, 0])
            screen_y = int(screen_coords[0, 1])
        else:
            margin_x = 0.25
            margin_y = 0.20
            
            norm_x = (face_x - margin_x) / (1 - 2 * margin_x)
            norm_y = (face_y - margin_y) / (1 - 2 * margin_y)
            
            norm_x = max(0, min(1, norm_x))
            norm_y = max(0, min(1, norm_y))
            
            screen_x = int(norm_x * self.screen_w)
            screen_y = int(norm_y * self.screen_h)
        
        return screen_x, screen_y
    
    def smooth_gaze(self, x, y):
        """Apply heavy smoothing for stable cursor"""
        self.gaze_buffer_x.append(x)
        self.gaze_buffer_y.append(y)
        
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
        
        if current_time - self.last_click_time < self.click_cooldown:
            return False
        
        try:
            current_x, current_y = pyautogui.position()
            
            # Safety check
            if current_y < self.safe_zone_margin:
                if current_x < self.safe_zone_margin or current_x > (self.screen_w - self.safe_zone_margin):
                    print(" Click blocked - near window controls")
                    self.play_error_sound()
                    return False
            
            # Perform click
            pyautogui.click(current_x, current_y)
            
            # Add click animation
            # Map screen coords to camera coords for animation
            cam_x = int((current_x / self.screen_w) * self.cam_w)
            cam_y = int((current_y / self.screen_h) * self.cam_h)
            self.add_click_animation(cam_x, cam_y)
            
            self.last_click_time = current_time
            self.click_count += 1
            
            return True
        except Exception as e:
            print(f" Click error: {e}")
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
        print(f" CLICK #{self.click_count} at ({current_pos[0]}, {current_pos[1]})")
    
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
        """Calculate FPS with averaging"""
        current_time = time.time()
        fps = 1 / (current_time - self.prev_time + 0.0001)
        self.prev_time = current_time
        
        self.fps_history.append(fps)
        avg_fps = int(np.mean(self.fps_history)) if self.fps_history else int(fps)
        
        return avg_fps
    
    def run(self, show_debug=True):
        """Main tracking loop with visual feedback"""
        print("\n" + "="*60)
        print("Starting Eye Tracker with Visual Feedback")
        print("="*60)
        print("\nCONTROLS:")
        print("  Q - Quit")
        print("  C - Toggle cursor control")
        print("  K - Toggle click on blink")
        print("  A - Toggle audio feedback")
        print("  V - Toggle visual effects (crosshair, trail, overlay)")
        print("  D - Toggle debug text")
        print('  R - Run calibration')
        print("  L - Reload calibration")
        print("  + - Decrease sensitivity")
        print("  - - Increase sensitivity")
        print("-" * 60 + "\n")
        
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
            
            face_detected = results.multi_face_landmarks is not None
            
            if face_detected:
                face_landmarks = results.multi_face_landmarks[0]
                landmarks = face_landmarks.landmark
                
                # Get face position
                face_x, face_y = self.get_face_position(landmarks)
                
                # Map to screen
                screen_x, screen_y = self.map_to_screen(face_x, face_y)
                
                # Smooth
                smooth_x, smooth_y = self.smooth_gaze(screen_x, screen_y)
                
                # Add to trail
                cam_x = int((smooth_x / self.screen_w) * self.cam_w)
                cam_y = int((smooth_y / self.screen_h) * self.cam_h)
                self.cursor_trail.append((cam_x, cam_y))
                
                # Move cursor
                if cursor_control_enabled and self._frame_count % self.settings.get('eye_tracking', 'update_rate') == 0:
                    self.move_cursor_fast(smooth_x, smooth_y)
                
                # Blink detection
                ear_right = self.calculate_ear(landmarks, self.RIGHT_EYE)
                ear_left = self.calculate_ear(landmarks, self.LEFT_EYE)
                avg_ear = (ear_left + ear_right) / 2.0
                
                self.adjust_blink_threshold(avg_ear)
                self.calculate_tracking_quality(True, avg_ear)
                
                if self.detect_blink(ear_left, ear_right):
                    if self.click_enabled:
                        if self.perform_click():
                            self.play_click_sound()
                    else:
                        print("BLINK! (clicking disabled)")
                
                # Draw visual feedback
                if show_debug:
                    # Draw cursor trail
                    self.draw_cursor_trail(frame)
                    
                    # Draw crosshair at current gaze
                    self.draw_crosshair(frame, cam_x, cam_y)
                    
                    # Draw click animations
                    self.draw_click_animations(frame)
                    
                    # Draw status overlay
                    self.draw_status_overlay(frame, fps, True)
                    
                    # Draw accuracy meter
                    self.draw_accuracy_meter(frame)
                    
                    # Draw landmarks
                    nose = landmarks[self.NOSE_TIP]
                    nose_x = int(nose.x * self.cam_w)
                    nose_y = int(nose.y * self.cam_h)
                    cv2.circle(frame, (nose_x, nose_y), 5, (255, 0, 0), -1)
                    
                    for eye_idx in self.RIGHT_EYE + self.LEFT_EYE:
                        landmark = landmarks[eye_idx]
                        x = int(landmark.x * self.cam_w)
                        y = int(landmark.y * self.cam_h)
                        cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
            
            else:
                self.calculate_tracking_quality(False, 0)
                
                if show_debug:
                    # Draw status overlay even without face
                    self.draw_status_overlay(frame, fps, False)
                    
                    cv2.putText(frame, " NO FACE DETECTED", 
                               (self.cam_w//2 - 150, self.cam_h//2),
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            
            if show_debug:
                cv2.imshow('Eye Tracker - BlinkOS Enhanced', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == ord('Q'):
                print("\n Stopping...")
                break
            elif key == ord('c') or key == ord('C'):
                cursor_control_enabled = not cursor_control_enabled
                print(f" Cursor: {'ON' if cursor_control_enabled else 'OFF'}")
            elif key == ord('k') or key == ord('K'):
                self.click_enabled = not self.click_enabled
                print(f" Click on blink: {'ENABLED' if self.click_enabled else 'DISABLED'}")
            elif key == ord('a') or key == ord('A'):
                self.audio_feedback = not self.audio_feedback
                print(f" Audio: {'ON' if self.audio_feedback else 'OFF'}")
            elif key == ord('v') or key == ord('V'):
                # Toggle all visual effects
                self.show_crosshair = not self.show_crosshair
                self.show_cursor_trail = not self.show_cursor_trail
                self.show_status_overlay = not self.show_status_overlay
                state = "ON" if self.show_crosshair else "OFF"
                print(f" Visual effects: {state}")
            elif key == ord('d') or key == ord('D'):
                show_text_debug = not show_text_debug
                show_debug = not show_debug
                print(f" Debug: {'ON' if show_debug else 'OFF'}")
            elif key == ord('r') or key == ord('R'):
                print("\n Starting calibration...")
                cv2.destroyWindow('Eye Tracker - BlinkOS Enhanced')
                success = self.calibration.run_calibration(self.face_mesh, self.cam)
                if success:
                    self.is_calibrated = True
                    print(" Calibration complete - cursor control improved!")
                else:
                    print("Calibration failed")
            elif key == ord('l') or key == ord('L'):
                self.is_calibrated = self.calibration.load_calibration()
                if self.is_calibrated:
                    print("Calibration reloaded")
                else:
                    print("No calibration file found")
            elif key == ord('+') or key == ord('='):
                if not self.is_calibrated:
                    self.screen_margin_x = max(0.1, self.screen_margin_x - 0.05)
                    self.screen_margin_y = max(0.1, self.screen_margin_y - 0.05)
                    print(f" Sensitivity increased: {self.screen_margin_x:.2f}")
                else:
                    print(" Using calibrated mode - sensitivity adjustment not needed")
            elif key == ord('-') or key == ord('_'):
                if not self.is_calibrated:
                    self.screen_margin_x = min(0.4, self.screen_margin_x + 0.05)
                    self.screen_margin_y = min(0.4, self.screen_margin_y + 0.05)
                    print(f" Sensitivity decreased: {self.screen_margin_x:.2f}")
                else:
                    print(" Using calibrated mode - sensitivity adjustment not needed")
        
        self.cam.release()
        cv2.destroyAllWindows()
        print("\nEye Tracker stopped")
        print(f"Total clicks: {self.click_count}")
        print(f"Average accuracy: {self.accuracy_percentage}%")
    
    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'cam') and self.cam.isOpened():
            self.cam.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    try:
        print("\n" + "="*60)
        print("BlinkOS - Enhanced Eye Tracker")
        print("="*60 + "\n")
        
        tracker = EyeTracker()
        tracker.run(show_debug=True)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
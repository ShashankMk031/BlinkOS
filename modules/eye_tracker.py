#!/usr/bin/env python3
"""
Eye Tracker Module - Enhanced with Visual Feedback & Error Handling
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
from modules.error_handler import ErrorHandler, RecoveryManager
from modules.logger import Logger, SessionLogger


class EyeTracker:
    
    def __init__(self):
        """Initialize the eye tracker with visual enhancements and error handling"""
        
        # Initialize error handling and logging FIRST
        self.error_handler = ErrorHandler()
        self.recovery_manager = RecoveryManager()
        self.logger = Logger()
        self.session_logger = SessionLogger(self.logger)
        
        # Log startup
        self.logger.log_system_info()
        self.logger.info("Eye Tracker initializing...")
        
        # Check permissions (microphone optional for eye tracker)
        print("\nChecking system requirements...")
        if not self.error_handler.check_all_permissions(require_microphone=False):
            self.logger.error("Permission check failed")
            raise Exception("Permission check failed - see messages above")
        
        self.logger.info("All permissions OK")
        
        # Load settings
        try:
            self.settings = Settings()
            self.logger.info("Settings loaded successfully")
            print("Settings loaded")
        except Exception as e:
            self.error_handler.handle_error(e, "Settings loading")
            self.logger.warning("Using default settings")
            self.settings = None
        
        # MediaPipe Face Mesh
        try:
            self.mp_face_mesh = mp.solutions.face_mesh
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
                static_image_mode=False
            )
            self.logger.info("MediaPipe Face Mesh initialized")
        except Exception as e:
            self.error_handler.handle_error(e, "MediaPipe initialization", fatal=True)
        
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Screen dimensions
        self.screen_w, self.screen_h = pyautogui.size()
        self.logger.info(f"Screen resolution: {self.screen_w}x{self.screen_h}")
        print(f"Screen resolution: {self.screen_w}x{self.screen_h}")
        
        # Camera setup with error handling
        try:
            self.cam = self.error_handler.safe_camera_init()
            if self.cam is None:
                raise Exception("Failed to initialize camera")
            
            self.cam_w = int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.cam_h = int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.logger.info(f"Camera initialized: {self.cam_w}x{self.cam_h}")
            print(f"Camera resolution: {self.cam_w}x{self.cam_h}")
        except Exception as e:
            self.error_handler.handle_error(e, "Camera initialization", fatal=True)
        
        # Face landmarks
        self.NOSE_TIP = 1
        self.RIGHT_EYE = [33, 160, 158, 133, 153, 144]
        self.LEFT_EYE = [362, 385, 387, 263, 373, 380]
        
        # Calibration mode
        try:
            self.calibration = Calibration(self.screen_w, self.screen_h)
            self.is_calibrated = self.calibration.load_calibration()
            if self.is_calibrated:
                self.logger.info("Calibration loaded successfully")
                print("Calibration loaded - using calibrated mapping")
            else:
                self.logger.info("No calibration found")
                print("No calibration found - using uncalibrated mode")
                print("   Press 'R' during tracking to run calibration")
        except Exception as e:
            self.error_handler.handle_error(e, "Calibration loading")
            self.is_calibrated = False
        
        self.calibration_mode = False
        self.screen_margin_x = 0.25
        self.screen_margin_y = 0.20
        
        # FPS
        self.prev_time = 0
        self.fps_history = deque(maxlen=30)
        
        # Load settings or use defaults
        if self.settings:
            self.smooth_buffer_size = self.settings.get('eye_tracking', 'smooth_buffer_size')
            self.click_enabled = self.settings.get('eye_tracking', 'click_enabled')
            self.click_cooldown = self.settings.get('eye_tracking', 'click_cooldown')
            self.safe_zone_margin = self.settings.get('eye_tracking', 'safe_zone_margin')
            self.audio_feedback = self.settings.get('eye_tracking', 'audio_feedback')
        else:
            self.smooth_buffer_size = 25
            self.click_enabled = True
            self.click_cooldown = 1.0
            self.safe_zone_margin = 50
            self.audio_feedback = True
        
        self.gaze_buffer_x = deque(maxlen=self.smooth_buffer_size)
        self.gaze_buffer_y = deque(maxlen=self.smooth_buffer_size)
        
        # Blink detection
        self.blink_threshold = 0.20
        self.blink_counter = 0
        self.blink_frames_required = 3
        
        # Click control
        self.last_click_time = 0
        self.click_count = 0
        
        # Frame counter
        self._frame_count = 0
        
        # PyAutoGUI settings
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0
        
        # Visual feedback features
        if self.settings:
            self.show_crosshair = self.settings.get('visual_feedback', 'show_crosshair')
            self.crosshair_size = self.settings.get('visual_feedback', 'crosshair_size')
            self.click_animation_duration = self.settings.get('visual_feedback', 'animation_duration')
            self.show_cursor_trail = self.settings.get('visual_feedback', 'show_cursor_trail')
            trail_length = self.settings.get('visual_feedback', 'trail_length')
            self.show_status_overlay = self.settings.get('visual_feedback', 'show_status_overlay')
            self.show_accuracy = self.settings.get('visual_feedback', 'show_accuracy_meter')
        else:
            self.show_crosshair = True
            self.crosshair_size = 20
            self.click_animation_duration = 0.5
            self.show_cursor_trail = True
            trail_length = 10
            self.show_status_overlay = True
            self.show_accuracy = True
        
        self.crosshair_color = (0, 255, 0)
        self.crosshair_thickness = 2
        self.click_animations = []
        self.cursor_trail = deque(maxlen=trail_length)
        self.trail_fade_speed = 0.8
        self.tracking_quality = 1.0
        self.quality_history = deque(maxlen=30)
        self.face_detection_confidence = deque(maxlen=10)
        self.accuracy_percentage = 80
        
        # Audio feedback
        self.use_sound_effects = False
        
        try:
            self.sound_click = "/System/Library/Sounds/Tink.aiff"
            self.sound_error = "/System/Library/Sounds/Basso.aiff"
            
            if os.path.exists(self.sound_click):
                self.use_sound_effects = True
                self.logger.info("Sound effects enabled")
                print("Sound effects enabled")
        except Exception as e:
            self.logger.warning(f"Sound effects disabled: {e}")
        
        # Quartz for macOS
        if self.settings:
            enable_quartz = self.settings.get('performance', 'enable_quartz')
        else:
            enable_quartz = True
        
        self.use_quartz = enable_quartz and platform.system() == 'Darwin'
        
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
                self.logger.info("Using Quartz for cursor control")
                print("Using Quartz for cursor control")
            except Exception as e:
                self.use_quartz = False
                self.logger.warning("Quartz unavailable, using PyAutoGUI")
        
        self.logger.info("Eye Tracker initialized successfully")
        print("Eye Tracker initialized with visual feedback!")
        print("\nTIP: For best control, move your HEAD to control the cursor")
        print("   Keep your head ~50cm from camera, well-lit from front\n")
    
    def get_face_position(self, landmarks):
        """Get face position using nose tip"""
        nose = landmarks[self.NOSE_TIP]
        return nose.x, nose.y
    
    def calculate_ear(self, landmarks, eye_indices):
        """Calculate Eye Aspect Ratio for blink detection"""
        try:
            points = np.array([[landmarks[i].x, landmarks[i].y, landmarks[i].z] for i in eye_indices])
            
            v1 = np.linalg.norm(points[1] - points[5])
            v2 = np.linalg.norm(points[2] - points[4])
            h = np.linalg.norm(points[0] - points[3])
            
            ear = (v1 + v2) / (2.0 * h + 0.0001)
            return ear
        except Exception as e:
            self.error_handler.handle_error(e, "EAR calculation")
            return 0.3
    
    def adjust_blink_threshold(self, current_ear):
        """Auto-adjust blink threshold"""
        try:
            if not hasattr(self, '_ear_baseline_samples'):
                self._ear_baseline_samples = []
            
            if current_ear > 0.2:
                self._ear_baseline_samples.append(current_ear)
                
                if len(self._ear_baseline_samples) == 30:
                    baseline_ear = np.mean(self._ear_baseline_samples)
                    self.blink_threshold = baseline_ear * 0.6
                    self.logger.info(f"Blink threshold adjusted: {self.blink_threshold:.3f}")
                    print(f"Blink threshold adjusted: {self.blink_threshold:.3f}")
        except Exception as e:
            self.error_handler.handle_error(e, "Blink threshold adjustment")
    
    def calculate_tracking_quality(self, face_detected, ear_avg):
        """Calculate tracking quality score"""
        try:
            if not face_detected:
                quality = 0.0
            else:
                if ear_avg > self.blink_threshold:
                    quality = min(1.0, ear_avg / 0.3)
                else:
                    quality = 0.5
            
            self.quality_history.append(quality)
            self.tracking_quality = np.mean(self.quality_history) if self.quality_history else quality
            self.accuracy_percentage = int(self.tracking_quality * 100)
        except Exception as e:
            self.error_handler.handle_error(e, "Quality calculation")
            self.tracking_quality = 0.5
            self.accuracy_percentage = 50
    
    def get_quality_color(self):
        """Get color based on tracking quality"""
        if self.tracking_quality > 0.7:
            return (0, 255, 0)
        elif self.tracking_quality > 0.4:
            return (0, 255, 255)
        else:
            return (0, 0, 255)
    
    def draw_crosshair(self, frame, x, y):
        """Draw crosshair at cursor position"""
        if not self.show_crosshair:
            return
        
        try:
            color = self.get_quality_color()
            size = self.crosshair_size
            thick = self.crosshair_thickness
            
            cv2.line(frame, (x - size, y), (x + size, y), color, thick)
            cv2.line(frame, (x, y - size), (x, y + size), color, thick)
            cv2.circle(frame, (x, y), size // 2, color, thick)
        except Exception as e:
            self.error_handler.handle_error(e, "Crosshair drawing")
    
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
        try:
            current_time = time.time()
            animations_to_remove = []
            
            for i, anim in enumerate(self.click_animations):
                elapsed = current_time - anim['start_time']
                
                if elapsed > self.click_animation_duration:
                    animations_to_remove.append(i)
                    continue
                
                progress = elapsed / self.click_animation_duration
                radius = int(progress * anim['max_radius'])
                
                overlay = frame.copy()
                cv2.circle(overlay, (anim['x'], anim['y']), radius, (0, 255, 0), 3)
                
                alpha = (1 - progress) * 0.7
                cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
            
            for i in reversed(animations_to_remove):
                self.click_animations.pop(i)
        except Exception as e:
            self.error_handler.handle_error(e, "Click animation drawing")
    
    def draw_cursor_trail(self, frame):
        """Draw cursor trail"""
        if not self.show_cursor_trail or len(self.cursor_trail) < 2:
            return
        
        try:
            for i in range(len(self.cursor_trail) - 1):
                alpha = (i + 1) / len(self.cursor_trail)
                thickness = max(1, int(3 * alpha))
                
                pt1 = self.cursor_trail[i]
                pt2 = self.cursor_trail[i + 1]
                
                color = tuple(int(c * alpha) for c in self.get_quality_color())
                cv2.line(frame, pt1, pt2, color, thickness)
        except Exception as e:
            self.error_handler.handle_error(e, "Trail drawing")
    
    def draw_status_overlay(self, frame, fps, face_detected):
        """Draw status overlay with tracking quality"""
        if not self.show_status_overlay:
            return
        
        try:
            bar_height = 40
            overlay = frame.copy()
            
            cv2.rectangle(overlay, (0, 0), (self.cam_w, bar_height), (40, 40, 40), -1)
            cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
            
            quality_color = self.get_quality_color()
            cv2.circle(frame, (20, 20), 8, quality_color, -1)
            
            if face_detected:
                status_text = f"TRACKING - {self.accuracy_percentage}%"
            else:
                status_text = "NO FACE DETECTED"
            
            cv2.putText(frame, status_text, (35, 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            cv2.putText(frame, f"FPS: {fps}", (self.cam_w - 100, 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            click_text = "CLICK: ON" if self.click_enabled else "CLICK: OFF"
            click_color = (0, 255, 0) if self.click_enabled else (0, 0, 255)
            cv2.putText(frame, click_text, (self.cam_w // 2 - 50, 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, click_color, 2)
            
            if self.is_calibrated:
                calib_text = "CALIBRATED"
                calib_color = (0, 255, 0)
            else:
                calib_text = "NOT CALIBRATED"
                calib_color = (0, 165, 255)
            
            cv2.putText(frame, calib_text, (10, self.cam_h - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, calib_color, 2)
        except Exception as e:
            self.error_handler.handle_error(e, "Status overlay drawing")
    
    def draw_accuracy_meter(self, frame):
        """Draw accuracy meter bar"""
        if not self.show_accuracy:
            return
        
        try:
            meter_x = self.cam_w - 150
            meter_y = self.cam_h - 40
            meter_w = 140
            meter_h = 20
            
            cv2.rectangle(frame, (meter_x, meter_y), (meter_x + meter_w, meter_y + meter_h),
                         (40, 40, 40), -1)
            
            fill_w = int(meter_w * self.tracking_quality)
            color = self.get_quality_color()
            cv2.rectangle(frame, (meter_x, meter_y), (meter_x + fill_w, meter_y + meter_h),
                         color, -1)
            
            cv2.rectangle(frame, (meter_x, meter_y), (meter_x + meter_w, meter_y + meter_h),
                         (200, 200, 200), 2)
            
            cv2.putText(frame, f"{self.accuracy_percentage}%", (meter_x + meter_w + 5, meter_y + 15),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        except Exception as e:
            self.error_handler.handle_error(e, "Accuracy meter drawing")
    
    def map_to_screen(self, face_x, face_y):
        """Map face position to screen coordinates"""
        try:
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
        except Exception as e:
            self.error_handler.handle_error(e, "Screen mapping")
            return self.screen_w // 2, self.screen_h // 2
    
    def smooth_gaze(self, x, y):
        """Apply heavy smoothing for stable cursor"""
        try:
            self.gaze_buffer_x.append(x)
            self.gaze_buffer_y.append(y)
            
            weights = np.linspace(0.5, 1.0, len(self.gaze_buffer_x))
            
            smooth_x = int(np.average(self.gaze_buffer_x, weights=weights))
            smooth_y = int(np.average(self.gaze_buffer_y, weights=weights))
            
            return smooth_x, smooth_y
        except Exception as e:
            self.error_handler.handle_error(e, "Gaze smoothing")
            return x, y
    
    def move_cursor_fast(self, x, y):
        """Fast cursor movement"""
        try:
            if self.use_quartz:
                try:
                    mouse_event = self.CGEventCreateMouseEvent(
                        self.event_source, self.kCGEventMouseMoved, (x, y), 0
                    )
                    self.CGEventPost(self.kCGHIDEventTap, mouse_event)
                    return True
                except:
                    self.use_quartz = False
            
            pyautogui.moveTo(x, y, duration=0, _pause=False)
            return True
        except Exception as e:
            self.error_handler.handle_error(e, "Cursor movement")
            return False
    
    def detect_blink(self, ear_left, ear_right):
        """Detect blink"""
        try:
            avg_ear = (ear_left + ear_right) / 2.0
            
            if avg_ear < self.blink_threshold:
                self.blink_counter += 1
            else:
                if self.blink_counter >= self.blink_frames_required:
                    self.blink_counter = 0
                    return True
                self.blink_counter = 0
            
            return False
        except Exception as e:
            self.error_handler.handle_error(e, "Blink detection")
            return False
    
    def perform_click(self):
        """Perform click with safety checks"""
        try:
            current_time = time.time()
            
            if current_time - self.last_click_time < self.click_cooldown:
                return False
            
            current_x, current_y = pyautogui.position()
            
            if current_y < self.safe_zone_margin:
                if current_x < self.safe_zone_margin or current_x > (self.screen_w - self.safe_zone_margin):
                    self.logger.warning("Click blocked - near window controls")
                    print("Click blocked - near window controls")
                    self.play_error_sound()
                    return False
            
            pyautogui.click(current_x, current_y)
            
            cam_x = int((current_x / self.screen_w) * self.cam_w)
            cam_y = int((current_y / self.screen_h) * self.cam_h)
            self.add_click_animation(cam_x, cam_y)
            
            self.last_click_time = current_time
            self.click_count += 1
            
            self.session_logger.log_click()
            
            return True
        except Exception as e:
            self.error_handler.handle_error(e, "Click performance")
            return False
    
    def play_click_sound(self):
        """Play click sound"""
        if not self.audio_feedback:
            return
        
        try:
            if self.use_sound_effects:
                subprocess.Popen(['afplay', self.sound_click], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
            else:
                print('\a')
            
            current_pos = pyautogui.position()
            print(f"CLICK #{self.click_count} at ({current_pos[0]}, {current_pos[1]})")
        except Exception as e:
            self.error_handler.handle_error(e, "Click sound")
    
    def play_error_sound(self):
        """Play error sound"""
        try:
            if self.use_sound_effects:
                subprocess.Popen(['afplay', self.sound_error], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
        except Exception as e:
            self.error_handler.handle_error(e, "Error sound")
    
    def calculate_fps(self):
        """Calculate FPS with averaging"""
        try:
            current_time = time.time()
            fps = 1 / (current_time - self.prev_time + 0.0001)
            self.prev_time = current_time
            
            self.fps_history.append(fps)
            avg_fps = int(np.mean(self.fps_history)) if self.fps_history else int(fps)
            
            return avg_fps
        except Exception as e:
            self.error_handler.handle_error(e, "FPS calculation")
            return 30
        
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
        print("  V - Toggle visual effects")
        print("  D - Toggle debug")
        print('  R - Run calibration')
        print("  L - Reload calibration")
        print("  + - Decrease sensitivity")
        print("  - - Increase sensitivity")
        print("-" * 60 + "\n")
        
        self.logger.info("Eye tracker started")
        
        cursor_control_enabled = True
        show_text_debug = True
        
        if self.settings:
            update_rate = self.settings.get('eye_tracking', 'update_rate')
        else:
            update_rate = 3
        
        try:
            while True:
                self._frame_count += 1
                
                ret, frame = self.cam.read()
                if not ret:
                    if self.recovery_manager.attempt_recovery(None, "camera_read"):
                        continue
                    else:
                        break
                
                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.face_mesh.process(rgb_frame)
                fps = self.calculate_fps()
                
                face_detected = results.multi_face_landmarks is not None
                
                if face_detected:
                    self.recovery_manager.reset_retry("face_detection")
                    
                    face_landmarks = results.multi_face_landmarks[0]
                    landmarks = face_landmarks.landmark
                    
                    face_x, face_y = self.get_face_position(landmarks)
                    screen_x, screen_y = self.map_to_screen(face_x, face_y)
                    smooth_x, smooth_y = self.smooth_gaze(screen_x, screen_y)
                    
                    cam_x = int((smooth_x / self.screen_w) * self.cam_w)
                    cam_y = int((smooth_y / self.screen_h) * self.cam_h)
                    self.cursor_trail.append((cam_x, cam_y))
                    
                    if cursor_control_enabled and self._frame_count % update_rate == 0:
                        self.move_cursor_fast(smooth_x, smooth_y)
                    
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
                    
                    if show_debug:
                        self.draw_cursor_trail(frame)
                        self.draw_crosshair(frame, cam_x, cam_y)
                        self.draw_click_animations(frame)
                        self.draw_status_overlay(frame, fps, True)
                        self.draw_accuracy_meter(frame)
                        
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
                        self.draw_status_overlay(frame, fps, False)
                        cv2.putText(frame, "NO FACE DETECTED", 
                                   (self.cam_w//2 - 150, self.cam_h//2),
                                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                
                if show_debug:
                    cv2.imshow('Eye Tracker - BlinkOS Enhanced', frame)
                
                key = cv2.waitKey(1) & 0xFF

                if key == 255 or key < 0: 
                    continue
                if key == ord('q') or key == ord('Q'):
                    self.logger.info("User requested quit")
                    print("\nStopping...")
                    break
                elif key == ord('c') or key == ord('C'):
                    cursor_control_enabled = not cursor_control_enabled
                    self.logger.info(f"Cursor control: {cursor_control_enabled}")
                    print(f"Cursor: {'ON' if cursor_control_enabled else 'OFF'}")
                elif key == ord('k') or key == ord('K'):
                    self.click_enabled = not self.click_enabled
                    self.logger.info(f"Click enabled: {self.click_enabled}")
                    print(f"Click on blink: {'ENABLED' if self.click_enabled else 'DISABLED'}")
                elif key == ord('a') or key == ord('A'):
                    self.audio_feedback = not self.audio_feedback
                    print(f"Audio: {'ON' if self.audio_feedback else 'OFF'}")
                elif key == ord('v') or key == ord('V'):
                    self.show_crosshair = not self.show_crosshair
                    self.show_cursor_trail = not self.show_cursor_trail
                    self.show_status_overlay = not self.show_status_overlay
                    state = "ON" if self.show_crosshair else "OFF"
                    print(f"Visual effects: {state}")
                elif key == ord('d') or key == ord('D'):
                    show_text_debug = not show_text_debug
                    show_debug = not show_debug
                    print(f"Debug: {'ON' if show_debug else 'OFF'}")
                elif key == ord('r') or key == ord('R'):
                    self.logger.info("Starting calibration")
                    print("\nStarting calibration...")
                    cv2.destroyWindow('Eye Tracker - BlinkOS Enhanced')
                    success = self.calibration.run_calibration(self.face_mesh, self.cam)
                    if success:
                        self.is_calibrated = True
                        self.session_logger.log_calibration(int(self.calibration.calibration_quality * 100))
                        print("Calibration complete!")
                    else:
                        print("Calibration failed")
                elif key == ord('l') or key == ord('L'):
                    self.is_calibrated = self.calibration.load_calibration()
                    msg = "reloaded" if self.is_calibrated else "not found"
                    self.logger.info(f"Calibration {msg}")
                    print(f"Calibration {msg}")
                elif key == ord('+') or key == ord('='):
                    if not self.is_calibrated:
                        self.screen_margin_x = max(0.1, self.screen_margin_x - 0.05)
                        self.screen_margin_y = max(0.1, self.screen_margin_y - 0.05)
                        print(f"Sensitivity increased: {self.screen_margin_x:.2f}")
                    else:
                        print("Using calibrated mode")
                elif key == ord('-') or key == ord('_'):
                    if not self.is_calibrated:
                        self.screen_margin_x = min(0.4, self.screen_margin_x + 0.05)
                        self.screen_margin_y = min(0.4, self.screen_margin_y + 0.05)
                        print(f"Sensitivity decreased: {self.screen_margin_x:.2f}")
                    else:
                        print("Using calibrated mode")
        
        except KeyboardInterrupt:
            self.logger.info("Interrupted by user")
            print("\n\nInterrupted by user")
        except Exception as e:
            self.error_handler.handle_error(e, "Main loop", fatal=False)
            self.logger.error(f"Fatal error in main loop: {e}")
        finally:
            self.session_logger.log_session_end()
            self.logger.close()
            
            self.cam.release()
            cv2.destroyAllWindows()
            print("\nEye Tracker stopped")
            print(f"Total clicks: {self.click_count}")
            print(f"Average accuracy: {self.accuracy_percentage}%")
            print(f"Log file: {self.logger.log_file}")
    
    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'cam') and self.cam is not None and self.cam.isOpened():
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
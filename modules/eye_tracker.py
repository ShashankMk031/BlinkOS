#!/usr/bin/env python3
"""
Eye Tracker Module - Core eye tracking and cursor control
Uses MediaPipe Face Mesh for facial landmark detection
"""

import cv2
import mediapipe as mp
import pyautogui
import numpy as np
from collections import deque
import time
import platform


class EyeTracker:
    """
    Main eye tracking class that handles face detection,
    gaze tracking, and cursor control
    """
    
    def __init__(self):
        """Initialize the eye tracker with MediaPipe and camera"""
        # MediaPipe Face Mesh setup
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            static_image_mode=False
        )
        
        # Drawing utilities
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Screen dimensions
        self.screen_w, self.screen_h = pyautogui.size()
        print(f"Screen resolution: {self.screen_w}x{self.screen_h}")
        
        # Camera setup
        self.cam = cv2.VideoCapture(0)
        if not self.cam.isOpened():
            raise Exception("Cannot open camera. Check permissions!")
        
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        self.cam_w = int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.cam_h = int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"Camera resolution: {self.cam_w}x{self.cam_h}")
        
        # Face landmarks for tracking
        self.NOSE_TIP = 1
        self.FOREHEAD = 10
        self.CHIN = 152
        self.LEFT_CHEEK = 234
        self.RIGHT_CHEEK = 454
        
        # Eye landmarks
        self.RIGHT_EYE = [33, 160, 158, 133, 153, 144]
        self.LEFT_EYE = [362, 385, 387, 263, 373, 380]
        
        # Eye center landmarks (more reliable)
        self.RIGHT_EYE_CENTER = 468
        self.LEFT_EYE_CENTER = 473
        
        # Iris landmarks
        self.RIGHT_IRIS = [474, 475, 476, 477]
        self.LEFT_IRIS = [469, 470, 471, 472]
        
        # Calibration
        self.is_calibrated = False
        self.face_center_baseline = None
        
        # FPS
        self.prev_time = 0
        
        # Smoothing
        self.smooth_buffer_size = 7
        self.gaze_buffer_x = deque(maxlen=self.smooth_buffer_size)
        self.gaze_buffer_y = deque(maxlen=self.smooth_buffer_size)
        
        # Blink detection
        self.blink_threshold = 0.20
        self.blink_counter = 0
        self.blink_frames_required = 3
        
        # Frame counter
        self._frame_count = 0
        
        # PyAutoGUI settings
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0
        
        # Try Quartz for macOS
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
                print("✅ Using Quartz for cursor control (faster)")
            except Exception as e:
                self.use_quartz = False
                print(f"⚠️ Quartz not available: {e}")
                print("   Using PyAutoGUI instead")
        
        print("✅ Eye Tracker initialized successfully!")
    
    def get_face_position(self, landmarks):
        """
        Get normalized face position (0-1) within camera frame
        Uses nose tip as reference point
        """
        nose = landmarks[self.NOSE_TIP]
        return nose.x, nose.y
    
    def get_eye_centers(self, landmarks):
        """
        Get the center points of both eyes
        Uses multiple landmarks for more stability
        """
        # Right eye center
        right_points = [landmarks[i] for i in self.RIGHT_EYE]
        right_x = np.mean([p.x for p in right_points])
        right_y = np.mean([p.y for p in right_points])
        
        # Left eye center
        left_points = [landmarks[i] for i in self.LEFT_EYE]
        left_x = np.mean([p.x for p in left_points])
        left_y = np.mean([p.y for p in left_points])
        
        return (right_x, right_y), (left_x, left_y)
    
    def get_iris_offset(self, landmarks):
        """
        Calculate how far iris is from eye center (gaze direction)
        Returns offset in normalized coordinates
        """
        try:
            # Get eye centers
            right_eye_center = np.mean([[landmarks[i].x, landmarks[i].y] for i in self.RIGHT_EYE], axis=0)
            left_eye_center = np.mean([[landmarks[i].x, landmarks[i].y] for i in self.LEFT_EYE], axis=0)
            
            # Get iris positions (if available)
            if len(landmarks) > max(self.RIGHT_IRIS):
                right_iris = np.mean([[landmarks[i].x, landmarks[i].y] for i in self.RIGHT_IRIS], axis=0)
                left_iris = np.mean([[landmarks[i].x, landmarks[i].y] for i in self.LEFT_IRIS], axis=0)
                
                # Calculate offset (iris - eye_center)
                right_offset = right_iris - right_eye_center
                left_offset = left_iris - left_eye_center
                
                # Average both eyes
                avg_offset = (right_offset + left_offset) / 2.0
                
                return avg_offset[0], avg_offset[1]
        except:
            pass
        
        return 0.0, 0.0
    
    def calculate_ear(self, landmarks, eye_indices):
        """Calculate Eye Aspect Ratio for blink detection"""
        points = np.array([[landmarks[i].x, landmarks[i].y, landmarks[i].z] for i in eye_indices])
        
        # Vertical distances
        v1 = np.linalg.norm(points[1] - points[5])
        v2 = np.linalg.norm(points[2] - points[4])
        
        # Horizontal distance
        h = np.linalg.norm(points[0] - points[3])
        
        ear = (v1 + v2) / (2.0 * h + 0.0001)
        return ear
    
    def adjust_blink_threshold(self, current_ear):
        """Dynamically adjust blink threshold"""
        if not hasattr(self, '_ear_baseline_samples'):
            self._ear_baseline_samples = []
        
        if current_ear > 0.2:
            self._ear_baseline_samples.append(current_ear)
            
            if len(self._ear_baseline_samples) == 30:
                baseline_ear = np.mean(self._ear_baseline_samples)
                self.blink_threshold = baseline_ear * 0.6
                print(f"📊 Blink threshold: {self.blink_threshold:.3f}")
    
    def map_to_screen(self, face_x, face_y, iris_offset_x, iris_offset_y):
        """
        Map face position + iris offset to screen coordinates
        Combines overall face position with fine eye movements
        """
        # Face position gives rough position (0-1 normalized)
        # We'll use full camera frame, with some margin
        margin = 0.15
        
        # Normalize face position with margins
        norm_x = (face_x - margin) / (1 - 2 * margin)
        norm_y = (face_y - margin) / (1 - 2 * margin)
        
        # Clamp to 0-1
        norm_x = max(0, min(1, norm_x))
        norm_y = max(0, min(1, norm_y))
        
        # Add iris offset for fine control (amplified)
        iris_amplification = 15.0  # Amplify small iris movements
        norm_x += iris_offset_x * iris_amplification
        norm_y += iris_offset_y * iris_amplification
        
        # Clamp again
        norm_x = max(0, min(1, norm_x))
        norm_y = max(0, min(1, norm_y))
        
        # Map to screen
        screen_x = int(norm_x * self.screen_w)
        screen_y = int(norm_y * self.screen_h)
        
        return screen_x, screen_y
    
    def smooth_gaze(self, x, y):
        """Apply smoothing"""
        self.gaze_buffer_x.append(x)
        self.gaze_buffer_y.append(y)
        
        smooth_x = int(np.mean(self.gaze_buffer_x))
        smooth_y = int(np.mean(self.gaze_buffer_y))
        
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
    
    def calculate_fps(self):
        """Calculate FPS"""
        current_time = time.time()
        fps = 1 / (current_time - self.prev_time + 0.0001)
        self.prev_time = current_time
        return int(fps)
    
    def run(self, show_debug=True):
        """Main tracking loop"""
        print("\n🚀 Starting Eye Tracker...")
        print("Press 'Q' to quit")
        print("Press 'C' to toggle cursor control")
        print("Press 'D' to toggle debug text")
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
                
                # Get face position (primary control)
                face_x, face_y = self.get_face_position(landmarks)
                
                # Get iris offset (fine control)
                iris_offset_x, iris_offset_y = self.get_iris_offset(landmarks)
                
                # Debug output
                if show_text_debug and self._frame_count % 60 == 0:
                    print(f"Face: ({face_x:.3f}, {face_y:.3f}) | Iris offset: ({iris_offset_x:.4f}, {iris_offset_y:.4f})")
                
                # Map to screen
                screen_x, screen_y = self.map_to_screen(face_x, face_y, iris_offset_x, iris_offset_y)
                
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
                    print(" BLINK!")
                
                # Draw debug info
                if show_debug:
                    # Draw nose (reference point)
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
                    
                    # Draw iris if available
                    if len(landmarks) > max(self.RIGHT_IRIS):
                        for iris_idx in self.RIGHT_IRIS + self.LEFT_IRIS:
                            landmark = landmarks[iris_idx]
                            x = int(landmark.x * self.cam_w)
                            y = int(landmark.y * self.cam_h)
                            cv2.circle(frame, (x, y), 3, (0, 0, 255), -1)
                    
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
            else:
                if show_debug:
                    cv2.putText(frame, "NO FACE DETECTED", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    cv2.putText(frame, f"FPS: {fps}", (10, 60),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            if show_debug:
                cv2.imshow('Eye Tracker - BlinkOS', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == ord('Q'):
                print("\n👋 Stopping...")
                break
            elif key == ord('c') or key == ord('C'):
                cursor_control_enabled = not cursor_control_enabled
                print(f"Cursor: {'ON' if cursor_control_enabled else 'OFF'}")
            elif key == ord('d') or key == ord('D'):
                show_text_debug = not show_text_debug
        
        self.cam.release()
        cv2.destroyAllWindows()
        print(" Stopped")
    
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
        print("\n Interrupted")
    except Exception as e:
        print(f"\n Error: {e}")
        import traceback
        traceback.print_exc()
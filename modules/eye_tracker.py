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
            min_detection_confidence=0.3,
            min_tracking_confidence=0.3,
            static_image_mode=False
        )
        
        # Drawing utilities for visualization
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Screen dimensions
        self.screen_w, self.screen_h = pyautogui.size()
        print(f"Screen resolution: {self.screen_w}x{self.screen_h}")
        
        # Camera setup
        self.cam = cv2.VideoCapture(0)
        if not self.cam.isOpened():
            raise Exception("Cannot open camera. Check permissions!")
        
        # Set camera properties for better performance
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Get actual camera resolution
        self.cam_w = int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.cam_h = int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"Camera resolution: {self.cam_w}x{self.cam_h}")
        
        # Eye landmark indices (MediaPipe specific)
        # Right eye landmarks
        self.RIGHT_EYE = [33, 160, 158, 133, 153, 144]
        # Left eye landmarks
        self.LEFT_EYE = [362, 385, 387, 263, 373, 380]
        
        # Iris landmarks (for more precise tracking)
        self.RIGHT_IRIS = [474, 475, 476, 477]
        self.LEFT_IRIS = [469, 470, 471, 472]
        
        # Calibration data (will be used later)
        self.is_calibrated = False
        self.calibration_data = None
        
        # FPS calculation
        self.prev_time = 0
        
        # Smoothing buffer for cursor (5 frame moving average)
        self.smooth_buffer_size = 5
        self.gaze_buffer_x = deque(maxlen=self.smooth_buffer_size)
        self.gaze_buffer_y = deque(maxlen=self.smooth_buffer_size)
        
        # Blink detection variables
        self.blink_threshold = 0.15
        self.blink_counter = 0
        self.blink_frames_required = 2
        
        # Disable PyAutoGUI failsafe (corner protection)
        pyautogui.FAILSAFE = False
        
        print("Eye Tracker initialized successfully!")
    
    def get_iris_position(self, landmarks, iris_indices, eye_indices):
        """
        Get iris center position RELATIVE to the eye boundaries
        This gives us actual gaze direction, not just face position
        
        Args:
            landmarks: Face mesh landmarks
            iris_indices: List of iris landmark indices
            eye_indices: List of eye boundary indices
            
        Returns:
            tuple: (x, y) relative position within eye (0-1 range)
        """
        # Get iris center
        iris_points = []
        for idx in iris_indices:
            point = landmarks[idx]
            iris_points.append([point.x, point.y])
        iris_center = np.mean(iris_points, axis=0)
        
        # Get eye boundaries
        eye_points = []
        for idx in eye_indices:
            point = landmarks[idx]
            eye_points.append([point.x, point.y])
        eye_points = np.array(eye_points)
        
        # Calculate eye bounds
        eye_left = np.min(eye_points[:, 0])
        eye_right = np.max(eye_points[:, 0])
        eye_top = np.min(eye_points[:, 1])
        eye_bottom = np.max(eye_points[:, 1])
        
        # Calculate relative position (0-1 range)
        eye_width = eye_right - eye_left
        eye_height = eye_bottom - eye_top
        
        if eye_width > 0 and eye_height > 0:
            relative_x = (iris_center[0] - eye_left) / eye_width
            relative_y = (iris_center[1] - eye_top) / eye_height
            
            # Clamp to 0-1 range
            relative_x = max(0, min(1, relative_x))
            relative_y = max(0, min(1, relative_y))
        else:
            relative_x, relative_y = 0.5, 0.5
        
        return relative_x, relative_y
    
    def calculate_ear(self, landmarks, eye_indices):
        """
        Calculate Eye Aspect Ratio (EAR) for blink detection
        Based on: Soukupová and Čech (2016)
        
        EAR = (||p2 - p6|| + ||p3 - p5||) / (2 * ||p1 - p4||)
        
        Args:
            landmarks: Face mesh landmarks
            eye_indices: List of eye landmark indices
            
        Returns:
            float: Eye Aspect Ratio value
        """
        # Get eye points
        points = []
        for idx in eye_indices:
            point = landmarks[idx]
            points.append([point.x, point.y, point.z])
        
        points = np.array(points)
        
        # Calculate distances
        # Vertical distances
        v1 = np.linalg.norm(points[1] - points[5])
        v2 = np.linalg.norm(points[2] - points[4])
        
        # Horizontal distance
        h = np.linalg.norm(points[0] - points[3])
        
        # EAR calculation
        ear = (v1 + v2) / (2.0 * h + 0.0001)
        
        return ear
    
    def map_to_screen(self, gaze_x, gaze_y):
        """
        Map relative gaze coordinates (0-1) to screen coordinates
        with improved sensitivity and amplification
        
        Args:
            gaze_x: Relative x coordinate (0-1, where 0.5 is center)
            gaze_y: Relative y coordinate (0-1, where 0.5 is center)
            
        Returns:
            tuple: (screen_x, screen_y) pixel coordinates
        """
        # Apply amplification for better range
        amplification_x = 2.0
        amplification_y = 2.0
        
        # Center the coordinates around 0.5
        centered_x = (gaze_x - 0.5) * amplification_x + 0.5
        centered_y = (gaze_y - 0.5) * amplification_y + 0.5
        
        # Clamp to 0-1 range
        centered_x = max(0, min(1, centered_x))
        centered_y = max(0, min(1, centered_y))
        
        # Map to screen coordinates
        screen_x = int(centered_x * self.screen_w)
        screen_y = int(centered_y * self.screen_h)
        
        # Clamp to screen bounds
        screen_x = max(0, min(screen_x, self.screen_w - 1))
        screen_y = max(0, min(screen_y, self.screen_h - 1))
        
        return screen_x, screen_y
    
    def smooth_gaze(self, x, y):
        """
        Apply moving average smoothing to gaze coordinates
        
        Args:
            x: Current x coordinate
            y: Current y coordinate
            
        Returns:
            tuple: Smoothed (x, y) coordinates
        """
        self.gaze_buffer_x.append(x)
        self.gaze_buffer_y.append(y)
        
        smooth_x = int(np.mean(self.gaze_buffer_x))
        smooth_y = int(np.mean(self.gaze_buffer_y))
        
        return smooth_x, smooth_y
    
    def detect_blink(self, ear_left, ear_right):
        """
        Detect if user is blinking based on EAR values
        
        Args:
            ear_left: EAR value for left eye
            ear_right: EAR value for right eye
            
        Returns:
            bool: True if blink detected, False otherwise
        """
        # Average EAR of both eyes
        avg_ear = (ear_left + ear_right) / 2.0
        
        # Check if below threshold
        if avg_ear < self.blink_threshold:
            self.blink_counter += 1
        else:
            # Reset if eyes are open
            if self.blink_counter >= self.blink_frames_required:
                self.blink_counter = 0
                return True
            self.blink_counter = 0
        
        return False
    
    def calculate_fps(self):
        """Calculate and return current FPS"""
        current_time = time.time()
        fps = 1 / (current_time - self.prev_time + 0.0001)
        self.prev_time = current_time
        return int(fps)
    
    def run(self, show_debug=True):
        """
        Main tracking loop
        
        Args:
            show_debug: Whether to show debug window with camera feed
        """
        print("\n Starting Eye Tracker...")
        print("Press 'Q' to quit")
        print("Press 'C' to toggle cursor control")
        print("-" * 50)
        
        cursor_control_enabled = True
        
        while True:
            # Capture frame
            ret, frame = self.cam.read()
            if not ret:
                print("Failed to grab frame")
                break
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Convert to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process with MediaPipe
            results = self.face_mesh.process(rgb_frame)
            
            # Calculate FPS
            fps = self.calculate_fps()
            
            if results.multi_face_landmarks:
                # Get face landmarks
                face_landmarks = results.multi_face_landmarks[0]
                landmarks = face_landmarks.landmark
                
                # Get iris positions RELATIVE to eye boundaries
                right_iris_x, right_iris_y = self.get_iris_position(
                    landmarks, self.RIGHT_IRIS, self.RIGHT_EYE
                )
                left_iris_x, left_iris_y = self.get_iris_position(
                    landmarks, self.LEFT_IRIS, self.LEFT_EYE
                )
                
                # Average both eyes for gaze position
                gaze_x = (right_iris_x + left_iris_x) / 2.0
                gaze_y = (right_iris_y + left_iris_y) / 2.0
                
                # Map to screen coordinates
                screen_x, screen_y = self.map_to_screen(gaze_x, gaze_y)
                
                # Apply smoothing
                smooth_x, smooth_y = self.smooth_gaze(screen_x, screen_y)
                
                # Move cursor if enabled
                if cursor_control_enabled:
                    try:
                        pyautogui.moveTo(smooth_x, smooth_y, duration=0)
                    except:
                        pass
                
                # Calculate EAR for blink detection
                ear_right = self.calculate_ear(landmarks, self.RIGHT_EYE)
                ear_left = self.calculate_ear(landmarks, self.LEFT_EYE)
                
                # Detect blink
                if self.detect_blink(ear_left, ear_right):
                    print(" BLINK DETECTED!")
                
                # Draw on frame if debug mode
                if show_debug:
                    # Draw iris landmarks (faster than full mesh)
                    self.mp_drawing.draw_landmarks(
                        image=frame,
                        landmark_list=face_landmarks,
                        connections=self.mp_face_mesh.FACEMESH_IRISES,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_iris_connections_style()
                    )
                    
                    # Draw eye points
                    for eye_idx in self.RIGHT_EYE + self.LEFT_EYE:
                        landmark = landmarks[eye_idx]
                        x = int(landmark.x * self.cam_w)
                        y = int(landmark.y * self.cam_h)
                        cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
                    
                    # Draw iris points
                    for iris_idx in self.RIGHT_IRIS + self.LEFT_IRIS:
                        landmark = landmarks[iris_idx]
                        x = int(landmark.x * self.cam_w)
                        y = int(landmark.y * self.cam_h)
                        cv2.circle(frame, (x, y), 2, (0, 0, 255), -1)
                    
                    # Display info
                    cv2.putText(frame, f"FPS: {fps}", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame, f"Gaze: ({smooth_x}, {smooth_y})", (10, 60),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame, f"EAR: {(ear_left + ear_right)/2:.3f}", (10, 90),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame, f"Cursor: {'ON' if cursor_control_enabled else 'OFF'}", (10, 120),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0) if cursor_control_enabled else (0, 0, 255), 2)
            
            else:
                # No face detected
                if show_debug:
                    cv2.putText(frame, "NO FACE DETECTED", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    cv2.putText(frame, f"FPS: {fps}", (10, 60),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Show debug window
            if show_debug:
                cv2.imshow('Eye Tracker - BlinkOS', frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == ord('Q'):
                print("\n Stopping Eye Tracker...")
                break
            elif key == ord('c') or key == ord('C'):
                cursor_control_enabled = not cursor_control_enabled
                print(f"Cursor control: {'ENABLED' if cursor_control_enabled else 'DISABLED'}")
        
        # Cleanup
        self.cam.release()
        cv2.destroyAllWindows()
        print(" Eye Tracker stopped")
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        if hasattr(self, 'cam') and self.cam.isOpened():
            self.cam.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    """Test the eye tracker directly"""
    try:
        tracker = EyeTracker()
        tracker.run(show_debug=True)
    except KeyboardInterrupt:
        print("\n\n Interrupted by user")
    except Exception as e:
        print(f"\n Error: {e}")
        import traceback
        traceback.print_exc()
#!/usr/bin/env python3
"""
Calibration Module - 9-point calibration for eye tracking
Creates precise mapping between face position and screen coordinates
""" 
"""Uses poly reg to create a non - linear mapping between face position and screen position 
so that I can have the comeplete access to the screen with the right movement of my setup """

import cv2
import numpy as np
import pickle
import os
import time


class Calibration:
    """
    Calibration system for eye tracking
    Uses 9-point calibration to create accurate face->screen mapping
    """
    
    def __init__(self, screen_w, screen_h, save_path='data/calibration.pkl'):
        """
        Initialize calibration
        
        Args:
            screen_w: Screen width in pixels
            screen_h: Screen height in pixels
            save_path: Path to save calibration data
        """
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.save_path = save_path
        
        # Create data directory if needed
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Calibration points (normalized 0-1)
        # 9-point grid: corners, edges, center
        self.calibration_points = [
            (0.1, 0.1),   # Top-left
            (0.5, 0.1),   # Top-center
            (0.9, 0.1),   # Top-right
            (0.1, 0.5),   # Middle-left
            (0.5, 0.5),   # Center
            (0.9, 0.5),   # Middle-right
            (0.1, 0.9),   # Bottom-left
            (0.5, 0.9),   # Bottom-center
            (0.9, 0.9),   # Bottom-right
        ]
        
        # Collected data
        self.face_positions = []
        self.screen_positions = []
        
        # Transformation parameters
        self.transform_matrix = None
        self.is_calibrated = False
        
        # Colors for UI
        self.color_inactive = (100, 100, 100)
        self.color_active = (0, 255, 0)
        self.color_completed = (0, 0, 255)
        
    def draw_calibration_point(self, img, point_idx, is_active=False, is_completed=False):
        """
        Draw a calibration point on the screen
        
        Args:
            img: Image to draw on
            point_idx: Index of calibration point
            is_active: Whether this is the current point
            is_completed: Whether this point is completed
        """
        if point_idx >= len(self.calibration_points):
            return
        
        norm_x, norm_y = self.calibration_points[point_idx]
        x = int(norm_x * img.shape[1])
        y = int(norm_y * img.shape[0])
        
        # Choose color
        if is_completed:
            color = self.color_completed
        elif is_active:
            color = self.color_active
        else:
            color = self.color_inactive
        
        # Draw outer circle
        cv2.circle(img, (x, y), 50, color, 3)
        
        # Draw inner circle
        cv2.circle(img, (x, y), 20, color, -1)
        
        # Draw crosshair if active
        if is_active:
            cv2.line(img, (x - 60, y), (x + 60, y), color, 2)
            cv2.line(img, (x, y - 60), (x, y + 60), color, 2)
            
            # Pulsing animation
            pulse_radius = int(30 + 10 * np.sin(time.time() * 5))
            cv2.circle(img, (x, y), pulse_radius, color, 2)
    
    def run_calibration(self, face_mesh, cam):
        """
        Run the calibration process
        
        Args:
            face_mesh: MediaPipe FaceMesh instance
            cam: Camera capture object
            
        Returns:
            bool: True if calibration successful
        """
        print("\n" + "="*60)
        print("CALIBRATION MODE")
        print("="*60)
        print("\nInstructions:")
        print("1. Look at each GREEN circle as it appears")
        print("2. Keep your head still and centered")
        print("3. Press SPACE when looking at the circle")
        print("4. Press ESC to cancel calibration")
        print("\nReady? Press SPACE to start...")
        print("="*60 + "\n")
        
        # Wait for user to be ready
        ready = False
        while not ready:
            ret, frame = cam.read()
            if not ret:
                return False
            
            frame = cv2.flip(frame, 1)
            
            # Show instruction screen
            instruction_img = np.zeros((self.screen_h, self.screen_w, 3), dtype=np.uint8)
            
            # Title
            cv2.putText(instruction_img, "CALIBRATION", 
                       (self.screen_w//2 - 200, 100),
                       cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
            
            # Instructions
            instructions = [
                "Look at each green circle",
                "Keep your head still",
                "Press SPACE when looking at circle",
                "",
                "Press SPACE to start",
                "Press ESC to cancel"
            ]
            
            y_pos = 250
            for instruction in instructions:
                cv2.putText(instruction_img, instruction,
                           (self.screen_w//2 - 250, y_pos),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 2)
                y_pos += 60
            
            cv2.imshow('Calibration', instruction_img)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord(' '):
                ready = True
            elif key == 27:  # ESC
                print("Calibration cancelled")
                cv2.destroyWindow('Calibration')
                return False
        
        # Run calibration for each point
        self.face_positions = []
        self.screen_positions = []
        
        for point_idx, (norm_x, norm_y) in enumerate(self.calibration_points):
            screen_x = int(norm_x * self.screen_w)
            screen_y = int(norm_y * self.screen_h)
            
            print(f"\nPoint {point_idx + 1}/9: Look at the GREEN circle")
            
            # Collect samples for this point
            samples = []
            collecting = True
            
            while collecting:
                ret, frame = cam.read()
                if not ret:
                    return False
                
                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = face_mesh.process(rgb_frame)
                
                # Create calibration display
                calib_img = np.zeros((self.screen_h, self.screen_w, 3), dtype=np.uint8)
                
                # Draw all points
                for i in range(len(self.calibration_points)):
                    is_active = (i == point_idx)
                    is_completed = (i < point_idx)
                    self.draw_calibration_point(calib_img, i, is_active, is_completed)
                
                # Instructions
                cv2.putText(calib_img, f"Point {point_idx + 1} / 9",
                           (self.screen_w//2 - 100, 50),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                
                cv2.putText(calib_img, "Press SPACE when looking at green circle",
                           (self.screen_w//2 - 300, self.screen_h - 50),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 2)
                
                # Show face detection status
                if results.multi_face_landmarks:
                    landmarks = results.multi_face_landmarks[0].landmark
                    nose = landmarks[1]
                    face_x, face_y = nose.x, nose.y
                    
                    cv2.putText(calib_img, "Face detected",
                               (20, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                else:
                    cv2.putText(calib_img, "No face detected!",
                               (20, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                cv2.imshow('Calibration', calib_img)
                
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord(' ') and results.multi_face_landmarks:
                    # Collect sample
                    landmarks = results.multi_face_landmarks[0].landmark
                    nose = landmarks[1]
                    face_x, face_y = nose.x, nose.y
                    
                    samples.append((face_x, face_y))
                    
                    # Need 3 samples per point for stability
                    if len(samples) >= 3:
                        # Average samples
                        avg_face_x = np.mean([s[0] for s in samples])
                        avg_face_y = np.mean([s[1] for s in samples])
                        
                        self.face_positions.append([avg_face_x, avg_face_y])
                        self.screen_positions.append([screen_x, screen_y])
                        
                        print(f"Point {point_idx + 1} calibrated: face=({avg_face_x:.3f}, {avg_face_y:.3f})")
                        
                        collecting = False
                    else:
                        print(f"   Sample {len(samples)}/3 collected")
                
                elif key == 27:  # ESC
                    print("Calibration cancelled")
                    cv2.destroyWindow('Calibration')
                    return False
        
        cv2.destroyWindow('Calibration')
        
        # Calculate transformation
        print("\nCalculating transformation matrix...")
        success = self.calculate_transformation()
        
        if success:
            print("Calibration complete!")
            self.save_calibration()
            return True
        else:
            print("Calibration failed - please try again")
            return False
    
    def calculate_transformation(self):
        """
        Calculate transformation matrix from face positions to screen coordinates
        Uses polynomial regression for non-linear mapping
        
        Returns:
            bool: True if successful
        """
        if len(self.face_positions) < 9:
            return False
        
        face_array = np.array(self.face_positions)
        screen_array = np.array(self.screen_positions)
        
        # Create polynomial features for better accuracy
        # [1, x, y, x^2, xy, y^2, x^3, x^2*y, x*y^2, y^3]
        def create_features(positions):
            x = positions[:, 0]
            y = positions[:, 1]
            return np.column_stack([
                np.ones_like(x),  # bias
                x, y,              # linear
                x**2, x*y, y**2,   # quadratic
                x**3, x**2*y, x*y**2, y**3  # cubic
            ])
        
        X = create_features(face_array)
        
        # Solve for transformation (separate for x and y)
        self.transform_matrix_x = np.linalg.lstsq(X, screen_array[:, 0], rcond=None)[0]
        self.transform_matrix_y = np.linalg.lstsq(X, screen_array[:, 1], rcond=None)[0]
        
        self.is_calibrated = True
        
        # Test accuracy
        predicted = self.apply_calibration(face_array)
        error = np.mean(np.sqrt(np.sum((predicted - screen_array)**2, axis=1)))
        print(f"Calibration accuracy: {error:.1f} pixels average error")
        
        return True
    
    def apply_calibration(self, face_positions):
        """
        Apply calibration to face positions
        
        Args:
            face_positions: Nx2 array of face positions (normalized)
            
        Returns:
            Nx2 array of screen coordinates
        """
        if not self.is_calibrated:
            # No calibration - use simple linear mapping
            return face_positions * [self.screen_w, self.screen_h]
        
        # Handle single position
        if face_positions.ndim == 1:
            face_positions = face_positions.reshape(1, -1)
        
        # Create polynomial features
        x = face_positions[:, 0]
        y = face_positions[:, 1]
        X = np.column_stack([
            np.ones_like(x),
            x, y,
            x**2, x*y, y**2,
            x**3, x**2*y, x*y**2, y**3
        ])
        
        # Apply transformation
        screen_x = X @ self.transform_matrix_x
        screen_y = X @ self.transform_matrix_y
        
        # Clamp to screen bounds
        screen_x = np.clip(screen_x, 0, self.screen_w - 1)
        screen_y = np.clip(screen_y, 0, self.screen_h - 1)
        
        return np.column_stack([screen_x, screen_y])
    
    def save_calibration(self):
        """Save calibration data to file"""
        data = {
            'face_positions': self.face_positions,
            'screen_positions': self.screen_positions,
            'transform_matrix_x': self.transform_matrix_x,
            'transform_matrix_y': self.transform_matrix_y,
            'screen_w': self.screen_w,
            'screen_h': self.screen_h,
            'is_calibrated': self.is_calibrated
        }
        
        with open(self.save_path, 'wb') as f:
            pickle.dump(data, f)
        
        print(f"Calibration saved to {self.save_path}")
    
    def load_calibration(self):
        """
        Load calibration from file
        
        Returns:
            bool: True if loaded successfully
        """
        if not os.path.exists(self.save_path):
            print(f"No calibration file found at {self.save_path}")
            return False
        
        try:
            with open(self.save_path, 'rb') as f:
                data = pickle.load(f)
            
            self.face_positions = data['face_positions']
            self.screen_positions = data['screen_positions']
            self.transform_matrix_x = data['transform_matrix_x']
            self.transform_matrix_y = data['transform_matrix_y']
            self.screen_w = data['screen_w']
            self.screen_h = data['screen_h']
            self.is_calibrated = data['is_calibrated']
            
            print(f"Calibration loaded from {self.save_path}")
            return True
            
        except Exception as e:
            print(f"Error loading calibration: {e}")
            return False


if __name__ == "__main__":
    """Test calibration standalone"""
    import mediapipe as mp
    import pyautogui
    
    print("Calibration Test")
    
    screen_w, screen_h = pyautogui.size()
    
    # Setup camera
    cam = cv2.VideoCapture(0)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # Setup face mesh
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    # Run calibration
    calib = Calibration(screen_w, screen_h)
    success = calib.run_calibration(face_mesh, cam)
    
    if success:
        print("\nCalibration successful!")
        print("Test by moving your head - cursor should follow accurately")
    else:
        print("\nCalibration failed")
    
    cam.release()
    cv2.destroyAllWindows()
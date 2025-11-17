#!/usr/bin/env python3
"""
Calibration Module - Enhanced 9-point calibration
Creates precise mapping with visual progress indicators and quality assessment
"""

import cv2
import numpy as np
import pickle
import os
import time


class Calibration:
    """
    Enhanced calibration system with visual feedback and quality assessment
    """
    
    def __init__(self, screen_w, screen_h, save_path='data/calibration.pkl'):
        """Initialize calibration"""
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.save_path = save_path
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # 9-point calibration grid
        self.calibration_points = [
            (0.1, 0.1),   # 1. Top-left
            (0.5, 0.1),   # 2. Top-center
            (0.9, 0.1),   # 3. Top-right
            (0.1, 0.5),   # 4. Middle-left
            (0.5, 0.5),   # 5. Center
            (0.9, 0.5),   # 6. Middle-right
            (0.1, 0.9),   # 7. Bottom-left
            (0.5, 0.9),   # 8. Bottom-center
            (0.9, 0.9),   # 9. Bottom-right
        ]
        
        # Collected data
        self.face_positions = []
        self.screen_positions = []
        
        # Calibration quality metrics
        self.calibration_quality = 0.0  # 0.0 to 1.0
        self.is_calibrated = False
        
        # Tuning parameters
        self.range_expansion = 1.15
        self.smoothing_factor = 0.1
        self.corner_boost = 1.1
        self.edge_threshold = 0.15
        
        # Visual settings
        self.color_inactive = (100, 100, 100)
        self.color_active = (0, 255, 0)
        self.color_completed = (0, 200, 255)
        self.color_current = (0, 255, 255)
        
        # Animation
        self.animation_time = 0
    
    def draw_progress_bar(self, img, current_point, total_points):
        """Draw calibration progress bar"""
        bar_x = 50
        bar_y = self.screen_h - 100
        bar_w = self.screen_w - 100
        bar_h = 30
        
        # Background
        cv2.rectangle(img, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h),
                     (60, 60, 60), -1)
        
        # Progress fill
        progress = current_point / total_points
        fill_w = int(bar_w * progress)
        cv2.rectangle(img, (bar_x, bar_y), (bar_x + fill_w, bar_y + bar_h),
                     (0, 255, 0), -1)
        
        # Border
        cv2.rectangle(img, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h),
                     (200, 200, 200), 2)
        
        # Progress text
        progress_text = f"{current_point}/{total_points} Points"
        text_size = cv2.getTextSize(progress_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
        text_x = bar_x + (bar_w - text_size[0]) // 2
        text_y = bar_y + (bar_h + text_size[1]) // 2
        cv2.putText(img, progress_text, (text_x, text_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Percentage
        percent_text = f"{int(progress * 100)}%"
        cv2.putText(img, percent_text, (bar_x + bar_w + 20, bar_y + 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    def draw_calibration_point(self, img, point_idx, is_active=False, is_completed=False):
        """Draw a calibration point with number"""
        if point_idx >= len(self.calibration_points):
            return
        
        norm_x, norm_y = self.calibration_points[point_idx]
        x = int(norm_x * img.shape[1])
        y = int(norm_y * img.shape[0])
        
        # Choose color
        if is_completed:
            color = self.color_completed
            outer_radius = 40
            inner_radius = 15
        elif is_active:
            color = self.color_current
            # Pulsing animation
            pulse = int(10 * np.sin(time.time() * 5))
            outer_radius = 50 + pulse
            inner_radius = 20
        else:
            color = self.color_inactive
            outer_radius = 35
            inner_radius = 12
        
        # Draw outer circle
        cv2.circle(img, (x, y), outer_radius, color, 3)
        
        # Draw inner circle
        cv2.circle(img, (x, y), inner_radius, color, -1)
        
        # Draw crosshair for active point
        if is_active:
            line_len = outer_radius + 20
            cv2.line(img, (x - line_len, y), (x + line_len, y), color, 2)
            cv2.line(img, (x, y - line_len), (x, y + line_len), color, 2)
            
            # Draw instruction
            instruction = "Look here & press SPACE"
            text_size = cv2.getTextSize(instruction, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            text_x = x - text_size[0] // 2
            text_y = y + outer_radius + 40
            
            # Text background
            cv2.rectangle(img, (text_x - 10, text_y - 25),
                         (text_x + text_size[0] + 10, text_y + 5),
                         (40, 40, 40), -1)
            
            cv2.putText(img, instruction, (text_x, text_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Draw point number
        point_num = str(point_idx + 1)
        text_size = cv2.getTextSize(point_num, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
        text_x = x - text_size[0] // 2
        text_y = y + text_size[1] // 2
        
        if is_completed:
            # Checkmark for completed points
            cv2.putText(img, "✓", (text_x, text_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        else:
            cv2.putText(img, point_num, (text_x, text_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    def calculate_calibration_quality(self):
        """
        Calculate calibration quality based on coverage and consistency
        Returns: Quality score 0.0 to 1.0
        """
        if len(self.face_positions) < 9:
            return 0.0
        
        face_array = np.array(self.face_positions)
        
        # Check coverage (how much of the face movement range is used)
        range_x = np.max(face_array[:, 0]) - np.min(face_array[:, 0])
        range_y = np.max(face_array[:, 1]) - np.min(face_array[:, 1])
        
        # Good coverage should use at least 40% of the camera view
        coverage_score = min(1.0, (range_x + range_y) / 0.8)
        
        # Check consistency (how linear/smooth the mapping is)
        # Calculate variance in distances between adjacent points
        distances = []
        for i in range(len(face_array) - 1):
            dist = np.linalg.norm(face_array[i] - face_array[i + 1])
            distances.append(dist)
        
        if len(distances) > 0:
            consistency_score = 1.0 - min(1.0, np.std(distances) / np.mean(distances))
        else:
            consistency_score = 0.5
        
        # Overall quality (weighted average)
        quality = 0.7 * coverage_score + 0.3 * consistency_score
        
        return quality
    
    def run_calibration(self, face_mesh, cam):
        """Run the enhanced calibration process"""
        print("\n" + "="*60)
        print(" ENHANCED CALIBRATION MODE")
        print("="*60)
        print("\n Instructions:")
        print("  1. Look at each GREEN circle as it appears")
        print("  2. Keep your head still and centered on each point")
        print("  3. Press SPACE when looking directly at the circle")
        print("  4. Press ESC to cancel calibration")
        print("\n TIP: Move your ENTIRE HEAD, not just your eyes!")
        print("="*60 + "\n")
        
        # Wait for ready
        ready = False
        while not ready:
            ret, frame = cam.read()
            if not ret:
                return False
            
            frame = cv2.flip(frame, 1)
            
            # Instruction screen
            instruction_img = np.zeros((self.screen_h, self.screen_w, 3), dtype=np.uint8)
            
            # Title with glow effect
            title = "CALIBRATION"
            cv2.putText(instruction_img, title, 
                       (self.screen_w//2 - 220, 120),
                       cv2.FONT_HERSHEY_SIMPLEX, 2.5, (100, 100, 100), 8)
            cv2.putText(instruction_img, title, 
                       (self.screen_w//2 - 220, 120),
                       cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 255, 0), 3)
            
            # Instructions box
            box_x, box_y = 200, 220
            box_w, box_h = self.screen_w - 400, 400
            
            cv2.rectangle(instruction_img, (box_x, box_y), (box_x + box_w, box_y + box_h),
                         (50, 50, 50), -1)
            cv2.rectangle(instruction_img, (box_x, box_y), (box_x + box_w, box_y + box_h),
                         (0, 255, 0), 3)
            
            instructions = [
                "1. Look at each numbered circle",
                "2. Move your HEAD (not just eyes)",
                "3. Press SPACE when centered",
                "4. Complete all 9 points",
                "",
                "Press SPACE to start",
                "Press ESC to cancel"
            ]
            
            y_pos = box_y + 60
            for instruction in instructions:
                if instruction == "":
                    y_pos += 20
                    continue
                    
                color = (255, 255, 255) if not instruction.startswith("Press") else (0, 255, 255)
                cv2.putText(instruction_img, instruction,
                           (box_x + 40, y_pos),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                y_pos += 50
            
            cv2.imshow('Calibration', instruction_img)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord(' '):
                ready = True
            elif key == 27:
                print(" Calibration cancelled")
                cv2.destroyWindow('Calibration')
                return False
        
        # Run calibration for each point
        self.face_positions = []
        self.screen_positions = []
        
        for point_idx, (norm_x, norm_y) in enumerate(self.calibration_points):
            screen_x = int(norm_x * self.screen_w)
            screen_y = int(norm_y * self.screen_h)
            
            print(f"\nPoint {point_idx + 1}/9: Look at the circle...")
            
            samples = []
            collecting = True
            show_countdown = False
            countdown_start = 0
            
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
                
                # Draw progress bar
                self.draw_progress_bar(calib_img, point_idx, len(self.calibration_points))
                
                # Title
                cv2.putText(calib_img, f"Point {point_idx + 1} of 9",
                           (self.screen_w//2 - 120, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
                
                # Face detection status
                if results.multi_face_landmarks:
                    landmarks = results.multi_face_landmarks[0].landmark
                    nose = landmarks[1]
                    face_x, face_y = nose.x, nose.y
                    
                    status_color = (0, 255, 0)
                    status_text = "✓ Face detected - Press SPACE"
                else:
                    status_color = (0, 0, 255)
                    status_text = "⚠ No face detected!"
                
                # Status box
                status_y = self.screen_h - 180
                cv2.rectangle(calib_img, (100, status_y - 10), 
                             (self.screen_w - 100, status_y + 40),
                             (40, 40, 40), -1)
                
                text_size = cv2.getTextSize(status_text, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)[0]
                text_x = (self.screen_w - text_size[0]) // 2
                cv2.putText(calib_img, status_text, (text_x, status_y + 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.9, status_color, 2)
                
                cv2.imshow('Calibration', calib_img)
                
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord(' ') and results.multi_face_landmarks:
                    # Collect sample
                    landmarks = results.multi_face_landmarks[0].landmark
                    nose = landmarks[1]
                    face_x, face_y = nose.x, nose.y
                    
                    samples.append((face_x, face_y))
                    
                    if len(samples) >= 3:
                        # Average samples
                        avg_face_x = np.mean([s[0] for s in samples])
                        avg_face_y = np.mean([s[1] for s in samples])
                        
                        self.face_positions.append([avg_face_x, avg_face_y])
                        self.screen_positions.append([screen_x, screen_y])
                        
                        print(f"Point {point_idx + 1} calibrated!")
                        
                        # Brief pause with visual feedback
                        success_img = calib_img.copy()
                        cv2.putText(success_img, "✓ CAPTURED!", 
                                   (self.screen_w//2 - 100, self.screen_h//2),
                                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 4)
                        cv2.imshow('Calibration', success_img)
                        cv2.waitKey(500)
                        
                        collecting = False
                    else:
                        print(f"Sample {len(samples)}/3 collected")
                
                elif key == 27:
                    print(" Calibration cancelled")
                    cv2.destroyWindow('Calibration')
                    return False
        
        # Calibration complete - show results
        self.is_calibrated = True
        self.calibration_quality = self.calculate_calibration_quality()
        
        print(f"\n Calibration complete!")
        print(f" Quality Score: {self.calibration_quality * 100:.1f}%")
        
        # Show completion screen
        completion_img = np.zeros((self.screen_h, self.screen_w, 3), dtype=np.uint8)
        
        # Success message
        cv2.putText(completion_img, "CALIBRATION COMPLETE!", 
                   (self.screen_w//2 - 280, self.screen_h//2 - 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 4)
        
        # Quality indicator
        quality_text = f"Quality: {int(self.calibration_quality * 100)}%"
        quality_color = (0, 255, 0) if self.calibration_quality > 0.7 else (0, 255, 255)
        cv2.putText(completion_img, quality_text,
                   (self.screen_w//2 - 120, self.screen_h//2),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, quality_color, 3)
        
        # Recommendation
        if self.calibration_quality > 0.7:
            recommendation = "Excellent! Cursor control will be accurate."
        elif self.calibration_quality > 0.5:
            recommendation = "Good! You can recalibrate for better accuracy."
        else:
            recommendation = "Consider recalibrating for better results."
        
        cv2.putText(completion_img, recommendation,
                   (self.screen_w//2 - 300, self.screen_h//2 + 80),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
        
        cv2.putText(completion_img, "Press any key to continue...",
                   (self.screen_w//2 - 180, self.screen_h//2 + 140),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (150, 150, 150), 2)
        
        cv2.imshow('Calibration', completion_img)
        cv2.waitKey(0)
        cv2.destroyWindow('Calibration')
        
        self.save_calibration()
        return True
    
    def apply_calibration(self, face_positions):
        """Apply calibration with tunable parameters"""
        if not self.is_calibrated:
            return face_positions * [self.screen_w, self.screen_h]
        
        if face_positions.ndim == 1:
            face_positions = face_positions.reshape(1, -1)
        
        x = face_positions[:, 0]
        y = face_positions[:, 1]
        
        # Use calibration data
        face_array = np.array(self.face_positions)
        face_min_x = np.min(face_array[:, 0])
        face_max_x = np.max(face_array[:, 0])
        face_min_y = np.min(face_array[:, 1])
        face_max_y = np.max(face_array[:, 1])
        
        face_range_x = face_max_x - face_min_x
        face_range_y = face_max_y - face_min_y
        
        # Apply range expansion
        face_center_x = (face_max_x + face_min_x) / 2
        face_center_y = (face_max_y + face_min_y) / 2
        
        expanded_min_x = face_center_x - (face_range_x * self.range_expansion / 2)
        expanded_max_x = face_center_x + (face_range_x * self.range_expansion / 2)
        expanded_min_y = face_center_y - (face_range_y * self.range_expansion / 2)
        expanded_max_y = face_center_y + (face_range_y * self.range_expansion / 2)
        
        # Map to normalized 0-1
        norm_x = (x - expanded_min_x) / (expanded_max_x - expanded_min_x + 0.001)
        norm_y = (y - expanded_min_y) / (expanded_max_y - expanded_min_y + 0.001)
        
        norm_x = np.clip(norm_x, 0, 1)
        norm_y = np.clip(norm_y, 0, 1)
        
        # Apply corner boost
        if self.corner_boost != 1.0:
            near_left = norm_x < self.edge_threshold
            near_right = norm_x > (1 - self.edge_threshold)
            near_top = norm_y < self.edge_threshold
            near_bottom = norm_y > (1 - self.edge_threshold)
            
            boost_x = np.where(near_left | near_right,
                              (norm_x - 0.5) * self.corner_boost + 0.5,
                              norm_x)
            boost_y = np.where(near_top | near_bottom,
                              (norm_y - 0.5) * self.corner_boost + 0.5,
                              norm_y)
            
            norm_x = boost_x
            norm_y = boost_y
            norm_x = np.clip(norm_x, 0, 1)
            norm_y = np.clip(norm_y, 0, 1)
        
        # Map to screen
        screen_x = norm_x * self.screen_w
        screen_y = norm_y * self.screen_h
        
        # Apply smoothing
        if self.smoothing_factor > 0:
            simple_x = x * self.screen_w
            simple_y = y * self.screen_h
            
            screen_x = (1 - self.smoothing_factor) * screen_x + self.smoothing_factor * simple_x
            screen_y = (1 - self.smoothing_factor) * screen_y + self.smoothing_factor * simple_y
        
        screen_x = np.clip(screen_x, 0, self.screen_w - 1)
        screen_y = np.clip(screen_y, 0, self.screen_h - 1)
        
        return np.column_stack([screen_x, screen_y])
    
    def save_calibration(self):
        """Save calibration data"""
        data = {
            'face_positions': self.face_positions,
            'screen_positions': self.screen_positions,
            'screen_w': self.screen_w,
            'screen_h': self.screen_h,
            'is_calibrated': self.is_calibrated,
            'calibration_quality': self.calibration_quality,
            'range_expansion': self.range_expansion,
            'smoothing_factor': self.smoothing_factor,
            'corner_boost': self.corner_boost,
            'edge_threshold': self.edge_threshold,
        }
        
        with open(self.save_path, 'wb') as f:
            pickle.dump(data, f)
        
        print(f"Calibration saved to {self.save_path}")
    
    def load_calibration(self):
        """Load calibration from file"""
        if not os.path.exists(self.save_path):
            print(f"  No calibration file found at {self.save_path}")
            return False
        
        try:
            with open(self.save_path, 'rb') as f:
                data = pickle.load(f)
            
            self.face_positions = data['face_positions']
            self.screen_positions = data['screen_positions']
            self.screen_w = data['screen_w']
            self.screen_h = data['screen_h']
            self.is_calibrated = data['is_calibrated']
            self.calibration_quality = data.get('calibration_quality', 0.8)
            
            self.range_expansion = data.get('range_expansion', 1.15)
            self.smoothing_factor = data.get('smoothing_factor', 0.1)
            self.corner_boost = data.get('corner_boost', 1.1)
            self.edge_threshold = data.get('edge_threshold', 0.15)
            
            print(f" Calibration loaded (Quality: {int(self.calibration_quality * 100)}%)")
            return True
            
        except Exception as e:
            print(f" Error loading calibration: {e}")
            return False


if __name__ == "__main__":
    """Test calibration"""
    import mediapipe as mp
    import pyautogui
    
    print("\n Calibration Test Mode")
    
    screen_w, screen_h = pyautogui.size()
    
    cam = cv2.VideoCapture(0)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    calib = Calibration(screen_w, screen_h)
    success = calib.run_calibration(face_mesh, cam)
    
    if success:
        print("\nCalibration successful!")
    else:
        print("\n Calibration failed")
    
    cam.release()
    cv2.destroyAllWindows()
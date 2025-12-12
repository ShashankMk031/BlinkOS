"""
Error handling module- Centralized error handling and recovery mechanisms. 
"""

import sys 
import traceback 
import platform 
import subprocess 
from datetime import datetime 

class ErrorHandler:
    """ 
    Centralized errror handling sysstem"""
    
    def __init__(self,logger=None):
        # Initialize 
        self.logger = logger 
        self.error_count = 0 
        self.last_error = None 
    
    def handle_error(self,error,context="Unknown",fatal=False):
        """ 
        Handle an error with context 
        
        args: 
            error:Exception object 
            context: Where the error occurred 
            fatal : If True , exit after handling 
        """
        self.error_count +=1 
        self.last_error = error 
        
        error_msg = f"Error in {context}:{str(error)}" 
        
        # Logging 
        if self.logger:
            self.logger.error(error_msg) 
            self.logger.error(traceback.format_exc()) 
        
        # Print to console 
        print(f"\nERROR in {context} ")
        print(f"    {str(error)}")
        
        if fatal:
            print("Fatal error encountered. Exiting...")
            sys.exit(1) 
    
    def check_camera_permission(self):
        """ 
        Check if camera access is available
        
        returns :  
        tuple: (bool: has_permission, str:error_message)
        """ 
        try: 
            import cv2 
            cam = cv2.VideoCapture(0) 
            
            if not cam.isOpened():
                return False, "Camera not accessible. Check permissions in System Preferences > Security & Privacy > Camera"
            
            ret,frame = cam.read() 
            cam.release() 
            
            if not ret: 
                return False, "Camera opened but cannot read frame. Try restarting the application / computer."
            
            return True, "Camera access OK" 
        
        except Exception as e:
            return False, f"Camera check failed : {str(e)}"
    
    def check_microphone_permission(self): 
        """ 
        Check if microphone access is available 
        
        returns: 
        tuple: (bool: has_permission, str:error_message)
        """ 
        # region agent log
        import json
        import time
        log_path = "/Users/shashankmk/Documents/Projects-Development/BlinkOS + SurveyAI/.cursor/debug.log"
        def write_log(hypothesis_id, location, message, data):
            payload = {
                "sessionId": "debug-session",
                "runId": "mic-permission-check",
                "hypothesisId": hypothesis_id,
                "location": location,
                "message": message,
                "data": data,
                "timestamp": int(time.time() * 1000),
            }
            try:
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(payload, ensure_ascii=True) + "\n")
            except:
                pass
        # endregion
        
        try: 
            # region agent log
            write_log("H1", "error_handler.py:81", "Starting microphone permission check", {})
            # endregion
            
            import speech_recognition as sr 
            recognizer = sr.Recognizer()
            
            # region agent log
            write_log("H2", "error_handler.py:85", "Creating Microphone object", {})
            # endregion
            
            with sr.Microphone() as source: 
                # region agent log
                write_log("H3", "error_handler.py:88", "Before adjust_for_ambient_noise", {})
                # endregion
                
                recognizer.adjust_for_ambient_noise(source, duration=0.5) 
                
                # region agent log
                write_log("H4", "error_handler.py:91", "After adjust_for_ambient_noise - success", {})
                # endregion
                
            return True, "Microphone access OK"
        
        except Exception as e: 
            # region agent log
            import traceback
            write_log("H5", "error_handler.py:96", "Microphone check exception caught", {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "error_repr": repr(e),
                "traceback": traceback.format_exc()[:500],
            })
            # endregion
            
            erroe_msg = str(e) 
            
            # Check for dependency issues first
            if "distutils" in erroe_msg or "ModuleNotFoundError" in str(type(e).__name__):
                return False, f"Missing dependency: {erroe_msg}. Try: pip install setuptools"
            elif "list index out of range" in erroe_msg or "No Default Input Device" in erroe_msg:
                return False, "No microphone detected. Check microphone connection."
            else: 
                return False, f"Microphone access denied. Check permission in  System Preferences > Security & Privacy > Microphone"
    
    def check_dependencies(self):
        """Check required dependencies"""
        required = {
            'cv2': 'opencv-python',
            'mediapipe': 'mediapipe',
            'pyautogui': 'pyautogui',
            'speech_recognition': 'SpeechRecognition',
            'numpy': 'numpy'
        }
        
        missing = []
        
        for module, package in required.items():
            try:
                __import__(module)
            except ImportError:
                missing.append(package)
        
        # Check pyttsx3 separately (optional)
        try:
            __import__('pyttsx3')
        except ImportError:
            print("  Note: pyttsx3 not found (optional - only needed for TTS)")
        
        if missing:
            return False, missing
        
        return True, []
    
    def get_system_info(self):
        """ 
        Get the system information for debugging
        returns: 
        dict:System information 
        """ 
        info = { 
            'platform':platform.system(), 
            'platform_version':platform.version(),
            'architecture':platform.machine(),
            'python_version':sys.version,
            }
        
        return info 
    
    def show_permission_instructions(self,permission_type):
        """ 
        SHow instruction for granting permissions 
        
        args : 
            permission_type : 'camera' or 'microphone'
        """
        if platform.system() != 'Darwin': 
            print(f"\n Please grant {permission_type} permission to this application.")
            return 
        
        print(f"\n{permission_type.upper()} PERMISSION REQUIRED")
        print('='*60)
        print(f"\n To grant {permission_type} acess: ") 
        print("1. Open System Preferences")
        print("2. Go to Security & Privacy")
        print(f"3. Click on {permission_type.capitalize()}")
        print("4. Check the box next to Terminal (or your terminal app)")
        print("5. Restart this application")
        print("\nOR run from command line:")
        print("  python3 main.py")
        print("="*60 + "\n")
        
    def check_all_permissions(self, require_microphone=True): 
        """ 
        Check all required permissions 
        
        args:
            require_microphone: If False, microphone check is optional (for eye tracker)
        
        returns: 
            bool: True if all required permissions OK 
        """ 
        
        all_ok = True 
        
        # Checks camera 
        camera_ok , camera_msg = self.check_camera_permission() 
        if camera_ok: 
            print("Camera permission: OK") 
        else: 
            print(f"Camera permission: FAILED - {camera_msg}" )
            self.show_permission_instructions('camera') 
            all_ok = False 
        
        # Check microphone (optional for eye tracker)
        mic_ok, mic_msg = self.check_microphone_permission() 
        if mic_ok: 
            print("Microphone permission: OK") 
        else: 
            if require_microphone:
                print(f"Microphone permission: FAILED - {mic_msg}")
                # Only show permission instructions if it's actually a permission issue
                if "permission" in mic_msg.lower() or "Security & Privacy" in mic_msg:
                    self.show_permission_instructions('microphone')
                all_ok = False
            else:
                # Microphone is optional, just warn
                print(f"Microphone permission: WARNING - {mic_msg} (optional for eye tracking)") 
        
        #Check dependencies 
        deps_ok, missing = self.check_dependencies() 
        if deps_ok: 
            print("All dependencies installed: OK") 
        else: 
            print(f"Missing dependencies: {', '.join(missing)}")
            print("Please install missing packages using pip.")
            all_ok = False
        print() 
        return all_ok
    
    def safe_camera_init(self,camera_id = 0):
        """ 
        Safely initialize camera with error handling 
        
        args: 
            camera_id: Camera device ID 
        
        returns:
            cv2.VideoCapture or None 
        """
        try: 
            import cv2 
            cam = cv2.VideoCapture(camera_id) 
            
            if not cam.isOpened(): 
                raise Exception("Camera failed to open.") 
            
            cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640) 
            cam.set(cv2.CAP_PROP_FRAME_HEIGHT,480) 
            
            ret, frame = cam.read() 
            if not ret: 
                cam.release() 
                raise Exception("Camera opened but cannot read frame.")
            
            return cam 
        except Exception as e:
            self.handle_error(e,"Camera Initialization") 
            return None 
    
    def safe_microphone_init(self):
        """ 
        Safely initialize microphone with error handling 
        
        returns: 
            tuple: (sr.Recognizer, sr.Microphone) or (None,None) 
        """ 
        try: 
            import speech_recognition as sr
            
            recognizer = sr.Recognizer() 
            microphone = sr.Microphone() 
            
            with microphone as source: 
                recognizer.adjust_for_ambient_noise(source,duration = 0.5) 
            
            return recognizer, microphone  
        except Exception as e: 
            self.handle_error(e,"Microphone Initialization") 
            return None, None   
        
class RecoveryManager: 
    # Manages recovery from errors 
    
    def __init__(self, max_retries=3): 
        # Initialize the recovery manager 
        self.max_retries = max_retries 
        self.retry_count = 0 
        
    def should_retry(self, operation): 
        """ 
        Check if operation should be retried 
        
        args: 
            operation : Name of operation 
        returns:
            bool : True if should retry 
        """
        count = self.retry_count.get(operation,0) 
        
        if count >= self.max_retries: 
            return False 
        
        self.retry_count[operation] = count + 1 
        return True 

    def reset_retry(self, operation): 
        """ Reset retry count for operation."""
        if operation in self.retry_count: 
            del self.retry_count[operation] 
            
    def attempt_recovery(self, error, operation): 
        """ 
        Attempt to recover from an error 
        
        args: 
            error: Exception that occurred 
            operation : Operation that failed 
            
        returns: 
            bool: True if recovery successful 
        """
        if not self.should_retry(operation):
            print(f"\nMax retries reached for {operation} ") 
            return False 

        retry_num = self.retry_count[operation] 
        print(f"\n Attempting recovery for {operation} (attempt {retry_num}/{self.max_retries} )....")
        
        # Wait before retry 
        import time 
        time.sleep(1) 
        
        return True 
    

if __name__ == "__main__": 
    # Test error handler 
    print("\nTesting error handler\n")
    
    handler = ErrorHandler() 
    
    # Test permission checks 
    handler.check_all_permissions() 
    
    # Test system info 
    info = handler.get_system_info() 
    print("\nSystem Info: ")
    for key, value in info.items(): 
        print(f" {key}: {value}") 
    
    print("\n Error handler test complete! ")
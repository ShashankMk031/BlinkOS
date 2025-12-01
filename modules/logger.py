""" 
Logger Module - Centralized logging system 
""" 

import os 
import sys 
from datetime import datetime 
from pathlib import Path 

class Logger: 
    # Simple logger class 
    
    def __init__(self, log_dir = 'logs', log_file = None, console = True): 
        """ 
        Initialize logger 
        
        args: 
            log_dir : Directory to store logs 
            log_file: Log file name (None = auto-generate)
            console: If True, also print to console 
        """
        self.log_dir = log_dir 
        self.console = console 
        
        # Create log directory 
        os.makedirs(log_dir, exist_ok=True)
        
        # Generate log file name 
        if log_file is None: 
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") 
            log_file = f"blinkos_log_{timestamp}.log"
            
        self.log_file = os.path.join(log_dir, log_file)
        
        # Create/open log file 
        self._init_log_file() 
    
    def _init_log_file(self):
        """Initialize log file with header"""
        with open(self.log_file, 'w') as f:
            f.write("="*60 + "\n")
            f.write("BlinkOS Log File\n")
            f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*60 + "\n\n")
        
        self.info(f"Logger initialized: {self.log_file}")
        
    def _write(self, level, message): 
        """ 
        Write log entry 
        
        args : 
            level : Log level (INFO, WARNING, ERROR) 
            message: Log message 
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        # Write to file 
        try: 
            with open(self.log_file, 'a') as f: 
                f.write(log_entry) 
        except Exception as e:
            print(f"Failed to write to log file: {str(e)}")
        
        # Print to console 
        if self.console: 
            if level == "ERROR": 
                print(f"[{timestamp}] {message} ", file=sys.stderr)
            else:
                print(f"[{timestamp}] {message}")
    
    def info(self, message):
        # Log info message 
        self._write("INFO", message) 
    
    def warning(self, message): 
        # Log warning message 
        self._write("WARNING", message) 
        
    def error(self, message): 
        # Log error message 
        self._write("ERROR", message)
    
    def debug(self, message):
        # Log debug message 
        self._write("DEBUG", message)
    
    def section(self,title): 
        # Log section header 
        seperator = "-" * 60 
        self._write("INFO", seperator)
        self._write("INFO", title) 
        self._write("INFO", seperator) 
    
    def log_system_info(self): 
        # Log system information 
        import platform 
        
        self.section("System Information:") 
        self.info(f"OS: {platform.system()} {platform.release()}") 
        self.info(f"Python: {sys.version.split()[0]}")
        self.info(f"Architecture: {platform.machine()}") 
    
    def log_event(self, event_type, details): 
        """ 
        Log an event 
        
        args: 
            event_type: Type of event 
            details : Event details 
        """
        self.info(f"EVENT: {event_type} - {details}")
    
    def log_performance(self, metric, value):
        """
        Log performance metric
        
        Args:
            metric: Metric name
            value: Metric value
        """
        self.info(f"PERFORMANCE: {metric} = {value}")
    
    def close(self):
        """Close logger"""
        self._write("INFO", "Logger closing")
        self._write("INFO", "="*60)

class SessionLogger: 
    # Logger for tracking session metrics 
    
    def __init__(self, logger):
        # Initialize session logger
        self.logger = logger 
        self.session_start = datetime.now() 
        self.metrics = { 
            'clicks' : 0, 
            'voice_commands' : 0, 
            'errors': 0, 
            'calibrations': 0, 
        }
        
    def log_click(self): 
        # Log click event 
        self.metrics['clicks'] += 1 
    
    def  log_voice_command(self, command): 
        # Log a voice command 
        self.metrics['voice_commands'] += 1 
        self.logger.log_event("VOICE COMMAND", command) 
    
    def log_error(self, error_type): 
        # Log an error event 
        self.metrics['errors'] += 1 
        self.logger.log_event("ERROR", error_type) 
    
    def log_calibration(self, quality): 
        # Log calibration
        self.metrics['calibrations'] += 1 
        self.logger.log_event("CALIBRATION", f"Quality: {quality}") 
    
    def get_session_summary(self):
        """Get session summary"""
        duration = datetime.now() - self.session_start
        
        summary = {
            'duration': str(duration).split('.')[0],
            'clicks': self.metrics['clicks'],
            'voice_commands': self.metrics['voice_commands'],
            'errors': self.metrics['errors'],
            'calibrations': self.metrics['calibrations'],
        }
    
    def log_session_end(self):
        """Log session end with summary"""
        summary = self.get_session_summary()
        
        self.logger.section("Session Summary")
        self.logger.info(f"Duration: {summary['duration']}")
        self.logger.info(f"Clicks: {summary['clicks']}")
        self.logger.info(f"Voice Commands: {summary['voice_commands']}")
        self.logger.info(f"Errors: {summary['errors']}")
        self.logger.info(f"Calibrations: {summary['calibrations']}")
    
def cleanup_old_logs(log_dir = 'logs', max_age_days = 7): 
    """ 
    Cleanup old log files 
    
    args: 
        log_dir : Directory containing logs 
        max_age_days : Max age of logs to keep 
    """
    if not os.path.exists(log_dir): 
        return 
    
    cutoff_time = datetime.now().timestamp() - (max_age_days * 24*60*60) 
    deleted_count = 0 
    
    for filename in os.listdir(log_dir): 
        file_path = os.path.join(log_dir, filename) 
        
        if os.path.isfile(file_path) and filename.endswith('.log'): 
            file_time  = os.path.getmtime(file_path) 
            
            if file_time < cutoff_time: 
                try: 
                    os.remove(file_path)  
                    deleted_count += 1 
                except Exception as e: 
                    print(f"Failed to delete log file {file_path}: {str(e)}") 
    
    if deleted_count > 0: 
        print(f"Deleted {deleted_count} old log files") 
        

if __name__ == "__main__": 
    print("\nTesting Logger\n")
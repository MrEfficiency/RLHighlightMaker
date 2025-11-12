# python/video_recorder.py

import time
import os
import obsws_python as obs

class OBSRecorder:
    def __init__(self, output_path, obs_config):
        """
        Initialize OBS WebSocket recorder.
        
        Args:
            output_path: Full path where the recording should be saved
            obs_config: Dictionary with 'host', 'port', and 'password'
        """
        self.output_path = output_path
        self.obs_config = obs_config
        self.ws = None
        self.is_connected = False
        self.recording_started = False
        
    def connect(self):
        """Connect to OBS WebSocket server."""
        try:
            host = self.obs_config.get('host', 'localhost')
            port = self.obs_config.get('port', 4455)
            password = self.obs_config.get('password', '')
            
            print(f"Connecting to OBS at {host}:{port}...")
            
            # Create connection with new library syntax
            self.ws = obs.ReqClient(host=host, port=port, password=password)
            self.is_connected = True
            print("Successfully connected to OBS!")
            
            # Get OBS version info
            version_info = self.ws.get_version()
            print(f"OBS Studio Version: {version_info.obs_version}")
            print(f"WebSocket Version: {version_info.obs_web_socket_version}")
            
            return True
            
        except Exception as e:
            print(f"Failed to connect to OBS: {e}")
            print("\nMake sure:")
            print("  1. OBS Studio is running")
            print("  2. WebSocket server is enabled (Tools → WebSocket Server Settings)")
            print("  3. The password in config.json matches OBS")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Disconnect from OBS WebSocket server."""
        if self.ws and self.is_connected:
            try:
                # The new library handles disconnection automatically
                self.ws = None
                print("Disconnected from OBS")
            except Exception as e:
                print(f"Error disconnecting from OBS: {e}")
            finally:
                self.is_connected = False
    
    def set_recording_folder(self, folder_path):
        """Set the OBS recording output folder."""
        if not self.is_connected:
            print("Not connected to OBS")
            return False
        
        try:
            # Ensure folder exists
            os.makedirs(folder_path, exist_ok=True)
            
            # Set the recording path in OBS
            self.ws.set_record_directory(folder_path)
            print(f"Set OBS recording folder to: {folder_path}")
            return True
        except Exception as e:
            print(f"Error setting recording folder: {e}")
            return False
    
    def start_recording(self):
        """Start recording in OBS."""
        if not self.is_connected:
            print("Not connected to OBS. Call connect() first.")
            return False
        
        try:
            # Check if already recording
            status = self.ws.get_record_status()
            if status.output_active:
                print("OBS is already recording")
                return False
            
            # Set the output folder
            output_dir = os.path.dirname(self.output_path)
            self.set_recording_folder(output_dir)
            
            # Start recording
            self.ws.start_record()
            self.recording_started = True
            print(f"Started OBS recording")
            print(f"Output will be saved to: {output_dir}")
            
            # Give OBS a moment to start
            time.sleep(0.5)
            
            return True
            
        except Exception as e:
            print(f"Error starting recording: {e}")
            return False
    
    def stop_recording(self):
        """Stop recording in OBS and wait for file to be saved."""
        if not self.is_connected:
            print("Not connected to OBS")
            return False
        
        if not self.recording_started:
            print("Recording was not started")
            return False
        
        try:
            # Stop recording
            result = self.ws.stop_record()
            print("Stopping OBS recording...")
            
            # The new API returns the output path directly
            if hasattr(result, 'output_path'):
                print(f"Recording saved to: {result.output_path}")
            
            # Wait for recording to finish saving
            max_wait = 30  # Maximum 30 seconds
            waited = 0
            while waited < max_wait:
                status = self.ws.get_record_status()
                if not status.output_active:
                    break
                time.sleep(0.5)
                waited += 0.5
            
            if waited >= max_wait:
                print("Warning: Timeout waiting for recording to stop")
            
            self.recording_started = False
            print("Recording stopped successfully")
            
            # Get the actual output file path from OBS
            output_dir = os.path.dirname(self.output_path)
            print(f"Recording saved to folder: {output_dir}")
            
            return True
            
        except Exception as e:
            print(f"Error stopping recording: {e}")
            return False
    
    def is_recording(self):
        """Check if OBS is currently recording."""
        if not self.is_connected:
            return False
        
        try:
            status = self.ws.get_record_status()
            return status.output_active
        except Exception as e:
            print(f"Error checking recording status: {e}")
            return False
    
    def get_last_recording_path(self):
        """
        Get the path of the most recently created recording in the output folder.
        Call this after stop_recording() to get the actual filename.
        """
        output_dir = os.path.dirname(self.output_path)
        
        try:
            # Find the most recently modified .mp4 file
            files = [os.path.join(output_dir, f) for f in os.listdir(output_dir) 
                    if f.endswith('.mp4')]
            
            if not files:
                print("No recording files found")
                return None
            
            # Get the most recent file
            latest_file = max(files, key=os.path.getmtime)
            
            # Verify it was created recently (within last minute)
            file_age = time.time() - os.path.getmtime(latest_file)
            if file_age > 60:
                print(f"Warning: Most recent file is {file_age:.0f} seconds old")
            
            file_size = os.path.getsize(latest_file) / (1024 * 1024)  # MB
            print(f"Last recording: {os.path.basename(latest_file)} ({file_size:.2f} MB)")
            
            return latest_file
            
        except Exception as e:
            print(f"Error finding last recording: {e}")
            return None
    
    def rename_last_recording(self, new_path):
        """
        Rename the most recent recording to the desired output path.
        Useful for controlling exact filenames.
        """
        last_recording = self.get_last_recording_path()
        
        if not last_recording:
            print("No recording found to rename")
            return False
        
        try:
            # Ensure target directory exists
            os.makedirs(os.path.dirname(new_path), exist_ok=True)
            
            # Rename the file
            os.rename(last_recording, new_path)
            print(f"Renamed recording to: {new_path}")
            return True
            
        except Exception as e:
            print(f"Error renaming recording: {e}")
            return False
    
    def __enter__(self):
        """Context manager entry - connects to OBS."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures recording is stopped and disconnects."""
        if self.recording_started:
            self.stop_recording()
        self.disconnect()


# Keep the old FFmpegRecorder class for backwards compatibility
class FFmpegRecorder:
    """
    Legacy FFmpeg recorder - kept for backwards compatibility.
    Consider using OBSRecorder instead for better game capture.
    """
    def __init__(self, output_path, codec, window_title, audio_device=None):
        print("Warning: FFmpegRecorder is deprecated. Consider using OBSRecorder for better results.")
        print("FFmpegRecorder functionality has been removed. Please update your code to use OBSRecorder.")
        self.output_path = output_path
    
    def start_recording(self):
        print("Error: FFmpegRecorder is no longer supported. Use OBSRecorder instead.")
        return False
    
    def stop_recording(self):
        pass
    
    def is_recording(self):
        return False
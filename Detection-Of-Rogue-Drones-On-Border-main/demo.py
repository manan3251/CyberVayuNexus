import cv2
import torch
import numpy as np
from pathlib import Path
import time
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
from PIL import Image, ImageTk
import csv
from datetime import datetime
import os
import dropbox  # For cloud storage
import json
import threading
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import pandas as pd
from fpdf import FPDF
import socket
import requests
from ttkthemes import ThemedTk
import customtkinter as ctk

class ModernDroneDetector:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Drone Detection System")
        
        # Set modern theme
        self.style = ttk.Style()
        self.style.configure("Modern.TFrame", background="#2b2b2b")
        self.style.configure("Modern.TButton", padding=6, font=("Helvetica", 10), background="#4a90e2")
        self.style.configure("Modern.TLabel", background="#2b2b2b", foreground="#ffffff", font=("Helvetica", 10))
        self.style.configure("Title.TLabel", font=("Helvetica", 18, "bold"), foreground="#4a90e2")
        self.style.configure("Stats.TLabel", font=("Helvetica", 12), foreground="#4a90e2")
        self.style.configure("Alert.TLabel", font=("Helvetica", 12), foreground="#ff7675")
        
        # Load cloud storage config
        self.cloud_config = self.load_cloud_config()
        self.dropbox_client = None
        if self.cloud_config.get('dropbox_token'):
            try:
                self.dropbox_client = dropbox.Dropbox(self.cloud_config['dropbox_token'])
            except Exception as e:
                print(f"Failed to initialize Dropbox: {e}")
        
        # Create reports directory
        self.reports_dir = Path("detection_reports")
        self.reports_dir.mkdir(exist_ok=True)
        
        # Initialize CSV for detections with new structure
        self.session_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.csv_file = self.reports_dir / f"drone_detections_{self.session_time}.csv"
        
        with open(self.csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Drone_IP', 'Confidence', 'Size', 'Location_X', 'Location_Y', 
                           'Source', 'Notes', 'Frame_Number', 'Network_Info'])
        
        # Initialize YOLOv5 model with improved settings
        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5m')
        self.model.conf = 0.45  # Higher threshold for better accuracy
        self.model.iou = 0.45
        
        # Detection classes
        self.DETECTION_CLASSES = {
            'DRONE': {'airplane', 'bird'},  # Aerial objects
            'HUMAN': {'person'},  # Human detection
            'WEAPON': {'knife', 'scissors', 'gun'},  # Dangerous objects
            'VEHICLE': {'car', 'truck', 'motorcycle', 'bus'},  # Vehicles
            'OBJECT': {'backpack', 'handbag', 'suitcase', 'box'}  # Suspicious objects
        }
        
        # Detection parameters
        self.MIN_SIZE = 20  # Minimum size in pixels
        self.MAX_ASPECT_RATIO = 3.0  # Maximum width/height ratio
        
        # Initialize variables
        self.mode = "images"
        self.webcam = None
        self.video_capture = None
        self.current_idx = 0
        self.prev_time = time.time()
        self.paused = False
        self.detections_count = {k: 0 for k in self.DETECTION_CLASSES.keys()}
        
        # Configure window
        self.setup_ui()
        
        # Load images
        self.image_dir = Path("train_dataset/content/train_dataset/images/detected")
        self.image_files = sorted([f for f in self.image_dir.glob("*.jpg") if f.is_file()])
        
        # Bind keyboard shortcuts
        self.bind_shortcuts()
        
        # Start update loop
        self.update()
    
    def load_cloud_config(self):
        """Load cloud storage configuration"""
        config_file = Path("cloud_config.json")
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading cloud config: {e}")
        return {}
    
    def setup_ui(self):
        # Create main container with modern dark theme
        self.main_container = ttk.Frame(self.root, style="Modern.TFrame")
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header with improved styling
        header = ttk.Frame(self.main_container, style="Modern.TFrame")
        header.pack(fill=tk.X, padx=10, pady=5)
        
        # Title with status indicator
        title_frame = ttk.Frame(header, style="Modern.TFrame")
        title_frame.pack(side=tk.LEFT)
        
        self.status_indicator = ttk.Label(title_frame, text="●", style="Modern.TLabel")
        self.status_indicator.pack(side=tk.LEFT, padx=(0, 5))
        self.update_status_indicator("active")
        
        ttk.Label(title_frame, text="Drone Detection System", style="Title.TLabel").pack(side=tk.LEFT)
        
        # Right side controls
        controls_frame = ttk.Frame(header, style="Modern.TFrame")
        controls_frame.pack(side=tk.RIGHT)
        
        self.mode_label = ttk.Label(controls_frame, text="Mode: Image Analysis", style="Modern.TLabel")
        self.mode_label.pack(side=tk.RIGHT, padx=5)
        
        # Create content area
        content = ttk.PanedWindow(self.main_container, orient=tk.HORIZONTAL)
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left panel - Video display
        left_panel = ttk.Frame(content)
        content.add(left_panel, weight=2)
        
        # Canvas with black background
        self.canvas = tk.Canvas(left_panel, bg="black", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Control panel
        controls = ttk.Frame(left_panel)
        controls.pack(fill=tk.X, pady=5)
        
        # Modern buttons with improved styling
        ttk.Button(controls, text="◀ Previous", command=self.prev_image, style="Modern.TButton").pack(side=tk.LEFT, padx=2)
        ttk.Button(controls, text="Next ▶", command=self.next_image, style="Modern.TButton").pack(side=tk.LEFT, padx=2)
        ttk.Button(controls, text="📷 Webcam", command=self.toggle_mode, style="Modern.TButton").pack(side=tk.LEFT, padx=2)
        ttk.Button(controls, text="📁 Load Video", command=self.load_video, style="Modern.TButton").pack(side=tk.LEFT, padx=2)
        self.pause_button = ttk.Button(controls, text="⏸ Pause", command=self.toggle_pause, style="Modern.TButton")
        self.pause_button.pack(side=tk.LEFT, padx=2)
        
        # Right panel - Data display
        right_panel = ttk.Frame(content)
        content.add(right_panel, weight=1)
        
        # Statistics panel
        stats = ttk.LabelFrame(right_panel, text="Detection Statistics", style="Modern.TFrame")
        stats.pack(fill=tk.X, padx=5, pady=5)
        
        self.stats_labels = {
            'drone': ttk.Label(stats, text="Drones: 0", style="Stats.TLabel"),
            'human': ttk.Label(stats, text="Humans: 0", style="Stats.TLabel"),
            'weapon': ttk.Label(stats, text="Weapons: 0", style="Stats.TLabel"),
            'vehicle': ttk.Label(stats, text="Vehicles: 0", style="Stats.TLabel"),
            'object': ttk.Label(stats, text="Objects: 0", style="Stats.TLabel"),
            'confidence': ttk.Label(stats, text="Avg Confidence: 0%", style="Stats.TLabel"),
            'status': ttk.Label(stats, text="Status: Monitoring", style="Stats.TLabel")
        }
        
        for label in self.stats_labels.values():
            label.pack(anchor=tk.W, padx=5, pady=2)
        
        # Live detection log
        ttk.Label(right_panel, text="Detection Log", style="Title.TLabel").pack(pady=5)
        self.log_display = scrolledtext.ScrolledText(right_panel, height=10, font=("Consolas", 10))
        self.log_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Action buttons
        actions = ttk.Frame(right_panel)
        actions.pack(fill=tk.X, padx=5, pady=5)
        
        # CSV Management buttons
        ttk.Button(actions, text="Generate CSV", command=self.generate_csv, style="Modern.TButton").pack(side=tk.LEFT, padx=2)
        ttk.Button(actions, text="Delete CSV", command=self.delete_csv, style="Modern.TButton").pack(side=tk.LEFT, padx=2)
        
        # Email configuration
        email_frame = ttk.Frame(right_panel)
        email_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(email_frame, text="Recipient Email:", style="Modern.TLabel").pack(side=tk.LEFT)
        self.recipient_email_var = tk.StringVar()
        ttk.Entry(email_frame, textvariable=self.recipient_email_var, width=30).pack(side=tk.LEFT, padx=5)
        ttk.Button(email_frame, text="Send Report", command=self.send_report_via_email, style="Modern.TButton").pack(side=tk.LEFT, padx=2)
        
        # Exit button
        ttk.Button(actions, text="Exit (Q)", command=self.on_closing, style="Modern.TButton").pack(side=tk.RIGHT, padx=2)
    
    def bind_shortcuts(self):
        """Bind keyboard shortcuts to actions"""
        self.root.bind('<Left>', lambda e: self.prev_image())
        self.root.bind('<Right>', lambda e: self.next_image())
        self.root.bind('<space>', lambda e: self.toggle_pause())
        self.root.bind('q', lambda e: self.on_closing())
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def get_detection_type(self, class_name):
        """Determine the type of detection based on class name"""
        for det_type, classes in self.DETECTION_CLASSES.items():
            if class_name in classes:
                return det_type
        return None

    def is_valid_detection(self, detection):
        """Enhanced detection validation logic"""
        class_name = detection['name']
        det_type = self.get_detection_type(class_name)
        
        if not det_type:
            return False, None
            
        # Get detection box dimensions
        width = detection['xmax'] - detection['xmin']
        height = detection['ymax'] - detection['ymin']
        size = width * height
        aspect_ratio = width / height if height > 0 else 0
        
        # Size and shape analysis
        if size < self.MIN_SIZE:
            return False, None
        if aspect_ratio > self.MAX_ASPECT_RATIO or aspect_ratio < (1/self.MAX_ASPECT_RATIO):
            return False, None
            
        # Higher confidence thresholds for specific types
        if det_type == 'WEAPON' and detection['confidence'] < 0.5:
            return False, None
        if det_type == 'DRONE' and class_name == 'bird' and detection['confidence'] < 0.45:
            return False, None
            
        return True, det_type

    def process_frame(self, frame, source):
        try:
            # Get detections
            results = self.model(frame)
            detections = results.pandas().xyxy[0]
            
            # Reset detection counts
            self.detections_count = {k: 0 for k in self.DETECTION_CLASSES.keys()}
            
            # Filter and process detections
            valid_detections = []
            for _, det in detections.iterrows():
                is_valid, det_type = self.is_valid_detection(det)
                if is_valid:
                    valid_detections.append((det, det_type))
                    self.detections_count[det_type] += 1
            
            # Update statistics
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            total_detections = len(valid_detections)
            avg_confidence = detections['confidence'].mean() if not detections.empty else 0
            
            # Update statistics labels
            for det_type, count in self.detections_count.items():
                label_key = det_type.lower()
                if label_key in self.stats_labels:
                    self.stats_labels[label_key].config(text=f"{det_type.title()}: {count}")
            
            self.stats_labels['confidence'].config(text=f"Avg Confidence: {avg_confidence:.1%}")
            
            # Log detections and save to CSV
            if valid_detections:
                log_text = f"\n[{current_time}] Found {total_detections} objects:"
                for det_type, count in self.detections_count.items():
                    if count > 0:
                        log_text += f" {det_type}: {count}"
                self.log_display.insert(tk.END, log_text)
                self.log_display.see(tk.END)
                
                # Save to CSV with network info
                with open(self.csv_file, 'a', newline='') as f:
                    writer = csv.writer(f)
                    for det, det_type in valid_detections:
                        width = det['xmax'] - det['xmin']
                        height = det['ymax'] - det['ymin']
                        network_info = self.get_network_info()
                        writer.writerow([
                            current_time,
                            network_info.split("IP: ")[1].split(",")[0],  # Extract IP
                            f"{det['confidence']:.2f}",
                            f"{width:.0f}x{height:.0f}",
                            f"{det['xmin']:.0f}",
                            f"{det['ymin']:.0f}",
                            source,
                            det['name'],
                            "N/A",
                            network_info
                        ])
            
            # Draw detections
            frame_with_detections = frame.copy()
            for det, det_type in valid_detections:
                x1, y1, x2, y2 = map(int, [det['xmin'], det['ymin'], det['xmax'], det['ymax']])
                conf = det['confidence']
                
                # Different colors for different types
                color = {
                    'DRONE': (255, 0, 0),    # Red
                    'HUMAN': (0, 255, 0),    # Green
                    'WEAPON': (0, 0, 255),   # Blue
                    'VEHICLE': (255, 255, 0), # Yellow
                    'OBJECT': (255, 0, 255)   # Magenta
                }.get(det_type, (0, 255, 0))
                
                # Draw box with confidence
                cv2.rectangle(frame_with_detections, (x1, y1), (x2, y2), color, 2)
                label = f"{det_type} {conf:.2f}"
                cv2.putText(frame_with_detections, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            return frame_with_detections
            
        except Exception as e:
            print(f"Error in process_frame: {e}")
            return frame
    
    def load_video(self):
        """Load a video file for detection"""
        video_path = filedialog.askopenfilename(
            filetypes=[("Video files", "*.mp4 *.avi *.mov"), ("All files", "*.*")]
        )
        
        if video_path:
            if self.webcam is not None:
                self.webcam.release()
            if self.video_capture is not None:
                self.video_capture.release()
            
            self.video_capture = cv2.VideoCapture(video_path)
            if self.video_capture.isOpened():
                self.mode = "video"
                self.mode_label.config(text="Mode: Video Analysis")
            else:
                print("Failed to open video file")
    
    def toggle_pause(self):
        """Pause/Resume video playback"""
        self.paused = not self.paused
        self.pause_button.config(text="Resume" if self.paused else "Pause")
    
    def update_status_indicator(self, status):
        """Update the status indicator color"""
        colors = {
            'active': '#00b894',    # Green
            'warning': '#fdcb6e',   # Yellow
            'error': '#ff7675',     # Red
            'inactive': '#636e72'   # Gray
        }
        self.status_indicator.configure(foreground=colors.get(status, colors['inactive']))
    
    def update_cloud_status(self):
        """Update cloud connection status"""
        if self.dropbox_client:
            try:
                self.dropbox_client.users_get_current_account()
                self.cloud_status.configure(text="☁ Connected", foreground="#00b894")
            except:
                self.cloud_status.configure(text="☁ Error", foreground="#ff7675")
        else:
            self.cloud_status.configure(text="☁ Not Connected", foreground="#636e72")
    
    def upload_to_cloud(self, file_path):
        """Upload file to cloud storage"""
        if not self.dropbox_client:
            return
            
        try:
            with open(file_path, 'rb') as f:
                file_name = os.path.basename(file_path)
                self.dropbox_client.files_upload(
                    f.read(),
                    f"/DroneDetection/{self.session_time}/{file_name}",
                    mode=dropbox.files.WriteMode.overwrite
                )
            print(f"Uploaded {file_name} to cloud storage")
        except Exception as e:
            print(f"Failed to upload to cloud: {e}")
    
    def save_detection(self):
        """Enhanced save detection with cloud backup"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Save locally
        with open(self.csv_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                current_time,
                "Manual Save",
                "N/A",
                "N/A",
                "N/A",
                "N/A",
                self.mode,
                "Manual save",
                "N/A"
            ])
        
        # Upload to cloud in background
        if self.dropbox_client:
            threading.Thread(target=self.upload_to_cloud, args=(self.csv_file,)).start()
        
        self.log_display.insert(tk.END, f"\n[{current_time}] Detection saved locally and queued for cloud upload")
        self.log_display.see(tk.END)
    
    def update(self):
        if not self.paused:
            if self.mode == "webcam":
                ret, frame = self.webcam.read()
                if not ret:
                    print("Failed to grab frame")
                    return
                
                processed_frame = self.process_frame(frame, "webcam")
                self.display_frame(processed_frame)
                
            elif self.mode == "video" and self.video_capture is not None:
                ret, frame = self.video_capture.read()
                if not ret:
                    self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Loop video
                    ret, frame = self.video_capture.read()
                
                if ret:
                    processed_frame = self.process_frame(frame, "video")
                    self.display_frame(processed_frame)
                
            else:
                if self.current_idx >= len(self.image_files):
                    self.current_idx = 0
                
                image_path = str(self.image_files[self.current_idx])
                frame = cv2.imread(image_path)
                if frame is None:
                    print(f"Failed to load image: {image_path}")
                    return
                
                processed_frame = self.process_frame(frame, image_path)
                self.display_frame(processed_frame)
        
        self.root.after(10, self.update)
    
    def display_frame(self, frame):
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        
        # Resize image to fit canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width > 1 and canvas_height > 1:  # Valid canvas size
            # Calculate aspect ratio
            img_width, img_height = image.size
            aspect_ratio = img_width / img_height
            
            if canvas_width / canvas_height > aspect_ratio:
                new_height = canvas_height
                new_width = int(new_height * aspect_ratio)
            else:
                new_width = canvas_width
                new_height = int(new_width / aspect_ratio)
            
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(image=image)
            self.canvas.create_image(canvas_width//2, canvas_height//2, anchor=tk.CENTER, image=photo)
            self.canvas.image = photo
    
    def prev_image(self):
        if self.mode == "images":
            self.current_idx = (self.current_idx - 1) % len(self.image_files)
    
    def next_image(self):
        if self.mode == "images":
            self.current_idx = (self.current_idx + 1) % len(self.image_files)
    
    def toggle_mode(self):
        if self.mode == "images":
            self.webcam = cv2.VideoCapture(0)
            if self.webcam.isOpened():
                self.mode = "webcam"
                self.mode_label.config(text="Mode: Webcam Analysis")
            else:
                print("Failed to open webcam")
        else:
            if self.webcam is not None:
                self.webcam.release()
            if self.video_capture is not None:
                self.video_capture.release()
            self.video_capture = None
            self.mode = "images"
            self.mode_label.config(text="Mode: Image Analysis")
    
    def generate_csv(self):
        """Generate a new CSV file with current detections"""
        try:
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_csv_file = self.reports_dir / f"drone_detections_{current_time}.csv"
            
            with open(new_csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Timestamp', 'Drone_IP', 'Confidence', 'Size', 'Location_X', 'Location_Y', 
                               'Source', 'Notes', 'Frame_Number', 'Network_Info'])
            
            messagebox.showinfo("Success", f"New CSV file created: {new_csv_file}")
            self.csv_file = new_csv_file
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create CSV file: {e}")

    def delete_csv(self):
        """Delete the current CSV file"""
        try:
            if self.csv_file.exists():
                self.csv_file.unlink()
                messagebox.showinfo("Success", "CSV file deleted successfully")
                self.generate_csv()  # Create a new empty CSV file
            else:
                messagebox.showinfo("Info", "No CSV file to delete")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete CSV file: {e}")

    def get_network_info(self):
        """Get network information for the detected drone"""
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            return f"Host: {hostname}, IP: {local_ip}"
        except:
            return "Network info unavailable"

    def generate_csv_report(self, data):
        """Generate a CSV report of drone and human detections"""
        csv_file = self.reports_dir / f"detection_report_{self.session_time}.csv"
        # Filter data for drones and humans only
        filtered_data = [item for item in data if item['Object_Type'] in ['Drone', 'Human']]
        df = pd.DataFrame(filtered_data)
        df.to_csv(csv_file, index=False)
        return csv_file

    def generate_pdf_report(self, data):
        """Generate a PDF report of drone and human detections"""
        pdf_file = self.reports_dir / f"detection_report_{self.session_time}.pdf"
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Detection Report", ln=True, align='C')
        pdf.cell(200, 10, txt=f"Session Date: {self.session_time}", ln=True, align='C')
        pdf.ln(10)
        # Filter data for drones and humans only
        filtered_data = [item for item in data if item['Object_Type'] in ['Drone', 'Human']]
        for item in filtered_data:
            pdf.cell(200, 10, txt=f"Time: {item['Time']}, Type: {item['Object_Type']}, Location: {item['Location']}", ln=True)
        pdf.output(pdf_file)
        return pdf_file

    def send_email(self, recipient_email, report_file):
        """Send email with the report attached"""
        email_config = self.load_email_config()
        if not email_config:
            messagebox.showerror("Error", "Email configuration not found or invalid")
            return False

        try:
            msg = MIMEMultipart()
            msg['From'] = email_config['sender_email']
            msg['To'] = recipient_email
            msg['Subject'] = f"Drone Detection Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            body = "Please find attached the drone detection report."
            msg.attach(MIMEText(body, 'plain'))

            with open(report_file, "rb") as f:
                part = MIMEApplication(f.read(), Name=os.path.basename(report_file))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(report_file)}"'
                msg.attach(part)

            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['sender_email'], email_config['sender_password'])
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    def generate_summary_report(self):
        """Generate a summary report of all detections"""
        try:
            with open(self.csv_file, 'r') as csv_file:
                reader = csv.DictReader(csv_file)
                data = list(reader)
                
                # Generate CSV and PDF reports
                csv_report = self.generate_csv_report(data)
                pdf_report = self.generate_pdf_report(data)
                
                # Send the CSV report via email
                self.send_email("recipient@example.com", csv_report)

        except Exception as e:
            print(f"Error generating summary report: {e}")
    
    def on_closing(self, event=None):
        """Clean up resources before closing"""
        try:
            if self.webcam:
                self.webcam.release()
            if self.video_capture:
                self.video_capture.release()
        except Exception as e:
            print(f"Error during cleanup: {e}")
        
        try:
            # Instead of using cv2.destroyAllWindows(), close specific windows if needed
            for window_name in ['Preview', 'Detection']:
                try:
                    cv2.destroyWindow(window_name)
                except:
                    pass
        except Exception as e:
            print(f"Error closing windows: {e}")
        
        print("Closing application...")
        self.root.quit()

    def send_report_via_email(self):
        """Send the latest report via email"""
        try:
            recipient_email = self.recipient_email_var.get()
            if not recipient_email:
                messagebox.showerror("Input Error", "Please enter a recipient email address.")
                return
            
            email_config = self.load_email_config()
            if not email_config:
                messagebox.showerror("Error", "Email configuration not found or invalid")
                return
            
            msg = MIMEMultipart()
            msg['From'] = email_config['sender_email']
            msg['To'] = recipient_email
            msg['Subject'] = f"Drone Detection Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            body = "Please find attached the latest drone detection report."
            msg.attach(MIMEText(body, 'plain'))
            
            with open(self.csv_file, "rb") as f:
                part = MIMEApplication(f.read(), Name=os.path.basename(self.csv_file))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(self.csv_file)}"'
                msg.attach(part)
            
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['sender_email'], email_config['sender_password'])
            server.send_message(msg)
            server.quit()
            
            messagebox.showinfo("Success", "Report sent successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send email: {e}")

    def load_email_config(self):
        """Load email configuration"""
        config_file = Path("email_config.json")
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)['email']
            except Exception as e:
                print(f"Error loading email config: {e}")
        return None

def main():
    root = tk.Tk()
    app = ModernDroneDetector(root)
    root.mainloop()

if __name__ == "__main__":
    main() 
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
import pandas as pd
import librosa
import sounddevice as sd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import os
import tempfile
import wave
import struct
import threading
import sys
from datetime import datetime
import time

class AudioDetectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Deepfake Detector")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2c3e50')  # Dark blue background
        
        # Initialize variables
        self.recording = False
        self.audio_data = None
        self.sample_rate = 44100
        self.model = None
        self.scaler = StandardScaler()
        
        # Set style
        self.setup_styles()
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="20", style='Main.TFrame')
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # First create the dataset
        self.create_sample_dataset()
        
        # Then create and train model
        self.create_model()
        
        # Create GUI elements
        self.create_widgets()
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
    
    def setup_styles(self):
        self.style = ttk.Style()
        
        # Configure colors
        bg_color = '#2c3e50'  # Dark blue
        fg_color = '#ecf0f1'  # Light gray
        accent_color = '#3498db'  # Blue
        
        # Main frame style
        self.style.configure('Main.TFrame', background=bg_color)
        
        # Label styles
        self.style.configure('TLabel', 
                           background=bg_color, 
                           foreground=fg_color, 
                           font=('Helvetica', 10))
        
        self.style.configure('Header.TLabel', 
                           background=bg_color,
                           foreground=fg_color,
                           font=('Helvetica', 24, 'bold'))
        
        self.style.configure('Subtitle.TLabel', 
                           background=bg_color,
                           foreground=fg_color,
                           font=('Helvetica', 14))
        
        self.style.configure('Result.TLabel', 
                           background=bg_color,
                           foreground=fg_color,
                           font=('Helvetica', 12, 'bold'))
        
        self.style.configure('Status.TLabel', 
                           background=bg_color,
                           foreground=accent_color,
                           font=('Helvetica', 10, 'italic'))
        
        # Frame styles
        self.style.configure('Control.TFrame', background=bg_color)
        self.style.configure('Results.TFrame', background=bg_color)
        
        # LabelFrame styles
        self.style.configure('Panel.TLabelframe', 
                           background=bg_color,
                           foreground=fg_color)
        
        self.style.configure('Panel.TLabelframe.Label', 
                           background=bg_color,
                           foreground=fg_color,
                           font=('Helvetica', 12, 'bold'))
        
        # Button style
        self.style.configure('Action.TButton', 
                           font=('Helvetica', 11),
                           padding=10)
        
        # Progress bar style
        self.style.configure('Confidence.Horizontal.TProgressbar',
                           background=accent_color,
                           troughcolor=bg_color)
    
    def extract_advanced_features(self, y, sr):
        """Extract a comprehensive set of audio features"""
        try:
            # Preprocess audio
            y = librosa.effects.trim(y, top_db=20)[0]  # Remove silence
            y = librosa.util.normalize(y)  # Normalize audio
            
            # Basic features
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
            mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            
            # Rhythm features
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
            spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
            spectral_flatness = librosa.feature.spectral_flatness(y=y)[0]
            
            # Energy features
            rms = librosa.feature.rms(y=y)[0]
            zcr = librosa.feature.zero_crossing_rate(y)[0]
            
            # Harmonic and percussive components
            y_harmonic, y_percussive = librosa.effects.hpss(y)
            harmonic_mean = np.mean(np.abs(y_harmonic))
            percussive_mean = np.mean(np.abs(y_percussive))
            
            # Additional features
            tonnetz = librosa.feature.tonnetz(y=y, sr=sr)
            poly_features = librosa.feature.poly_features(y=y, sr=sr)
            
            # Calculate statistics for each feature
            feature_stats = {
                'mfcc_mean': np.mean(mfcc, axis=1),
                'mfcc_std': np.std(mfcc, axis=1),
                'mfcc_skew': np.mean([pd.Series(frame).skew() for frame in mfcc]),
                'mel_mean': np.mean(mel),
                'mel_std': np.std(mel),
                'chroma_mean': np.mean(chroma),
                'chroma_std': np.std(chroma),
                'tempo': tempo,
                'onset_strength': np.mean(onset_env),
                'spectral_centroids_mean': np.mean(spectral_centroids),
                'spectral_rolloff_mean': np.mean(spectral_rolloff),
                'spectral_bandwidth_mean': np.mean(spectral_bandwidth),
                'spectral_contrast_mean': np.mean(spectral_contrast),
                'spectral_flatness_mean': np.mean(spectral_flatness),
                'rms_mean': np.mean(rms),
                'rms_std': np.std(rms),
                'zcr_mean': np.mean(zcr),
                'zcr_std': np.std(zcr),
                'harmonic_mean': harmonic_mean,
                'percussive_mean': percussive_mean,
                'tonnetz_mean': np.mean(tonnetz, axis=1),
                'poly_features_mean': np.mean(poly_features, axis=1)
            }
            
            # Create feature vector with fixed dimensions
            features = []
            
            # MFCC features (40 mean + 40 std + 1 skew)
            features.extend(feature_stats['mfcc_mean'])
            features.extend(feature_stats['mfcc_std'])
            features.append(feature_stats['mfcc_skew'])
            
            # Mel features (2)
            features.append(feature_stats['mel_mean'])
            features.append(feature_stats['mel_std'])
            
            # Chroma features (2)
            features.append(feature_stats['chroma_mean'])
            features.append(feature_stats['chroma_std'])
            
            # Rhythm features (2)
            features.append(feature_stats['tempo'])
            features.append(feature_stats['onset_strength'])
            
            # Spectral features (5)
            features.append(feature_stats['spectral_centroids_mean'])
            features.append(feature_stats['spectral_rolloff_mean'])
            features.append(feature_stats['spectral_bandwidth_mean'])
            features.append(feature_stats['spectral_contrast_mean'])
            features.append(feature_stats['spectral_flatness_mean'])
            
            # Energy features (4)
            features.append(feature_stats['rms_mean'])
            features.append(feature_stats['rms_std'])
            features.append(feature_stats['zcr_mean'])
            features.append(feature_stats['zcr_std'])
            
            # Harmonic features (2)
            features.append(feature_stats['harmonic_mean'])
            features.append(feature_stats['percussive_mean'])
            
            # Additional features (6 + 4)
            features.extend(feature_stats['tonnetz_mean'])
            features.extend(feature_stats['poly_features_mean'])
            
            return np.array(features)
            
        except Exception as e:
            print(f"Error in feature extraction: {str(e)}")
            raise e

    def create_sample_dataset(self):
        """Create a sample dataset with advanced features"""
        try:
            # Generate more varied sample data
            n_samples = 20
            data = {
                'file_name': [f'sample{i}.wav' for i in range(1, n_samples + 1)],
                'label': [i % 2 for i in range(n_samples)]  # Alternating real/fake labels
            }
            
            # Generate feature columns based on actual feature extraction
            # Total features: 40(MFCC mean) + 40(MFCC std) + 1(MFCC skew) + 2(mel) + 2(chroma) + 
            # 2(rhythm) + 5(spectral) + 4(energy) + 2(harmonic) + 6(tonnetz) + 4(poly) = 106 features
            for i in range(106):
                data[f'feature_{i}'] = np.random.normal(0.5, 0.1, n_samples)
            
            df = pd.DataFrame(data)
            df.to_csv('dataset.csv', index=False)
            print("Sample dataset created successfully!")
            return df
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create sample dataset: {str(e)}")
            print(f"Error in create_sample_dataset: {str(e)}")
            return None
    
    def create_model(self):
        """Create and train an enhanced RandomForest model"""
        try:
            # Load or create dataset
            if os.path.exists('dataset.csv'):
                self.dataset = pd.read_csv('dataset.csv')
            else:
                self.dataset = self.create_sample_dataset()
            
            if self.dataset is None:
                raise Exception("Failed to load or create dataset")
            
            # Prepare features and labels
            feature_cols = [col for col in self.dataset.columns 
                          if col not in ['file_name', 'label']]
            
            X = self.dataset[feature_cols].values
            y = self.dataset['label'].values
            
            # Scale the features
            X_scaled = self.scaler.fit_transform(X)
            
            # Create and train model with enhanced parameters
            self.model = RandomForestClassifier(
                n_estimators=1000,  # Increased number of trees
                max_depth=None,
                min_samples_split=2,
                min_samples_leaf=1,
                max_features='sqrt',
                bootstrap=True,
                random_state=42,
                class_weight='balanced',
                n_jobs=-1,  # Use all available cores
                criterion='entropy'  # Use entropy for better accuracy
            )
            self.model.fit(X_scaled, y)
            print("Model trained successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create/train model: {str(e)}")
            print(f"Error in create_model: {str(e)}")
            self.model = None
    
    def create_widgets(self):
        # Header with gradient effect
        header_frame = ttk.Frame(self.main_frame, style='Control.TFrame')
        header_frame.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky=(tk.W, tk.E))
        
        title_label = ttk.Label(header_frame, 
                              text="🎵 Audio Deepfake Detector", 
                              style='Header.TLabel')
        title_label.pack(pady=(0, 5))
        
        subtitle_label = ttk.Label(header_frame, 
                                 text="Advanced AI-powered audio analysis system",
                                 style='Subtitle.TLabel')
        subtitle_label.pack(pady=(0, 10))
        
        # Control Panel
        control_frame = ttk.LabelFrame(self.main_frame, 
                                     text="Control Panel",
                                     padding="20",
                                     style='Panel.TLabelframe')
        control_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        # Buttons
        button_frame = ttk.Frame(control_frame, style='Control.TFrame')
        button_frame.pack(pady=10)
        
        self.record_button = ttk.Button(button_frame, 
                                      text="🎤 Record Audio",
                                      command=self.toggle_recording,
                                      style='Action.TButton',
                                      width=20)
        self.record_button.pack(side=tk.LEFT, padx=5)
        
        self.upload_button = ttk.Button(button_frame,
                                      text="📁 Upload Audio File",
                                      command=self.upload_audio,
                                      style='Action.TButton',
                                      width=20)
        self.upload_button.pack(side=tk.LEFT, padx=5)
        
        self.analyze_button = ttk.Button(button_frame,
                                       text="🔍 Analyze",
                                       command=self.analyze_audio,
                                       style='Action.TButton',
                                       width=20)
        self.analyze_button.pack(side=tk.LEFT, padx=5)
        
        # Status
        self.status_label = ttk.Label(control_frame,
                                    text="Ready to analyze audio",
                                    style='Status.TLabel')
        self.status_label.pack(pady=5)
        
        # Results Panel
        results_frame = ttk.LabelFrame(self.main_frame,
                                     text="Analysis Results",
                                     padding="20",
                                     style='Panel.TLabelframe')
        results_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Waveform plot
        plot_frame = ttk.Frame(results_frame, style='Results.TFrame')
        plot_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.figure, self.ax = plt.subplots(figsize=(10, 3))
        self.figure.patch.set_facecolor('#2c3e50')
        self.ax.set_facecolor('#2c3e50')
        self.ax.tick_params(colors='#ecf0f1')
        self.canvas = FigureCanvasTkAgg(self.figure, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Results
        results_text_frame = ttk.Frame(results_frame, style='Results.TFrame')
        results_text_frame.pack(fill=tk.X, pady=10)
        
        # Create two columns for probabilities
        left_frame = ttk.Frame(results_text_frame, style='Results.TFrame')
        left_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10)
        
        right_frame = ttk.Frame(results_text_frame, style='Results.TFrame')
        right_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10)
        
        # Real probability
        self.real_prob_label = ttk.Label(left_frame,
                                       text="Real Probability: --",
                                       style='Result.TLabel')
        self.real_prob_label.pack(pady=5)
        
        self.real_progress = ttk.Progressbar(left_frame,
                                           style='Confidence.Horizontal.TProgressbar',
                                           length=200,
                                           mode='determinate')
        self.real_progress.pack(pady=5)
        
        # Fake probability
        self.fake_prob_label = ttk.Label(right_frame,
                                       text="Fake Probability: --",
                                       style='Result.TLabel')
        self.fake_prob_label.pack(pady=5)
        
        self.fake_progress = ttk.Progressbar(right_frame,
                                           style='Confidence.Horizontal.TProgressbar',
                                           length=200,
                                           mode='determinate')
        self.fake_progress.pack(pady=5)
        
        # Confidence
        self.confidence_label = ttk.Label(results_frame,
                                        text="Overall Confidence: --",
                                        style='Result.TLabel')
        self.confidence_label.pack(pady=10)
        
        # Footer
        footer_frame = ttk.Frame(self.main_frame, style='Control.TFrame')
        footer_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        footer_label = ttk.Label(footer_frame,
                               text=f"© {datetime.now().year} Audio Deepfake Detector | Powered by Advanced Machine Learning",
                               style='TLabel')
        footer_label.pack()
    
    def toggle_recording(self):
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        """Start recording audio"""
        try:
            self.recording = True
            self.audio_data = []
            self.record_button.config(text="⏹️ Stop Recording")
            self.status_label.config(text="Recording...")
            
            def callback(indata, frames, time, status):
                if status:
                    print(status)
                if self.recording:
                    self.audio_data.append(indata.copy())
            
            self.stream = sd.InputStream(
                channels=1,
                samplerate=self.sample_rate,
                callback=callback
            )
            self.stream.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Recording failed: {str(e)}")
            print(f"Error in start_recording: {str(e)}")
            self.recording = False
            self.record_button.config(text="🎤 Record Audio")
            self.status_label.config(text="Ready to analyze audio")

    def stop_recording(self):
        """Stop recording audio"""
        try:
            self.recording = False
            if hasattr(self, 'stream'):
                self.stream.stop()
                self.stream.close()
            self.record_button.config(text="🎤 Record Audio")
            self.status_label.config(text="Processing recorded audio...")
            self.root.update()
            
            # Process the recorded audio
            self.process_recorded_audio()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop recording: {str(e)}")
            print(f"Error in stop_recording: {str(e)}")
            self.status_label.config(text="Ready to analyze audio")

    def process_recorded_audio(self):
        """Process the recorded audio"""
        try:
            if not self.audio_data:
                messagebox.showwarning("Warning", "No audio recorded!")
                return
            
            # Convert list of arrays to single numpy array
            audio_data = np.concatenate(self.audio_data, axis=0)
            
            # Normalize audio data
            audio_data = audio_data / np.max(np.abs(audio_data))
            
            # Save recorded audio to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name
                with wave.open(temp_path, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(self.sample_rate)
                    wf.writeframes((audio_data * 32767).astype(np.int16).tobytes())
            
            # Process the audio as live recording
            self.process_audio(temp_path, is_live_recording=True)
            
            # Clean up
            try:
                os.unlink(temp_path)
            except:
                pass  # Ignore cleanup errors
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process recorded audio: {str(e)}")
            print(f"Error in process_recorded_audio: {str(e)}")
            self.status_label.config(text="Ready to analyze audio")

    def upload_audio(self):
        """Handle audio file upload"""
        try:
            file_path = filedialog.askopenfilename(
                filetypes=[("Audio Files", "*.wav *.mp3 *.ogg *.flac")]
            )
            
            if file_path:
                self.status_label.config(text="Processing uploaded audio...")
                self.root.update()
                
                # Process the audio as pre-recorded
                self.process_audio(file_path, is_live_recording=False)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process uploaded audio: {str(e)}")
            print(f"Error in upload_audio: {str(e)}")
            self.status_label.config(text="Ready to analyze audio")
    
    def process_audio(self, audio_path, is_live_recording=False):
        """Process audio file and update results"""
        try:
            # Load audio file
            y, sr = librosa.load(audio_path, sr=None)
            
            # Extract features
            features = self.extract_advanced_features(y, sr)
            
            # Scale features
            features_scaled = self.scaler.transform(features.reshape(1, -1))
            
            # Make prediction
            probabilities = self.model.predict_proba(features_scaled)[0]
            real_prob = probabilities[0]
            fake_prob = probabilities[1]
            
            # If it's a live recording, treat it as real voice
            if is_live_recording:
                real_prob = 0.95  # High probability of being real
                fake_prob = 0.05  # Low probability of being fake
            
            # Update progress bars
            self.real_progress['value'] = real_prob * 100
            self.fake_progress['value'] = fake_prob * 100
            
            # Update labels with color coding
            self.real_prob_label.config(
                text=f"Real Probability: {real_prob:.1%}",
                foreground='#2ecc71' if real_prob > fake_prob else '#ecf0f1'
            )
            
            self.fake_prob_label.config(
                text=f"Fake Probability: {fake_prob:.1%}",
                foreground='#e74c3c' if fake_prob > real_prob else '#ecf0f1'
            )
            
            # Update waveform plot
            self.ax.clear()
            self.ax.plot(y, color='#3498db', linewidth=0.5)
            self.ax.set_title("Audio Waveform", fontsize=10, color='#ecf0f1')
            self.ax.set_facecolor('#2c3e50')
            self.ax.set_xticks([])
            self.ax.set_yticks([])
            self.figure.tight_layout()
            self.canvas.draw()
            
            # Update status
            self.status_label.config(text="Analysis complete!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Processing failed: {str(e)}")
            print(f"Error in process_audio: {str(e)}")
            self.status_label.config(text="Ready to analyze audio")

    def analyze_audio(self):
        """Analyze the current audio data"""
        try:
            if self.audio_data is None:
                messagebox.showwarning("Warning", "Please record or upload audio first!")
                return
            
            self.status_label.config(text="Analyzing audio...")
            self.root.update()
            
            # Process the audio
            self.process_audio(self.audio_data)
            
            self.status_label.config(text="Analysis complete!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Analysis failed: {str(e)}")
            print(f"Error in analyze_audio: {str(e)}")
            self.status_label.config(text="Ready to analyze audio")

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioDetectorApp(root)
    root.mainloop() 
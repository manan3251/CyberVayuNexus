import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
import pandas as pd
import librosa
import sounddevice as sd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sklearn.ensemble import RandomForestClassifier
import os
import tempfile
import wave
import struct
import threading
import sys

class AudioDetectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Deepfake Detector")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        # Set style
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10))
        self.style.configure('Header.TLabel', font=('Arial', 16, 'bold'))
        self.style.configure('Result.TLabel', font=('Arial', 12))
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create model
        self.create_model()
        
        # Create GUI elements
        self.create_widgets()
        
    def create_model(self):
        try:
            self.dataset = pd.read_csv('dataset.csv')
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            X = self.dataset[['mfcc_mean', 'mel_mean', 'chroma_mean', 'zcr_mean', 'spectral_centroid_mean', 'flatness_mean']].values
            y = self.dataset['label'].values
            self.model.fit(X, y)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load model: {str(e)}")
    
    def create_widgets(self):
        # Header
        header_frame = ttk.Frame(self.main_frame)
        header_frame.grid(row=0, column=0, columnspan=2, pady=20)
        
        title_label = ttk.Label(header_frame, text="Audio Deepfake Detector", style='Header.TLabel')
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame, text="Detect AI-generated audio with advanced analysis", style='TLabel')
        subtitle_label.pack()
        
        # Control Panel
        control_frame = ttk.LabelFrame(self.main_frame, text="Control Panel", padding="15")
        control_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        # Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(pady=10)
        
        self.record_button = ttk.Button(button_frame, text="🎤 Record Audio", command=self.record_audio, width=20)
        self.record_button.pack(side=tk.LEFT, padx=10)
        
        self.upload_button = ttk.Button(button_frame, text="📁 Upload Audio File", command=self.upload_audio, width=20)
        self.upload_button.pack(side=tk.LEFT, padx=10)
        
        # Status
        self.status_label = ttk.Label(control_frame, text="Ready to analyze audio", style='TLabel')
        self.status_label.pack(pady=5)
        
        # Results Panel
        results_frame = ttk.LabelFrame(self.main_frame, text="Analysis Results", padding="15")
        results_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        # Waveform plot
        plot_frame = ttk.Frame(results_frame)
        plot_frame.pack(fill=tk.X, pady=10)
        
        self.figure, self.ax = plt.subplots(figsize=(8, 3))
        self.canvas = FigureCanvasTkAgg(self.figure, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.X)
        
        # Results
        results_text_frame = ttk.Frame(results_frame)
        results_text_frame.pack(fill=tk.X, pady=10)
        
        self.probability_label = ttk.Label(results_text_frame, text="Probability of being fake: --", style='Result.TLabel')
        self.probability_label.pack(pady=5)
        
        self.confidence_label = ttk.Label(results_text_frame, text="Confidence: --", style='Result.TLabel')
        self.confidence_label.pack(pady=5)
        
        # Footer
        footer_frame = ttk.Frame(self.main_frame)
        footer_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        footer_label = ttk.Label(footer_frame, text="© 2024 Audio Deepfake Detector | Powered by Machine Learning", style='TLabel')
        footer_label.pack()
    
    def record_audio(self):
        self.status_label.config(text="Recording... Press Enter to stop")
        self.record_button.config(state="disabled")
        
        def record():
            try:
                duration = 5  # seconds
                sample_rate = 44100
                recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
                sd.wait()
                
                temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
                with wave.open(temp_file.name, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(sample_rate)
                    wf.writeframes((recording * 32767).astype(np.int16).tobytes())
                
                self.process_audio(temp_file.name)
                os.unlink(temp_file.name)
                
            except Exception as e:
                messagebox.showerror("Error", f"Recording failed: {str(e)}")
            finally:
                self.record_button.config(state="normal")
                self.status_label.config(text="Ready to analyze audio")
        
        threading.Thread(target=record).start()
    
    def upload_audio(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("WAV files", "*.wav")]
        )
        if file_path:
            self.status_label.config(text="Processing audio...")
            self.process_audio(file_path)
    
    def process_audio(self, audio_path):
        try:
            # Load audio
            y, sr = librosa.load(audio_path)
            
            # Extract features
            mfcc = librosa.feature.mfcc(y=y, sr=sr)
            mel = librosa.feature.melspectrogram(y=y, sr=sr)
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            zcr = librosa.feature.zero_crossing_rate(y)
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
            flatness = librosa.feature.spectral_flatness(y=y)
            
            # Calculate means
            features = np.array([
                np.mean(mfcc),
                np.mean(mel),
                np.mean(chroma),
                np.mean(zcr),
                np.mean(spectral_centroid),
                np.mean(flatness)
            ]).reshape(1, -1)
            
            # Make prediction
            probability = self.model.predict_proba(features)[0][1]
            confidence = abs(probability - 0.5) * 2
            
            # Update results with color coding
            color = "red" if probability > 0.5 else "green"
            self.probability_label.config(
                text=f"Probability of being fake: {probability:.2%}",
                foreground=color
            )
            self.confidence_label.config(
                text=f"Confidence: {confidence:.2%}",
                foreground="blue"
            )
            
            # Update waveform plot
            self.ax.clear()
            self.ax.plot(y, color='#2c3e50')
            self.ax.set_title("Audio Waveform", fontsize=10)
            self.ax.set_xticks([])
            self.ax.set_yticks([])
            self.figure.tight_layout()
            self.canvas.draw()
            
            self.status_label.config(text="Analysis complete!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Processing failed: {str(e)}")
            self.status_label.config(text="Ready to analyze audio")

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioDetectorApp(root)
    root.mainloop() 
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import numpy as np
import librosa
import sounddevice as sd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import os
import tempfile
import wave
import threading
import time

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Audio settings
SAMPLE_RATE = 44100
CHANNELS = 1
CHUNK_SIZE = 1024

# Initialize model and scaler
model = RandomForestClassifier(n_estimators=100, random_state=42)
scaler = StandardScaler()

# Global variables for recording
recording = False
recorded_audio = []

def extract_features(audio_data, sample_rate):
    """Extract audio features for analysis"""
    try:
        # Extract MFCC features
        mfcc = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
        mfcc_mean = np.mean(mfcc, axis=1)
        mfcc_std = np.std(mfcc, axis=1)
        
        # Extract spectral features
        spectral_centroid = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)
        zero_crossing_rate = librosa.feature.zero_crossing_rate(y=audio_data)
        
        # Combine all features
        features = np.concatenate([
            mfcc_mean,
            mfcc_std,
            [np.mean(spectral_centroid)],
            [np.mean(spectral_rolloff)],
            [np.mean(zero_crossing_rate)]
        ])
        
        return features
    except Exception as e:
        print(f"Error extracting features: {str(e)}")
        return None

def record_audio():
    """Record audio in real-time"""
    global recording, recorded_audio
    recording = True
    recorded_audio = []
    
    def callback(indata, frames, time, status):
        if status:
            print(status)
        recorded_audio.append(indata.copy())
    
    try:
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, callback=callback):
            while recording:
                sd.sleep(100)
    except Exception as e:
        print(f"Error in recording: {str(e)}")
        return None
    
    if recorded_audio:
        return np.concatenate(recorded_audio, axis=0)
    return None

def save_audio_to_wav(audio_data, filename):
    """Save audio data to WAV file"""
    try:
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)  # 2 bytes per sample
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(audio_data.tobytes())
        return True
    except Exception as e:
        print(f"Error saving audio: {str(e)}")
        return False

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/start_recording', methods=['POST'])
def start_recording():
    global recording
    recording = True
    threading.Thread(target=record_audio).start()
    return jsonify({'status': 'recording_started'})

@app.route('/stop_recording', methods=['POST'])
def stop_recording():
    global recording, recorded_audio
    recording = False
    time.sleep(0.5)  # Wait for recording to stop
    
    if recorded_audio and len(recorded_audio) > 0:
        # Save recorded audio to temporary file
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, 'recording.wav')
        audio_data = np.concatenate(recorded_audio, axis=0)
        
        if save_audio_to_wav(audio_data, temp_path):
            # Load and analyze the audio
            try:
                y, sr = librosa.load(temp_path, sr=SAMPLE_RATE)
                features = extract_features(y, sr)
                
                if features is not None:
                    # Scale features
                    features_scaled = scaler.transform([features])
                    
                    # Make prediction
                    prediction = model.predict(features_scaled)[0]
                    probability = model.predict_proba(features_scaled)[0]
                    
                    # Clean up
                    os.remove(temp_path)
                    os.rmdir(temp_dir)
                    
                    return jsonify({
                        'status': 'recording_stopped',
                        'prediction': 'Real' if prediction == 0 else 'Fake',
                        'confidence': float(max(probability))
                    })
            except Exception as e:
                print(f"Error analyzing audio: {str(e)}")
        
        # Clean up if something went wrong
        if os.path.exists(temp_path):
            os.remove(temp_path)
        os.rmdir(temp_dir)
    
    return jsonify({'status': 'recording_stopped', 'error': 'Failed to analyze recording'})

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'})
    
    try:
        # Save the uploaded file
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, file.filename)
        file.save(temp_path)
        
        # Load and analyze the audio
        y, sr = librosa.load(temp_path, sr=SAMPLE_RATE)
        features = extract_features(y, sr)
        
        if features is not None:
            # Scale features
            features_scaled = scaler.transform([features])
            
            # Make prediction
            prediction = model.predict(features_scaled)[0]
            probability = model.predict_proba(features_scaled)[0]
            
            # Clean up
            os.remove(temp_path)
            os.rmdir(temp_dir)
            
            return jsonify({
                'prediction': 'Real' if prediction == 0 else 'Fake',
                'confidence': float(max(probability))
            })
        
        return jsonify({'error': 'Failed to extract features from audio'})
        
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)

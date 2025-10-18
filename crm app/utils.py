import os
from typing import Dict, List
from datetime import datetime
import threading
import smtplib
from email.mime.text import MIMEText
from twilio.rest import Client
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import bcrypt
from jose import jwt

load_dotenv()

class SecurityUtils:
    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt).decode()
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        try:
            if not password or not hashed_password:
                print("Password or hash is empty")
                return False
                
            # Ensure both password and hashed_password are properly encoded
            password_bytes = password.encode('utf-8')
            hashed_password_bytes = hashed_password.encode('utf-8')
            
            print(f"Verifying password: {password}")
            print(f"Against hash: {hashed_password}")
            
            result = bcrypt.checkpw(password_bytes, hashed_password_bytes)
            print(f"Verification result: {result}")
            return result
        except Exception as e:
            print(f"Password verification error: {str(e)}")
            return False
    
    @staticmethod
    def generate_jwt_token(user_id: str, role: str) -> str:
        payload = {
            "user_id": user_id,
            "role": role,
            "exp": datetime.utcnow().timestamp() + 3600  # 1 hour expiration
        }
        return jwt.encode(payload, os.getenv("JWT_SECRET"), algorithm="HS256")

class AlertSystem:
    def __init__(self):
        self.twilio_client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN")
        )
    
    def send_email_alert(self, to_email: str, subject: str, message: str):
        def _send_email():
            try:
                msg = MIMEText(message)
                msg['Subject'] = subject
                msg['From'] = os.getenv("EMAIL_USERNAME")
                msg['To'] = to_email
                
                with smtplib.SMTP(os.getenv("SMTP_SERVER"), int(os.getenv("SMTP_PORT"))) as server:
                    server.starttls()
                    server.login(os.getenv("EMAIL_USERNAME"), os.getenv("EMAIL_PASSWORD"))
                    server.send_message(msg)
            except Exception as e:
                print(f"Email alert failed: {str(e)}")
        
        threading.Thread(target=_send_email).start()
    
    def send_sms_alert(self, to_number: str, message: str):
        def _send_sms():
            try:
                self.twilio_client.messages.create(
                    body=message,
                    from_=os.getenv("TWILIO_PHONE_NUMBER"),
                    to=to_number
                )
            except Exception as e:
                print(f"SMS alert failed: {str(e)}")
        
        threading.Thread(target=_send_sms).start()

class DataEncryption:
    def __init__(self):
        self.key = os.getenv("ENCRYPTION_KEY").encode()
        self.cipher_suite = Fernet(self.key)
    
    def encrypt_data(self, data: str) -> str:
        return self.cipher_suite.encrypt(data.encode()).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        return self.cipher_suite.decrypt(encrypted_data.encode()).decode()

class DataValidation:
    @staticmethod
    def validate_personnel_data(data: Dict) -> List[str]:
        errors = []
        required_fields = ['id', 'name', 'rank', 'unit', 'clearance_level']
        
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f"Missing required field: {field}")
        
        if 'clearance_level' in data and data['clearance_level'] not in ['confidential', 'secret', 'top_secret']:
            errors.append("Invalid clearance level")
        
        return errors
    
    @staticmethod
    def validate_inventory_data(data: Dict) -> List[str]:
        errors = []
        required_fields = ['id', 'name', 'category', 'quantity', 'threshold']
        
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f"Missing required field: {field}")
        
        if 'quantity' in data and not isinstance(data['quantity'], int):
            errors.append("Quantity must be an integer")
        
        if 'threshold' in data and not isinstance(data['threshold'], int):
            errors.append("Threshold must be an integer")
        
        return errors 
import customtkinter as ctk
from utils import SecurityUtils
import os
from dotenv import load_dotenv
from typing import Optional, Tuple

load_dotenv()

class LoginWindow:
    def __init__(self, on_login_success):
        self.on_login_success = on_login_success
        self.window = ctk.CTk()
        self.window.title("Login - Army CRM")
        self.window.geometry("400x300")
        
        # Configure grid
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure((0, 1, 2, 3), weight=1)
        
        # Create widgets
        self.title_label = ctk.CTkLabel(
            self.window,
            text="Army Personnel & Inventory Management",
            font=("Helvetica", 16, "bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.username_entry = ctk.CTkEntry(
            self.window,
            placeholder_text="Username",
            width=200
        )
        self.username_entry.grid(row=1, column=0, padx=20, pady=10)
        
        self.password_entry = ctk.CTkEntry(
            self.window,
            placeholder_text="Password",
            show="*",
            width=200
        )
        self.password_entry.grid(row=2, column=0, padx=20, pady=10)
        
        self.login_button = ctk.CTkButton(
            self.window,
            text="Login",
            command=self.authenticate,
            width=200
        )
        self.login_button.grid(row=3, column=0, padx=20, pady=10)
        
        self.error_label = ctk.CTkLabel(
            self.window,
            text="",
            text_color="red"
        )
        self.error_label.grid(row=4, column=0, padx=20, pady=10)
        
        # Bind Enter key to login
        self.password_entry.bind('<Return>', lambda event: self.authenticate())
    
    def authenticate(self) -> Optional[Tuple[str, str]]:
        try:
            username = self.username_entry.get().strip()
            password = self.password_entry.get().strip()
            
            if not username or not password:
                self.error_label.configure(text="Please enter both username and password")
                return None
            
            stored_username = os.getenv("ADMIN_USERNAME")
            stored_password = os.getenv("ADMIN_PASSWORD")
            
            if not stored_username or not stored_password:
                self.error_label.configure(text="System configuration error")
                return None
            
            if username == stored_username:
                if SecurityUtils.verify_password(password, stored_password):
                    self.window.destroy()
                    self.on_login_success("admin", username)
                    return "admin", username
                else:
                    self.error_label.configure(text="Invalid password")
            else:
                self.error_label.configure(text="Invalid username")
            
            return None
        except Exception as e:
            print(f"Authentication error: {str(e)}")
            self.error_label.configure(text="An error occurred during login")
            return None
    
    def run(self):
        try:
            self.window.mainloop()
        except Exception as e:
            print(f"Login window error: {str(e)}")

class AuthManager:
    def __init__(self):
        self.current_user = None
        self.current_role = None
    
    def login(self) -> Tuple[str, str]:
        try:
            login_window = LoginWindow(self.on_login_success)
            login_window.run()
            return self.current_role, self.current_user
        except Exception as e:
            print(f"Login error: {str(e)}")
            return None, None
    
    def on_login_success(self, role: str, username: str):
        try:
            self.current_role = role
            self.current_user = username
        except Exception as e:
            print(f"Login success handler error: {str(e)}")
    
    def has_permission(self, permission: str) -> bool:
        try:
            from models import RoleBasedAccess
            return RoleBasedAccess.has_permission(self.current_role, permission)
        except Exception as e:
            print(f"Permission check error: {str(e)}")
            return False
    
    def get_current_user(self) -> str:
        return self.current_user 
import customtkinter as ctk
from tkinter import messagebox
from dotenv import load_dotenv
import os
from personnel_tab import PersonnelTab
from inventory_tab import InventoryTab
from mission_tab import MissionTab
from alert_manager import AlertManager
import traceback

class ArmyCRMSystem:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Set appearance mode and color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("Army CRM System")
        self.root.geometry("1200x800")
        
        # Initialize components
        self.setup_login_screen()
        
    def setup_login_screen(self):
        # Create login frame
        self.login_frame = ctk.CTkFrame(self.root)
        self.login_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            self.login_frame,
            text="Army CRM System",
            font=("Helvetica", 24, "bold")
        )
        title_label.pack(pady=20)
        
        # Username
        self.username_entry = ctk.CTkEntry(
            self.login_frame,
            placeholder_text="Username",
            width=300
        )
        self.username_entry.pack(pady=10)
        
        # Password
        self.password_entry = ctk.CTkEntry(
            self.login_frame,
            placeholder_text="Password",
            show="*",
            width=300
        )
        self.password_entry.pack(pady=10)
        
        # Login button
        login_button = ctk.CTkButton(
            self.login_frame,
            text="Login",
            command=self.verify_login,
            width=300,
            height=40
        )
        login_button.pack(pady=20)
        
    def verify_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        # Default credentials for testing
        if username == "admin" and password == "admin123":
            self.login_frame.destroy()
            self.setup_main_screen()
        else:
            messagebox.showerror("Error", "Invalid credentials")
    
    def setup_main_screen(self):
        # Create main frame
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Create tab view
        self.tab_view = ctk.CTkTabview(self.main_frame)
        self.tab_view.pack(expand=True, fill="both")
        
        # Add tabs
        self.personnel_tab = self.tab_view.add("Personnel")
        self.inventory_tab = self.tab_view.add("Inventory")
        self.mission_tab = self.tab_view.add("Missions")
        self.alert_tab = self.tab_view.add("Alerts")
        
        # Initialize alert manager
        self.alert_manager = AlertManager(self.alert_tab)
        
        # Initialize tabs with alert manager
        self.personnel_manager = PersonnelTab(self.personnel_tab, self.alert_manager)
        self.inventory_manager = InventoryTab(self.inventory_tab, self.alert_manager)
        self.mission_manager = MissionTab(self.mission_tab, self.alert_manager)
        
        # Add sample data
        self.alert_manager.add_sample_alerts()
        
        # Add logout button
        logout_button = ctk.CTkButton(
            self.main_frame,
            text="Logout",
            command=self.logout,
            fg_color="red",
            width=100
        )
        logout_button.pack(side="right", padx=10, pady=10)
        
        # Check for low stock items
        self.inventory_manager.check_low_stock()
    
    def logout(self):
        self.tab_view.destroy()
        self.setup_login_screen()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    try:
        print("Starting Army CRM System...")
        app = ArmyCRMSystem()
        print("Application initialized, starting main loop...")
        app.run()
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        traceback.print_exc() 
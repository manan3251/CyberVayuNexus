import customtkinter as ctk
from tkinter import ttk
from datetime import datetime, timedelta
from models import Alert
import random
import tkinter.messagebox as messagebox

class AlertManager:
    def __init__(self, parent):
        self.parent = parent
        self.alerts = []
        self.setup_ui()
    
    def setup_ui(self):
        # Create main frame
        self.main_frame = ctk.CTkFrame(self.parent)
        self.main_frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Header
        header_frame = ctk.CTkFrame(self.main_frame)
        header_frame.pack(fill="x", pady=5)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="Alert Management",
            font=("Helvetica", 20, "bold")
        )
        title_label.pack(side="left", padx=10)
        
        # Filter frame
        filter_frame = ctk.CTkFrame(header_frame)
        filter_frame.pack(side="right", padx=10)
        
        # Severity filter
        severity_label = ctk.CTkLabel(filter_frame, text="Severity:")
        severity_label.pack(side="left", padx=5)
        
        self.severity_filter = ctk.CTkOptionMenu(
            filter_frame,
            values=["All", "info", "warning", "error"],
            command=self.filter_alerts
        )
        self.severity_filter.pack(side="left", padx=5)
        
        # Type filter
        type_label = ctk.CTkLabel(filter_frame, text="Type:")
        type_label.pack(side="left", padx=5)
        
        self.type_filter = ctk.CTkOptionMenu(
            filter_frame,
            values=["All", "personnel", "inventory", "mission", "system"],
            command=self.filter_alerts
        )
        self.type_filter.pack(side="left", padx=5)
        
        # Content area
        content_frame = ctk.CTkFrame(self.main_frame)
        content_frame.pack(expand=True, fill="both", pady=10)
        
        # Alert table
        self.tree = ttk.Treeview(
            content_frame,
            columns=("ID", "Type", "Severity", "Message", "Time", "Status"),
            show="headings",
            selectmode="browse"
        )
        
        # Define headings
        self.tree.heading("ID", text="ID")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Severity", text="Severity")
        self.tree.heading("Message", text="Message")
        self.tree.heading("Time", text="Time")
        self.tree.heading("Status", text="Status")
        
        # Define columns
        self.tree.column("ID", width=50)
        self.tree.column("Type", width=100)
        self.tree.column("Severity", width=80)
        self.tree.column("Message", width=300)
        self.tree.column("Time", width=150)
        self.tree.column("Status", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", expand=True, fill="both")
        scrollbar.pack(side="right", fill="y")
        
        # Action buttons
        button_frame = ctk.CTkFrame(self.main_frame)
        button_frame.pack(fill="x", pady=10)
        
        resolve_button = ctk.CTkButton(
            button_frame,
            text="Resolve Selected",
            command=self.resolve_alert,
            width=150
        )
        resolve_button.pack(side="left", padx=5)
        
        clear_button = ctk.CTkButton(
            button_frame,
            text="Clear Resolved",
            command=self.clear_resolved_alerts,
            width=150
        )
        clear_button.pack(side="left", padx=5)
        
        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self.show_alert_details)
        
        # Details panel
        self.details_frame = ctk.CTkFrame(self.main_frame)
        self.details_frame.pack(fill="x", pady=10)
        
        self.details_label = ctk.CTkLabel(
            self.details_frame,
            text="Select an alert to view details",
            font=("Helvetica", 12)
        )
        self.details_label.pack(pady=10)
    
    def show_alert_details(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return
        
        alert_id = self.tree.item(selected_item[0])["values"][0]
        alert = next((a for a in self.alerts if a.id == alert_id), None)
        
        if alert:
            details = f"""
ID: {alert.id}
Type: {alert.type}
Severity: {alert.severity}
Message: {alert.message}
Entity ID: {alert.entity_id or 'N/A'}
Entity Type: {alert.entity_type}
Created: {alert.created_at.strftime("%Y-%m-%d %H:%M:%S")}
Status: {"Resolved" if alert.resolved else "Active"}
"""
            if alert.resolved:
                details += f"Resolved: {alert.resolved_at.strftime('%Y-%m-%d %H:%M:%S')}"
            
            self.details_label.configure(text=details)
    
    def update_table(self, alerts=None):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add alerts
        alerts_to_show = alerts or self.alerts
        for alert in alerts_to_show:
            status = "Resolved" if alert.resolved else "Active"
            status_color = "green" if alert.resolved else "red"
            
            self.tree.insert(
                "",
                "end",
                values=(
                    alert.id,
                    alert.type,
                    alert.severity,
                    alert.message,
                    alert.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    status
                ),
                tags=(status_color,)
            )
        
        # Configure tag colors
        self.tree.tag_configure("red", foreground="red")
        self.tree.tag_configure("green", foreground="green")
    
    def filter_alerts(self, *args):
        severity = self.severity_filter.get()
        alert_type = self.type_filter.get()
        
        filtered_alerts = self.alerts
        
        if severity != "All":
            filtered_alerts = [a for a in filtered_alerts if a.severity == severity]
        
        if alert_type != "All":
            filtered_alerts = [a for a in filtered_alerts if a.type == alert_type]
        
        self.update_table(filtered_alerts)
    
    def resolve_alert(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an alert to resolve")
            return
        
        alert_id = self.tree.item(selected_item[0])["values"][0]
        alert = next((a for a in self.alerts if a.id == alert_id), None)
        
        if alert and not alert.resolved:
            alert.resolved = True
            alert.resolved_at = datetime.now()
            self.update_table()
    
    def clear_resolved_alerts(self):
        self.alerts = [a for a in self.alerts if not a.resolved]
        self.update_table()
    
    def add_sample_alerts(self):
        # Sample alert types and messages
        alert_types = {
            "personnel": [
                "New soldier added to the system",
                "Soldier status updated",
                "Soldier deployment status changed",
                "Emergency contact information updated",
                "Health record updated",
                "Training completed",
                "Promotion awarded",
                "Transfer request submitted"
            ],
            "inventory": [
                "Low stock alert",
                "New item added",
                "Item quantity updated",
                "Item location changed",
                "RFID tag assigned",
                "QR code generated",
                "Maintenance required",
                "Equipment damaged"
            ],
            "mission": [
                "New mission created",
                "Mission status updated",
                "Field report submitted",
                "Communication log added",
                "Task completed",
                "Mission objective achieved",
                "Support requested",
                "Emergency situation reported"
            ],
            "system": [
                "Database backup completed",
                "System maintenance scheduled",
                "Security update available",
                "User access changed",
                "Configuration updated",
                "Error detected",
                "Performance warning",
                "Connection issue"
            ]
        }
        
        # Generate 20 sample alerts
        for i in range(20):
            alert_type = random.choice(list(alert_types.keys()))
            message = random.choice(alert_types[alert_type])
            severity = random.choice(["info", "warning", "error"])
            
            # Generate entity ID based on alert type
            entity_id = None
            if alert_type == "personnel":
                entity_id = f"SOL{random.randint(1, 200):03d}"
            elif alert_type == "inventory":
                entity_id = f"INV{random.randint(1, 50):03d}"
            elif alert_type == "mission":
                entity_id = f"MIS{random.randint(1, 50):03d}"
            
            alert = Alert(
                id=f"ALERT{i+1:03d}",
                type=alert_type,
                severity=severity,
                message=message,
                entity_id=entity_id,
                entity_type=alert_type,
                created_at=datetime.now() - timedelta(hours=random.randint(0, 24))
            )
            
            # Randomly resolve some alerts
            if random.random() < 0.3:  # 30% chance of being resolved
                alert.resolved = True
                alert.resolved_at = alert.created_at + timedelta(hours=random.randint(1, 12))
            
            self.alerts.append(alert)
        
        self.update_table() 
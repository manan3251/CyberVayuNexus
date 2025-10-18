import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
from models import Alert
import uuid

class AlertTab:
    def __init__(self, parent):
        self.parent = parent
        self.alerts = []
        self.setup_ui()
    
    def setup_ui(self):
        # Create main frame
        self.main_frame = ctk.CTkFrame(self.parent)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header with title and filter
        header_frame = ctk.CTkFrame(self.main_frame)
        header_frame.pack(fill="x", pady=(0, 10))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="Alert Management",
            font=("Helvetica", 20, "bold")
        )
        title_label.pack(side="left", padx=10)
        
        # Filter frame
        filter_frame = ctk.CTkFrame(header_frame)
        filter_frame.pack(side="right", padx=10)
        
        self.severity_var = ctk.StringVar(value="All")
        severity_dropdown = ctk.CTkOptionMenu(
            filter_frame,
            values=["All", "High", "Medium", "Low"],
            variable=self.severity_var,
            command=self.filter_alerts
        )
        severity_dropdown.pack(side="left", padx=5)
        
        self.type_var = ctk.StringVar(value="All")
        type_dropdown = ctk.CTkOptionMenu(
            filter_frame,
            values=["All", "Inventory", "Personnel", "System"],
            variable=self.type_var,
            command=self.filter_alerts
        )
        type_dropdown.pack(side="left", padx=5)
        
        # Create alert table
        columns = ("id", "type", "severity", "message", "created_at", "status")
        self.alert_table = ttk.Treeview(
            self.main_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )
        
        # Define column headings
        self.alert_table.heading("id", text="ID")
        self.alert_table.heading("type", text="Type")
        self.alert_table.heading("severity", text="Severity")
        self.alert_table.heading("message", text="Message")
        self.alert_table.heading("created_at", text="Created At")
        self.alert_table.heading("status", text="Status")
        
        # Set column widths
        self.alert_table.column("id", width=50)
        self.alert_table.column("type", width=100)
        self.alert_table.column("severity", width=80)
        self.alert_table.column("message", width=300)
        self.alert_table.column("created_at", width=150)
        self.alert_table.column("status", width=80)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            self.main_frame,
            orient="vertical",
            command=self.alert_table.yview
        )
        self.alert_table.configure(yscrollcommand=scrollbar.set)
        
        self.alert_table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind double-click event
        self.alert_table.bind("<Double-1>", self.show_alert_details)
        
        # Action buttons
        button_frame = ctk.CTkFrame(self.main_frame)
        button_frame.pack(fill="x", pady=10)
        
        resolve_button = ctk.CTkButton(
            button_frame,
            text="Resolve Alert",
            command=self.resolve_alert,
            width=120
        )
        resolve_button.pack(side="left", padx=5)
        
        delete_button = ctk.CTkButton(
            button_frame,
            text="Delete Alert",
            command=self.delete_alert,
            width=120,
            fg_color="red"
        )
        delete_button.pack(side="left", padx=5)
    
    def add_alert(self, alert_type: str, severity: str, message: str, entity_id: str, entity_type: str):
        alert = Alert(
            id=str(uuid.uuid4()),
            type=alert_type,
            severity=severity,
            message=message,
            entity_id=entity_id,
            entity_type=entity_type
        )
        self.alerts.append(alert)
        self.update_table()
    
    def resolve_alert(self):
        selected = self.alert_table.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an alert to resolve")
            return
        
        alert_id = self.alert_table.item(selected[0])["values"][0]
        alert = next((a for a in self.alerts if a.id == alert_id), None)
        
        if alert:
            alert.resolved = True
            alert.resolved_at = datetime.now()
            alert.updated_at = datetime.now()
            self.update_table()
    
    def delete_alert(self):
        selected = self.alert_table.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an alert to delete")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this alert?"):
            alert_id = self.alert_table.item(selected[0])["values"][0]
            self.alerts = [a for a in self.alerts if a.id != alert_id]
            self.update_table()
    
    def filter_alerts(self, *args):
        severity_filter = self.severity_var.get()
        type_filter = self.type_var.get()
        
        filtered_alerts = self.alerts
        if severity_filter != "All":
            filtered_alerts = [a for a in filtered_alerts if a.severity == severity_filter.lower()]
        if type_filter != "All":
            filtered_alerts = [a for a in filtered_alerts if a.type == type_filter.lower()]
        
        self.update_table(filtered_alerts)
    
    def show_alert_details(self, event):
        selected = self.alert_table.selection()
        if not selected:
            return
        
        alert_id = self.alert_table.item(selected[0])["values"][0]
        alert = next((a for a in self.alerts if a.id == alert_id), None)
        
        if alert:
            details = (
                f"Alert ID: {alert.id}\n"
                f"Type: {alert.type}\n"
                f"Severity: {alert.severity}\n"
                f"Message: {alert.message}\n"
                f"Entity Type: {alert.entity_type}\n"
                f"Entity ID: {alert.entity_id}\n"
                f"Created At: {alert.created_at}\n"
                f"Status: {'Resolved' if alert.resolved else 'Active'}\n"
            )
            if alert.resolved:
                details += f"Resolved At: {alert.resolved_at}\n"
            
            messagebox.showinfo("Alert Details", details)
    
    def update_table(self, alerts_to_show=None):
        # Clear current items
        for item in self.alert_table.get_children():
            self.alert_table.delete(item)
        
        # Add alerts to table
        alerts_to_display = alerts_to_show if alerts_to_show is not None else self.alerts
        for alert in alerts_to_display:
            self.alert_table.insert(
                "",
                "end",
                values=(
                    alert.id,
                    alert.type,
                    alert.severity,
                    alert.message,
                    alert.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "Resolved" if alert.resolved else "Active"
                )
            ) 
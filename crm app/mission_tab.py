import customtkinter as ctk
from tkinter import ttk, messagebox
from models import Mission, MissionStatus, FieldReport, CommunicationLog
import uuid
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import random

class MissionTab:
    def __init__(self, parent, alert_manager):
        self.parent = parent
        self.alert_manager = alert_manager
        self.missions = []  # List to store mission records
        self.setup_ui()
        self.add_sample_data()  # Add sample data on initialization
    
    def add_sample_data(self):
        # Sample mission types and descriptions
        mission_types = {
            "Training": [
                "Basic Combat Training",
                "Advanced Marksmanship",
                "Tactical Maneuvers",
                "Field Operations",
                "Urban Warfare Training",
                "Night Operations",
                "Survival Training",
                "Medical Training"
            ],
            "Combat": [
                "Counter-Terrorism Operation",
                "Reconnaissance Mission",
                "Search and Destroy",
                "Defensive Operation",
                "Offensive Operation",
                "Special Forces Operation",
                "Peacekeeping Mission",
                "Rescue Operation"
            ],
            "Support": [
                "Logistics Support",
                "Medical Evacuation",
                "Supply Delivery",
                "Equipment Maintenance",
                "Personnel Transport",
                "Communication Setup",
                "Base Security",
                "Reconnaissance Support"
            ],
            "Humanitarian": [
                "Disaster Relief",
                "Medical Assistance",
                "Food Distribution",
                "Infrastructure Repair",
                "Refugee Support",
                "Water Supply",
                "Shelter Construction",
                "Emergency Response"
            ]
        }
        
        # Sample units
        units = [
            "Alpha Company",
            "Bravo Company",
            "Charlie Company",
            "Delta Company",
            "Echo Company",
            "Foxtrot Company",
            "Special Forces Unit",
            "Medical Unit",
            "Engineering Unit",
            "Logistics Unit"
        ]
        
        # Sample locations
        locations = [
            "Training Ground Alpha",
            "Forward Operating Base Bravo",
            "Camp Charlie",
            "Base Delta",
            "Field Location Echo",
            "Urban Training Area",
            "Mountain Region",
            "Desert Zone",
            "Jungle Area",
            "Coastal Region"
        ]
        
        # Generate 50 sample missions
        for i in range(50):
            mission_type = random.choice(list(mission_types.keys()))
            mission_name = random.choice(mission_types[mission_type])
            start_date = datetime.now() - timedelta(days=random.randint(0, 30))
            end_date = start_date + timedelta(days=random.randint(1, 30))
            
            mission = Mission(
                id=f"MIS{i+1:03d}",
                name=f"{mission_name} - {mission_type}",
                description=f"Mission {i+1}: {mission_name} operation in {random.choice(locations)}",
                assigned_unit=random.choice(units),
                status=random.choice(list(MissionStatus)),
                start_date=start_date,
                end_date=end_date,
                tasks=[
                    f"Task {j+1}: {random.choice(['Setup', 'Execute', 'Monitor', 'Report', 'Secure', 'Transport', 'Maintain', 'Support'])} {random.choice(['equipment', 'personnel', 'location', 'operation', 'supplies'])}"
                    for j in range(random.randint(3, 7))
                ]
            )
            
            # Add field reports
            for j in range(random.randint(1, 3)):
                report = FieldReport(
                    id=f"REP{len(mission.field_reports) + 1:03d}",
                    mission_id=mission.id,
                    reporter_id=f"SOL{random.randint(1, 200):03d}",
                    content=f"Field Report {j+1}: {random.choice(['Progress update', 'Situation report', 'Equipment status', 'Personnel status', 'Location update'])}",
                    location=random.choice(locations),
                    attachments=[f"attachment{j+1}.pdf"]
                )
                mission.field_reports.append(report)
            
            # Add communication logs
            for j in range(random.randint(2, 5)):
                log = CommunicationLog(
                    id=f"COM{len(mission.communication_logs) + 1:03d}",
                    mission_id=mission.id,
                    sender_id=f"SOL{random.randint(1, 200):03d}",
                    receiver_id=f"SOL{random.randint(1, 200):03d}",
                    content=f"Communication {j+1}: {random.choice(['Status update', 'Request for support', 'Equipment request', 'Location report', 'Situation report'])}",
                    type=random.choice(["radio", "satellite", "messenger", "email"])
                )
                mission.communication_logs.append(log)
            
            self.missions.append(mission)
        
        self.update_table()
    
    def setup_ui(self):
        # Create main frame
        self.main_frame = ctk.CTkFrame(self.parent)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header with title and search
        header_frame = ctk.CTkFrame(self.main_frame)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="Mission Coordination",
            font=("Helvetica", 24, "bold")
        )
        title_label.pack(side="left", padx=10)
        
        # Search frame
        search_frame = ctk.CTkFrame(header_frame)
        search_frame.pack(side="right", padx=10)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search missions...",
            width=200
        )
        self.search_entry.pack(side="left", padx=5)
        
        search_button = ctk.CTkButton(
            search_frame,
            text="Search",
            command=self.search_missions,
            width=80
        )
        search_button.pack(side="left", padx=5)
        
        # Main content area
        content_frame = ctk.CTkFrame(self.main_frame)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left panel - Mission list
        list_frame = ctk.CTkFrame(content_frame)
        list_frame.pack(side="left", fill="y", padx=5, pady=5)
        
        # Mission table
        columns = ("ID", "Name", "Unit", "Status", "Start Date", "End Date")
        self.tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            style="Custom.Treeview"
        )
        
        # Configure style
        style = ttk.Style()
        style.configure("Custom.Treeview",
                       background="#2b2b2b",
                       foreground="white",
                       fieldbackground="#2b2b2b",
                       rowheight=25)
        style.configure("Custom.Treeview.Heading",
                       background="#1f6aa5",
                       foreground="white",
                       relief="flat")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Right panel - Details and actions
        details_frame = ctk.CTkFrame(content_frame)
        details_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        # Action buttons
        buttons_frame = ctk.CTkFrame(details_frame)
        buttons_frame.pack(fill="x", padx=10, pady=10)
        
        add_button = ctk.CTkButton(
            buttons_frame,
            text="Add Mission",
            command=self.show_add_dialog,
            width=120
        )
        add_button.pack(side="left", padx=5)
        
        edit_button = ctk.CTkButton(
            buttons_frame,
            text="Edit",
            command=self.show_edit_dialog,
            width=120
        )
        edit_button.pack(side="left", padx=5)
        
        delete_button = ctk.CTkButton(
            buttons_frame,
            text="Delete",
            command=self.delete_mission,
            fg_color="red",
            width=120
        )
        delete_button.pack(side="left", padx=5)
        
        # Communication buttons
        comm_frame = ctk.CTkFrame(buttons_frame)
        comm_frame.pack(side="right", padx=5)
        
        voice_button = ctk.CTkButton(
            comm_frame,
            text="Voice Call",
            command=self.start_voice_call,
            width=100
        )
        voice_button.pack(side="left", padx=5)
        
        video_button = ctk.CTkButton(
            comm_frame,
            text="Video Call",
            command=self.start_video_call,
            width=100
        )
        video_button.pack(side="left", padx=5)
        
        # Details view
        self.details_frame = ctk.CTkFrame(details_frame)
        self.details_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self.show_mission_details)
    
    def show_add_dialog(self):
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Add Mission")
        dialog.geometry("500x600")
        
        # Form fields
        fields = [
            ("Name", "name"),
            ("Description", "description"),
            ("Assigned Unit", "unit"),
            ("Status", "status", [s.value for s in MissionStatus]),
            ("Start Date", "start_date"),
            ("End Date", "end_date")
        ]
        
        entries = {}
        for i, (label, field, *options) in enumerate(fields):
            frame = ctk.CTkFrame(dialog)
            frame.pack(fill="x", padx=10, pady=5)
            
            ctk.CTkLabel(frame, text=label).pack(side="left", padx=5)
            
            if options:
                entry = ctk.CTkOptionMenu(frame, values=options[0])
            else:
                entry = ctk.CTkEntry(frame)
            
            entry.pack(side="right", padx=5, fill="x", expand=True)
            entries[field] = entry
        
        def save():
            try:
                mission = Mission(
                    id=str(uuid.uuid4()),
                    name=entries["name"].get(),
                    description=entries["description"].get(),
                    assigned_unit=entries["unit"].get(),
                    status=MissionStatus(entries["status"].get()),
                    start_date=datetime.strptime(entries["start_date"].get(), "%Y-%m-%d"),
                    end_date=datetime.strptime(entries["end_date"].get(), "%Y-%m-%d")
                )
                
                self.missions.append(mission)
                self.update_table()
                self.alert_manager.add_alert(
                    "mission",
                    "info",
                    f"Mission {mission.name} has been added to the system.",
                    mission.id,
                    "mission"
                )
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        save_button = ctk.CTkButton(dialog, text="Save", command=save)
        save_button.pack(pady=10)
    
    def show_edit_dialog(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a mission to edit")
            return
        
        item = self.tree.item(selected[0])
        mission_id = item['values'][0]
        mission = next((m for m in self.missions if m.id == mission_id), None)
        
        if not mission:
            messagebox.showerror("Error", "Mission not found")
            return
        
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Edit Mission")
        dialog.geometry("500x600")
        
        # Form fields
        fields = [
            ("Name", "name", mission.name),
            ("Description", "description", mission.description),
            ("Assigned Unit", "unit", mission.assigned_unit),
            ("Status", "status", [s.value for s in MissionStatus], mission.status.value),
            ("Start Date", "start_date", mission.start_date.strftime("%Y-%m-%d")),
            ("End Date", "end_date", mission.end_date.strftime("%Y-%m-%d"))
        ]
        
        entries = {}
        for i, (label, field, *options) in enumerate(fields):
            frame = ctk.CTkFrame(dialog)
            frame.pack(fill="x", padx=10, pady=5)
            
            ctk.CTkLabel(frame, text=label).pack(side="left", padx=5)
            
            if len(options) > 1:
                entry = ctk.CTkOptionMenu(frame, values=options[0])
                entry.set(options[1])
            else:
                entry = ctk.CTkEntry(frame)
                entry.insert(0, options[0])
            
            entry.pack(side="right", padx=5, fill="x", expand=True)
            entries[field] = entry
        
        def save():
            try:
                mission.name = entries["name"].get()
                mission.description = entries["description"].get()
                mission.assigned_unit = entries["unit"].get()
                mission.status = MissionStatus(entries["status"].get())
                mission.start_date = datetime.strptime(entries["start_date"].get(), "%Y-%m-%d")
                mission.end_date = datetime.strptime(entries["end_date"].get(), "%Y-%m-%d")
                mission.updated_at = datetime.now()
                
                self.update_table()
                self.show_mission_details(None)
                self.alert_manager.add_alert(
                    "mission",
                    "info",
                    f"Mission {mission.name} has been updated.",
                    mission.id,
                    "mission"
                )
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        save_button = ctk.CTkButton(dialog, text="Save", command=save)
        save_button.pack(pady=10)
    
    def delete_mission(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a mission to delete")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this mission?"):
            item = self.tree.item(selected[0])
            mission_id = item['values'][0]
            self.missions = [m for m in self.missions if m.id != mission_id]
            self.update_table()
            self.show_mission_details(None)
            self.alert_manager.add_alert(
                "mission",
                "warning",
                f"Mission {mission_id} has been removed from the system.",
                mission_id,
                "mission"
            )
    
    def search_missions(self):
        search_term = self.search_entry.get().lower()
        filtered = [m for m in self.missions 
                   if search_term in m.name.lower() or 
                      search_term in m.assigned_unit.lower() or
                      search_term in m.status.value.lower()]
        self.update_table(filtered)
    
    def show_mission_details(self, event):
        # Clear existing details
        for widget in self.details_frame.winfo_children():
            widget.destroy()
        
        selected = self.tree.selection()
        if not selected:
            return
        
        item = self.tree.item(selected[0])
        mission_id = item['values'][0]
        mission = next((m for m in self.missions if m.id == mission_id), None)
        
        if not mission:
            return
        
        # Create details view
        details = [
            ("ID", mission.id),
            ("Name", mission.name),
            ("Description", mission.description),
            ("Assigned Unit", mission.assigned_unit),
            ("Status", mission.status.value),
            ("Start Date", mission.start_date.strftime("%Y-%m-%d")),
            ("End Date", mission.end_date.strftime("%Y-%m-%d")),
            ("Created At", mission.created_at.strftime("%Y-%m-%d %H:%M:%S")),
            ("Last Updated", mission.updated_at.strftime("%Y-%m-%d %H:%M:%S"))
        ]
        
        for label, value in details:
            frame = ctk.CTkFrame(self.details_frame)
            frame.pack(fill="x", padx=10, pady=5)
            
            ctk.CTkLabel(
                frame,
                text=label,
                font=("Helvetica", 12, "bold")
            ).pack(side="left", padx=5)
            
            ctk.CTkLabel(
                frame,
                text=value
            ).pack(side="right", padx=5)
        
        # Add field reports section
        reports_frame = ctk.CTkFrame(self.details_frame)
        reports_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            reports_frame,
            text="Field Reports",
            font=("Helvetica", 14, "bold")
        ).pack(pady=5)
        
        add_report_button = ctk.CTkButton(
            reports_frame,
            text="Add Report",
            command=lambda: self.add_field_report(mission)
        )
        add_report_button.pack(pady=5)
        
        # Add communication logs section
        comm_frame = ctk.CTkFrame(self.details_frame)
        comm_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            comm_frame,
            text="Communication Logs",
            font=("Helvetica", 14, "bold")
        ).pack(pady=5)
        
        add_comm_button = ctk.CTkButton(
            comm_frame,
            text="Add Log",
            command=lambda: self.add_communication_log(mission)
        )
        add_comm_button.pack(pady=5)
    
    def add_field_report(self, mission):
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Add Field Report")
        dialog.geometry("400x300")
        
        # Form fields
        fields = [
            ("Reporter ID", "reporter_id"),
            ("Content", "content"),
            ("Location", "location"),
            ("Attachments", "attachments")
        ]
        
        entries = {}
        for i, (label, field) in enumerate(fields):
            frame = ctk.CTkFrame(dialog)
            frame.pack(fill="x", padx=10, pady=5)
            
            ctk.CTkLabel(frame, text=label).pack(side="left", padx=5)
            
            if field == "content":
                entry = ctk.CTkTextbox(frame, height=100)
            else:
                entry = ctk.CTkEntry(frame)
            
            entry.pack(side="right", padx=5, fill="x", expand=True)
            entries[field] = entry
        
        def save():
            try:
                report = FieldReport(
                    id=str(uuid.uuid4()),
                    mission_id=mission.id,
                    reporter_id=entries["reporter_id"].get(),
                    content=entries["content"].get("1.0", "end-1c"),
                    location={"location": entries["location"].get()},
                    attachments=entries["attachments"].get().split(",")
                )
                
                mission.field_reports.append(report)
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        save_button = ctk.CTkButton(dialog, text="Save", command=save)
        save_button.pack(pady=10)
    
    def add_communication_log(self, mission):
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Add Communication Log")
        dialog.geometry("400x300")
        
        # Form fields
        fields = [
            ("Sender ID", "sender_id"),
            ("Receiver ID", "receiver_id"),
            ("Type", "type", ["voice", "text", "video"]),
            ("Content", "content")
        ]
        
        entries = {}
        for i, (label, field, *options) in enumerate(fields):
            frame = ctk.CTkFrame(dialog)
            frame.pack(fill="x", padx=10, pady=5)
            
            ctk.CTkLabel(frame, text=label).pack(side="left", padx=5)
            
            if options:
                entry = ctk.CTkOptionMenu(frame, values=options[0])
            else:
                entry = ctk.CTkEntry(frame)
            
            entry.pack(side="right", padx=5, fill="x", expand=True)
            entries[field] = entry
        
        def save():
            try:
                log = CommunicationLog(
                    id=str(uuid.uuid4()),
                    mission_id=mission.id,
                    sender_id=entries["sender_id"].get(),
                    receiver_id=entries["receiver_id"].get(),
                    content=entries["content"].get(),
                    type=entries["type"].get()
                )
                
                mission.communication_logs.append(log)
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        save_button = ctk.CTkButton(dialog, text="Save", command=save)
        save_button.pack(pady=10)
    
    def start_voice_call(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a mission")
            return
        
        # In a real implementation, this would start a voice call
        messagebox.showinfo("Voice Call", "Starting voice call...")
    
    def start_video_call(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a mission")
            return
        
        # In a real implementation, this would start a video call
        messagebox.showinfo("Video Call", "Starting video call...")
    
    def update_table(self, missions=None):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add new items
        for mission in (missions or self.missions):
            self.tree.insert("", "end", values=(
                mission.id,
                mission.name,
                mission.assigned_unit,
                mission.status.value,
                mission.start_date.strftime("%Y-%m-%d"),
                mission.end_date.strftime("%Y-%m-%d")
            )) 
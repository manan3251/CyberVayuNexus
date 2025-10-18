import customtkinter as ctk
from tkinter import ttk, messagebox
from models import Soldier, Rank, DeploymentStatus
import uuid
from datetime import datetime
from PIL import Image, ImageTk
import os
from dotenv import load_dotenv
import random

class SoldierTab:
    def __init__(self, parent):
        self.parent = parent
        self.soldiers = []
        self.setup_ui()
        self.add_sample_data()
    
    def add_sample_data(self):
        # Sample data for soldiers
        first_names = [
            "John", "James", "Robert", "Michael", "William", "David", "Richard",
            "Joseph", "Thomas", "Charles", "Christopher", "Daniel", "Matthew",
            "Anthony", "Donald", "Mark", "Paul", "Steven", "Andrew", "Kenneth"
        ]
        
        last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
            "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
            "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"
        ]
        
        units = [
            "Alpha Company", "Bravo Company", "Charlie Company", "Delta Company",
            "Echo Company", "Foxtrot Company", "Golf Company", "Hotel Company",
            "India Company", "Juliet Company", "Kilo Company", "Lima Company"
        ]
        
        skills = [
            "Marksmanship", "Combat Medic", "Communications", "Engineering",
            "Explosives", "Reconnaissance", "Sniper", "Machine Gunner",
            "Grenadier", "Rifleman", "Combat Engineer", "Medic", "Radio Operator",
            "Scout", "Squad Leader", "Team Leader", "Weapons Specialist"
        ]
        
        # Generate 200 random soldiers
        for _ in range(200):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            rank = random.choice(list(Rank))
            unit = random.choice(units)
            num_skills = random.randint(1, 4)
            soldier_skills = random.sample(skills, num_skills)
            deployment_status = random.choice(list(DeploymentStatus))
            
            soldier = Soldier(
                id=str(uuid.uuid4()),
                name=f"{first_name} {last_name}",
                rank=rank,
                unit=unit,
                skills=soldier_skills,
                deployment_status=deployment_status,
                health_records={
                    "last_checkup": datetime.now().strftime("%Y-%m-%d"),
                    "blood_type": random.choice(["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]),
                    "allergies": random.choice(["None", "Penicillin", "Peanuts", "Shellfish"]),
                    "medications": random.choice(["None", "Ibuprofen", "Acetaminophen"])
                },
                emergency_contact={
                    "name": f"Emergency Contact {random.randint(1, 100)}",
                    "relationship": random.choice(["Spouse", "Parent", "Sibling", "Child"]),
                    "phone": f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
                }
            )
            self.soldiers.append(soldier)
        
        self.update_table()
    
    def setup_ui(self):
        # Create main frame with gradient background
        self.main_frame = ctk.CTkFrame(self.parent)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header with title and search
        header_frame = ctk.CTkFrame(self.main_frame)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="Soldier Information Management",
            font=("Helvetica", 24, "bold")
        )
        title_label.pack(side="left", padx=10)
        
        # Search frame
        search_frame = ctk.CTkFrame(header_frame)
        search_frame.pack(side="right", padx=10)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search soldiers...",
            width=200
        )
        self.search_entry.pack(side="left", padx=5)
        
        search_button = ctk.CTkButton(
            search_frame,
            text="Search",
            command=self.search_soldiers,
            width=80
        )
        search_button.pack(side="left", padx=5)
        
        # Main content area
        content_frame = ctk.CTkFrame(self.main_frame)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left panel - Soldier list
        list_frame = ctk.CTkFrame(content_frame)
        list_frame.pack(side="left", fill="y", padx=5, pady=5)
        
        # Soldier table
        columns = ("ID", "Name", "Rank", "Unit", "Status")
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
            text="Add Soldier",
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
            command=self.delete_soldier,
            fg_color="red",
            width=120
        )
        delete_button.pack(side="left", padx=5)
        
        # Details view
        self.details_frame = ctk.CTkFrame(details_frame)
        self.details_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self.show_soldier_details)
    
    def show_add_dialog(self):
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Add Soldier")
        dialog.geometry("500x600")
        
        # Form fields
        fields = [
            ("Name", "name"),
            ("Rank", "rank", [r.value for r in Rank]),
            ("Unit", "unit"),
            ("Skills", "skills"),
            ("Deployment Status", "status", [s.value for s in DeploymentStatus]),
            ("Health Records", "health"),
            ("Emergency Contact", "contact")
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
                soldier = Soldier(
                    id=str(uuid.uuid4()),
                    name=entries["name"].get(),
                    rank=Rank(entries["rank"].get()),
                    unit=entries["unit"].get(),
                    skills=entries["skills"].get().split(","),
                    deployment_status=DeploymentStatus(entries["status"].get()),
                    health_records={"records": entries["health"].get()},
                    emergency_contact={"contact": entries["contact"].get()}
                )
                
                self.soldiers.append(soldier)
                self.update_table()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        save_button = ctk.CTkButton(dialog, text="Save", command=save)
        save_button.pack(pady=10)
    
    def show_edit_dialog(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a soldier to edit")
            return
        
        item = self.tree.item(selected[0])
        soldier_id = item['values'][0]
        soldier = next((s for s in self.soldiers if s.id == soldier_id), None)
        
        if not soldier:
            messagebox.showerror("Error", "Soldier not found")
            return
        
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Edit Soldier")
        dialog.geometry("500x600")
        
        # Form fields
        fields = [
            ("Name", "name", soldier.name),
            ("Rank", "rank", [r.value for r in Rank], soldier.rank.value),
            ("Unit", "unit", soldier.unit),
            ("Skills", "skills", ",".join(soldier.skills)),
            ("Deployment Status", "status", [s.value for s in DeploymentStatus], soldier.deployment_status.value),
            ("Health Records", "health", str(soldier.health_records)),
            ("Emergency Contact", "contact", str(soldier.emergency_contact))
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
                soldier.name = entries["name"].get()
                soldier.rank = Rank(entries["rank"].get())
                soldier.unit = entries["unit"].get()
                soldier.skills = entries["skills"].get().split(",")
                soldier.deployment_status = DeploymentStatus(entries["status"].get())
                soldier.health_records = {"records": entries["health"].get()}
                soldier.emergency_contact = {"contact": entries["contact"].get()}
                soldier.updated_at = datetime.now()
                
                self.update_table()
                self.show_soldier_details(None)
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        save_button = ctk.CTkButton(dialog, text="Save", command=save)
        save_button.pack(pady=10)
    
    def delete_soldier(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a soldier to delete")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this soldier?"):
            item = self.tree.item(selected[0])
            soldier_id = item['values'][0]
            self.soldiers = [s for s in self.soldiers if s.id != soldier_id]
            self.update_table()
            self.show_soldier_details(None)
    
    def search_soldiers(self):
        search_term = self.search_entry.get().lower()
        filtered = [s for s in self.soldiers 
                   if search_term in s.name.lower() or 
                      search_term in s.unit.lower() or
                      search_term in s.rank.value.lower()]
        self.update_table(filtered)
    
    def show_soldier_details(self, event):
        # Clear existing details
        for widget in self.details_frame.winfo_children():
            widget.destroy()
        
        selected = self.tree.selection()
        if not selected:
            return
        
        item = self.tree.item(selected[0])
        soldier_id = item['values'][0]
        soldier = next((s for s in self.soldiers if s.id == soldier_id), None)
        
        if not soldier:
            return
        
        # Create details view
        details = [
            ("ID", soldier.id),
            ("Name", soldier.name),
            ("Rank", soldier.rank.value),
            ("Unit", soldier.unit),
            ("Skills", ", ".join(soldier.skills)),
            ("Deployment Status", soldier.deployment_status.value),
            ("Health Records", str(soldier.health_records)),
            ("Emergency Contact", str(soldier.emergency_contact)),
            ("Created At", soldier.created_at.strftime("%Y-%m-%d %H:%M:%S")),
            ("Last Updated", soldier.updated_at.strftime("%Y-%m-%d %H:%M:%S"))
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
    
    def update_table(self, soldiers=None):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add new items
        for soldier in (soldiers or self.soldiers):
            self.tree.insert("", "end", values=(
                soldier.id,
                soldier.name,
                soldier.rank.value,
                soldier.unit,
                soldier.deployment_status.value
            )) 
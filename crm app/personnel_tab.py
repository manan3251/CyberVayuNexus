import customtkinter as ctk
from tkinter import ttk, messagebox
from models import Soldier, Rank, DeploymentStatus
import random
from datetime import datetime, timedelta

class PersonnelTab:
    def __init__(self, parent, alert_manager):
        self.parent = parent
        self.alert_manager = alert_manager
        self.soldiers = []
        self.setup_ui()
        self.add_sample_data()
    
    def setup_ui(self):
        # Create main frame
        self.main_frame = ctk.CTkFrame(self.parent)
        self.main_frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Header
        header_frame = ctk.CTkFrame(self.main_frame)
        header_frame.pack(fill="x", pady=5)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="Personnel Management",
            font=("Helvetica", 20, "bold")
        )
        title_label.pack(side="left", padx=10)
        
        # Search frame
        search_frame = ctk.CTkFrame(header_frame)
        search_frame.pack(side="right", padx=10)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search personnel...",
            width=200
        )
        self.search_entry.pack(side="left", padx=5)
        
        search_button = ctk.CTkButton(
            search_frame,
            text="Search",
            command=self.search_personnel,
            width=80
        )
        search_button.pack(side="left", padx=5)
        
        # Content area
        content_frame = ctk.CTkFrame(self.main_frame)
        content_frame.pack(expand=True, fill="both", pady=10)
        
        # Soldier list
        list_frame = ctk.CTkFrame(content_frame)
        list_frame.pack(side="left", expand=True, fill="both", padx=5)
        
        # Create treeview
        self.tree = ttk.Treeview(
            list_frame,
            columns=("ID", "Name", "Rank", "Unit", "Status"),
            show="headings"
        )
        
        # Define headings
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Rank", text="Rank")
        self.tree.heading("Unit", text="Unit")
        self.tree.heading("Status", text="Status")
        
        # Define columns
        self.tree.column("ID", width=50)
        self.tree.column("Name", width=150)
        self.tree.column("Rank", width=100)
        self.tree.column("Unit", width=100)
        self.tree.column("Status", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", expand=True, fill="both")
        scrollbar.pack(side="right", fill="y")
        
        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self.show_soldier_details)
        
        # Action buttons
        button_frame = ctk.CTkFrame(content_frame)
        button_frame.pack(side="right", fill="y", padx=5)
        
        add_button = ctk.CTkButton(
            button_frame,
            text="Add Soldier",
            command=self.show_add_dialog,
            width=150
        )
        add_button.pack(pady=5)
        
        edit_button = ctk.CTkButton(
            button_frame,
            text="Edit Soldier",
            command=self.show_edit_dialog,
            width=150
        )
        edit_button.pack(pady=5)
        
        delete_button = ctk.CTkButton(
            button_frame,
            text="Delete Soldier",
            command=self.delete_soldier,
            width=150
        )
        delete_button.pack(pady=5)
        
        # Details panel
        self.details_frame = ctk.CTkFrame(content_frame)
        self.details_frame.pack(side="right", fill="y", padx=5)
        
        self.details_label = ctk.CTkLabel(
            self.details_frame,
            text="Select a soldier to view details",
            font=("Helvetica", 12)
        )
        self.details_label.pack(pady=10)
    
    def add_sample_data(self):
        first_names = ["John", "James", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
        units = ["Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot", "Golf", "Hotel", "India", "Juliet"]
        skills = ["Combat", "Medical", "Engineering", "Communications", "Intelligence", "Logistics", "Transportation", "Maintenance"]
        
        for i in range(200):
            soldier = Soldier(
                id=f"SOL{i+1:03d}",
                name=f"{random.choice(first_names)} {random.choice(last_names)}",
                rank=random.choice(list(Rank)),
                unit=random.choice(units),
                skills=random.sample(skills, random.randint(1, 3)),
                deployment_status=random.choice(list(DeploymentStatus)),
                health_records={
                    "last_checkup": (datetime.now() - timedelta(days=random.randint(0, 180))).strftime("%Y-%m-%d"),
                    "blood_type": random.choice(["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]),
                    "allergies": random.choice(["None", "Peanuts", "Pollen", "Dust", "Shellfish"])
                },
                emergency_contact={
                    "name": f"Emergency Contact {i+1}",
                    "relationship": random.choice(["Spouse", "Parent", "Sibling", "Child"]),
                    "phone": f"+1-555-{random.randint(1000, 9999)}"
                }
            )
            self.soldiers.append(soldier)
        
        self.update_table()
    
    def show_soldier_details(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return
        
        soldier_id = self.tree.item(selected_item[0])["values"][0]
        soldier = next((s for s in self.soldiers if s.id == soldier_id), None)
        
        if soldier:
            details = f"""
ID: {soldier.id}
Name: {soldier.name}
Rank: {soldier.rank.value}
Unit: {soldier.unit}
Skills: {', '.join(soldier.skills)}
Status: {soldier.deployment_status.value}

Health Records:
- Last Checkup: {soldier.health_records['last_checkup']}
- Blood Type: {soldier.health_records['blood_type']}
- Allergies: {soldier.health_records['allergies']}

Emergency Contact:
- Name: {soldier.emergency_contact['name']}
- Relationship: {soldier.emergency_contact['relationship']}
- Phone: {soldier.emergency_contact['phone']}
"""
            self.details_label.configure(text=details)
    
    def show_add_dialog(self):
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Add Soldier")
        dialog.geometry("400x500")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Form fields
        name_label = ctk.CTkLabel(dialog, text="Name:")
        name_label.pack(pady=5)
        name_entry = ctk.CTkEntry(dialog, width=300)
        name_entry.pack(pady=5)
        
        rank_label = ctk.CTkLabel(dialog, text="Rank:")
        rank_label.pack(pady=5)
        rank_var = ctk.StringVar(value=list(Rank)[0].value)
        rank_menu = ctk.CTkOptionMenu(
            dialog,
            values=[r.value for r in Rank],
            variable=rank_var
        )
        rank_menu.pack(pady=5)
        
        unit_label = ctk.CTkLabel(dialog, text="Unit:")
        unit_label.pack(pady=5)
        unit_entry = ctk.CTkEntry(dialog, width=300)
        unit_entry.pack(pady=5)
        
        def add_soldier():
            try:
                soldier = Soldier(
                    id=f"SOL{len(self.soldiers) + 1:03d}",
                    name=name_entry.get(),
                    rank=Rank(rank_var.get()),
                    unit=unit_entry.get(),
                    skills=[],
                    deployment_status=DeploymentStatus.ACTIVE,
                    health_records={
                        "last_checkup": datetime.now().strftime("%Y-%m-%d"),
                        "blood_type": "Unknown",
                        "allergies": "None"
                    },
                    emergency_contact={
                        "name": "To be added",
                        "relationship": "To be added",
                        "phone": "To be added"
                    }
                )
                self.soldiers.append(soldier)
                self.update_table()
                self.alert_manager.add_alert(
                    "personnel",
                    "info",
                    f"Soldier {soldier.name} has been added to the system.",
                    soldier.id,
                    "soldier"
                )
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        add_button = ctk.CTkButton(
            dialog,
            text="Add",
            command=add_soldier
        )
        add_button.pack(pady=20)
    
    def show_edit_dialog(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a soldier to edit")
            return
        
        soldier_id = self.tree.item(selected_item[0])["values"][0]
        soldier = next((s for s in self.soldiers if s.id == soldier_id), None)
        
        if not soldier:
            messagebox.showerror("Error", "Soldier not found")
            return
        
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Edit Soldier")
        dialog.geometry("400x500")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Form fields
        name_label = ctk.CTkLabel(dialog, text="Name:")
        name_label.pack(pady=5)
        name_entry = ctk.CTkEntry(dialog, width=300)
        name_entry.insert(0, soldier.name)
        name_entry.pack(pady=5)
        
        rank_label = ctk.CTkLabel(dialog, text="Rank:")
        rank_label.pack(pady=5)
        rank_var = ctk.StringVar(value=soldier.rank.value)
        rank_menu = ctk.CTkOptionMenu(
            dialog,
            values=[r.value for r in Rank],
            variable=rank_var
        )
        rank_menu.pack(pady=5)
        
        unit_label = ctk.CTkLabel(dialog, text="Unit:")
        unit_label.pack(pady=5)
        unit_entry = ctk.CTkEntry(dialog, width=300)
        unit_entry.insert(0, soldier.unit)
        unit_entry.pack(pady=5)
        
        def update_soldier():
            try:
                soldier.name = name_entry.get()
                soldier.rank = Rank(rank_var.get())
                soldier.unit = unit_entry.get()
                self.update_table()
                self.alert_manager.add_alert(
                    "personnel",
                    "info",
                    f"Soldier {soldier.name} has been updated.",
                    soldier.id,
                    "soldier"
                )
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        update_button = ctk.CTkButton(
            dialog,
            text="Update",
            command=update_soldier
        )
        update_button.pack(pady=20)
    
    def delete_soldier(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a soldier to delete")
            return
        
        soldier_id = self.tree.item(selected_item[0])["values"][0]
        soldier = next((s for s in self.soldiers if s.id == soldier_id), None)
        
        if not soldier:
            messagebox.showerror("Error", "Soldier not found")
            return
        
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete {soldier.name}?"):
            self.soldiers.remove(soldier)
            self.update_table()
            self.alert_manager.add_alert(
                "personnel",
                "warning",
                f"Soldier {soldier.name} has been removed from the system.",
                soldier.id,
                "soldier"
            )
    
    def search_personnel(self):
        search_term = self.search_entry.get().lower()
        if not search_term:
            self.update_table()
            return
        
        filtered_soldiers = [
            s for s in self.soldiers
            if search_term in s.name.lower() or
               search_term in s.rank.value.lower() or
               search_term in s.unit.lower()
        ]
        
        self.update_table(filtered_soldiers)
    
    def update_table(self, soldiers=None):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add items
        soldiers_to_show = soldiers or self.soldiers
        for soldier in soldiers_to_show:
            self.tree.insert(
                "",
                "end",
                values=(
                    soldier.id,
                    soldier.name,
                    soldier.rank.value,
                    soldier.unit,
                    soldier.deployment_status.value
                )
            ) 
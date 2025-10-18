import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import json
import os

class ArmyManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Army Management System")
        self.root.geometry("1200x700")
        self.root.configure(bg='#f0f0f0')

        # Create data directory if it doesn't exist
        self.data_dir = "data"
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        # Initialize personnel list
        self.personnel = []
        self.load_personnel()

        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create menu bar
        self.create_menu_bar()

        # Create left panel (Personnel List)
        self.create_personnel_list()

        # Create right panel (Personnel Details)
        self.create_personnel_details()

        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

    def create_menu_bar(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Personnel", command=self.new_personnel)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Reports menu
        reports_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Reports", menu=reports_menu)
        reports_menu.add_command(label="Unit Summary", command=self.show_unit_summary)
        reports_menu.add_command(label="Equipment Status", command=self.show_equipment_status)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def create_personnel_list(self):
        # Personnel list frame
        list_frame = ttk.LabelFrame(self.main_frame, text="Personnel", padding="5")
        list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)

        # Search box
        search_frame = ttk.Frame(list_frame)
        search_frame.pack(fill=tk.X, pady=5)
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_personnel)
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Personnel list
        self.personnel_list = ttk.Treeview(list_frame, columns=("id", "name", "rank", "unit"), show="headings")
        self.personnel_list.heading("id", text="ID")
        self.personnel_list.heading("name", text="Name")
        self.personnel_list.heading("rank", text="Rank")
        self.personnel_list.heading("unit", text="Unit")
        self.personnel_list.pack(fill=tk.BOTH, expand=True)
        self.personnel_list.bind("<<TreeviewSelect>>", self.on_personnel_select)

        # Add/Delete buttons
        button_frame = ttk.Frame(list_frame)
        button_frame.pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="Add Personnel", command=self.new_personnel).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete Personnel", command=self.delete_personnel).pack(side=tk.LEFT, padx=5)

    def create_personnel_details(self):
        # Personnel details frame
        details_frame = ttk.LabelFrame(self.main_frame, text="Personnel Details", padding="10")
        details_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)

        # Form fields
        fields = [
            ("ID", "id"),
            ("Name", "name"),
            ("Rank", "rank"),
            ("Unit", "unit"),
            ("Date of Birth", "dob"),
            ("Date of Enlistment", "doe"),
            ("Specialization", "specialization"),
            ("Equipment", "equipment"),
            ("Medical Status", "medical_status"),
            ("Notes", "notes")
        ]

        self.entry_vars = {}
        for i, (label, field) in enumerate(fields):
            ttk.Label(details_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=2)
            if field == "notes":
                var = tk.StringVar()
                entry = tk.Text(details_frame, height=5, width=30)
                self.entry_vars[field] = (var, entry)
                entry.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=2)
            else:
                var = tk.StringVar()
                entry = ttk.Entry(details_frame, textvariable=var)
                self.entry_vars[field] = (var, entry)
                entry.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=2)

        # Save button
        ttk.Button(details_frame, text="Save", command=self.save_personnel).grid(row=len(fields), column=1, sticky=tk.E, pady=10)

    def load_personnel(self):
        try:
            with open(os.path.join(self.data_dir, "personnel.json"), "r") as f:
                self.personnel = json.load(f)
        except FileNotFoundError:
            self.personnel = []

    def save_personnel(self):
        with open(os.path.join(self.data_dir, "personnel.json"), "w") as f:
            json.dump(self.personnel, f)

    def filter_personnel(self, *args):
        search_term = self.search_var.get().lower()
        self.personnel_list.delete(*self.personnel_list.get_children())
        for person in self.personnel:
            if (search_term in person["id"].lower() or 
                search_term in person["name"].lower() or 
                search_term in person["rank"].lower() or 
                search_term in person["unit"].lower()):
                self.personnel_list.insert("", "end", values=(
                    person["id"],
                    person["name"],
                    person["rank"],
                    person["unit"]
                ))

    def new_personnel(self):
        self.personnel_list.selection_clear()
        for var, _ in self.entry_vars.values():
            var.set("")

    def delete_personnel(self):
        selected = self.personnel_list.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a personnel to delete")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this personnel record?"):
            index = self.personnel_list.index(selected[0])
            del self.personnel[index]
            self.save_personnel()
            self.filter_personnel()
            self.new_personnel()

    def on_personnel_select(self, event):
        selected = self.personnel_list.selection()
        if not selected:
            return
        
        index = self.personnel_list.index(selected[0])
        person = self.personnel[index]
        
        for field, (var, _) in self.entry_vars.items():
            var.set(person.get(field, ""))

    def save_personnel(self):
        person = {}
        for field, (var, _) in self.entry_vars.items():
            person[field] = var.get()
        
        if not person["id"] or not person["name"] or not person["rank"] or not person["unit"]:
            messagebox.showwarning("Warning", "ID, Name, Rank, and Unit are required fields")
            return

        selected = self.personnel_list.selection()
        if selected:
            # Update existing personnel
            index = self.personnel_list.index(selected[0])
            self.personnel[index] = person
        else:
            # Add new personnel
            self.personnel.append(person)
        
        self.save_personnel()
        self.filter_personnel()
        messagebox.showinfo("Success", "Personnel record saved successfully")

    def show_unit_summary(self):
        # Count personnel by unit
        unit_counts = {}
        for person in self.personnel:
            unit = person.get("unit", "Unknown")
            unit_counts[unit] = unit_counts.get(unit, 0) + 1

        # Create summary message
        summary = "Unit Summary:\n\n"
        for unit, count in unit_counts.items():
            summary += f"{unit}: {count} personnel\n"

        messagebox.showinfo("Unit Summary", summary)

    def show_equipment_status(self):
        # Count equipment types
        equipment_counts = {}
        for person in self.personnel:
            equipment = person.get("equipment", "None")
            if equipment:
                equipment_counts[equipment] = equipment_counts.get(equipment, 0) + 1

        # Create equipment status message
        status = "Equipment Status:\n\n"
        for equipment, count in equipment_counts.items():
            status += f"{equipment}: {count} assigned\n"

        messagebox.showinfo("Equipment Status", status)

    def show_about(self):
        messagebox.showinfo("About", "Army Management System\nVersion 1.0")

if __name__ == "__main__":
    root = tk.Tk()
    app = ArmyManagementApp(root)
    root.mainloop() 
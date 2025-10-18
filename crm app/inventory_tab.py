import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from models import InventoryItem, Alert
import os
from dotenv import load_dotenv
import uuid
import random

class InventoryTab:
    def __init__(self, parent, alert_manager=None):
        self.parent = parent
        self.alert_manager = alert_manager
        self.inventory = []
        self.setup_ui()
        self.add_sample_data()
    
    def add_sample_data(self):
        categories = {
            "Weapons": [
                "M4 Carbine", "M16 Rifle", "M249 SAW", "M240 Machine Gun",
                "M2 Browning", "M9 Pistol", "M1911 Pistol", "M24 Sniper Rifle"
            ],
            "Ammunition": [
                "5.56mm NATO", "7.62mm NATO", "9mm Parabellum", ".45 ACP",
                ".50 BMG", "40mm Grenade", "12 Gauge Shell", "7.62x39mm"
            ],
            "Protection": [
                "Kevlar Helmet", "Body Armor", "Ballistic Shield", "Gas Mask",
                "Night Vision Goggles", "Tactical Vest", "Combat Boots", "Gloves"
            ],
            "Communication": [
                "Radio Set", "Satellite Phone", "GPS Device", "Signal Flares",
                "Whistle", "Flashlight", "Batteries", "Charging Station"
            ],
            "Medical": [
                "First Aid Kit", "Tourniquet", "Bandages", "Morphine",
                "Antibiotics", "Splint", "IV Kit", "Defibrillator"
            ],
            "Vehicles": [
                "Humvee", "MRAP", "Truck", "ATV",
                "Motorcycle", "Tank", "APC", "Helicopter"
            ]
        }
        
        locations = [
            "Armory A", "Armory B", "Warehouse 1", "Warehouse 2",
            "Field Storage", "Vehicle Depot", "Medical Storage", "HQ Storage"
        ]
        
        for category, items in categories.items():
            for item_name in items:
                quantity = random.randint(10, 1000)
                threshold = int(quantity * 0.2)  # 20% of quantity
                
                item = InventoryItem(
                    id=f"INV{len(self.inventory) + 1:03d}",
                    name=item_name,
                    category=category,
                    quantity=quantity,
                    location=random.choice(locations),
                    threshold=threshold,
                    rfid_tag=f"RFID{random.randint(1000, 9999)}",
                    qr_code=f"QR{random.randint(1000, 9999)}"
                )
                self.inventory.append(item)
        
        self.update_table()
    
    def setup_ui(self):
        # Create main frame
        self.main_frame = ctk.CTkFrame(self.parent)
        self.main_frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Header
        header_frame = ctk.CTkFrame(self.main_frame)
        header_frame.pack(fill="x", pady=5)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="Inventory Management",
            font=("Helvetica", 20, "bold")
        )
        title_label.pack(side="left", padx=10)
        
        # Search frame
        search_frame = ctk.CTkFrame(header_frame)
        search_frame.pack(side="right", padx=10)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search inventory...",
            width=200
        )
        self.search_entry.pack(side="left", padx=5)
        
        search_button = ctk.CTkButton(
            search_frame,
            text="Search",
            command=self.search_inventory,
            width=80
        )
        search_button.pack(side="left", padx=5)
        
        # Content area
        content_frame = ctk.CTkFrame(self.main_frame)
        content_frame.pack(expand=True, fill="both", pady=10)
        
        # Inventory list
        list_frame = ctk.CTkFrame(content_frame)
        list_frame.pack(side="left", expand=True, fill="both", padx=5)
        
        # Create treeview
        self.tree = ttk.Treeview(
            list_frame,
            columns=("ID", "Name", "Category", "Quantity", "Location", "Status"),
            show="headings"
        )
        
        # Define headings
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Quantity", text="Quantity")
        self.tree.heading("Location", text="Location")
        self.tree.heading("Status", text="Status")
        
        # Define columns
        self.tree.column("ID", width=50)
        self.tree.column("Name", width=150)
        self.tree.column("Category", width=100)
        self.tree.column("Quantity", width=80)
        self.tree.column("Location", width=100)
        self.tree.column("Status", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", expand=True, fill="both")
        scrollbar.pack(side="right", fill="y")
        
        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self.show_item_details)
        
        # Action buttons
        button_frame = ctk.CTkFrame(content_frame)
        button_frame.pack(side="right", fill="y", padx=5)
        
        add_button = ctk.CTkButton(
            button_frame,
            text="Add Item",
            command=self.show_add_dialog,
            width=150
        )
        add_button.pack(pady=5)
        
        edit_button = ctk.CTkButton(
            button_frame,
            text="Edit Item",
            command=self.show_edit_dialog,
            width=150
        )
        edit_button.pack(pady=5)
        
        delete_button = ctk.CTkButton(
            button_frame,
            text="Delete Item",
            command=self.delete_item,
            width=150
        )
        delete_button.pack(pady=5)
        
        # Quick actions
        actions_frame = ctk.CTkFrame(button_frame)
        actions_frame.pack(fill="x", pady=10)
        
        check_stock_button = ctk.CTkButton(
            actions_frame,
            text="Check Low Stock",
            command=self.check_low_stock,
            width=150
        )
        check_stock_button.pack(pady=5)
        
        generate_qr_button = ctk.CTkButton(
            actions_frame,
            text="Generate QR Code",
            command=self.generate_qr_code,
            width=150
        )
        generate_qr_button.pack(pady=5)
        
        # Details panel
        self.details_frame = ctk.CTkFrame(content_frame)
        self.details_frame.pack(side="right", fill="y", padx=5)
        
        self.details_label = ctk.CTkLabel(
            self.details_frame,
            text="Select an item to view details",
            font=("Helvetica", 12)
        )
        self.details_label.pack(pady=10)
    
    def show_item_details(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return
        
        item_id = self.tree.item(selected_item[0])["values"][0]
        item = next((i for i in self.inventory if i.id == item_id), None)
        
        if item:
            status = "Low Stock" if item.quantity <= item.threshold else "In Stock"
            status_color = "red" if status == "Low Stock" else "green"
            
            details = f"""
ID: {item.id}
Name: {item.name}
Category: {item.category}
Quantity: {item.quantity}
Threshold: {item.threshold}
Location: {item.location}
Status: {status}

RFID Tag: {item.rfid_tag}
QR Code: {item.qr_code}

Last Updated: {item.updated_at.strftime("%Y-%m-%d %H:%M:%S")}
"""
            self.details_label.configure(text=details)
            
            # Generate alert if stock is low
            if status == "Low Stock":
                self.alert_manager.add_alert(
                    "inventory",
                    "warning",
                    f"Low stock alert: {item.name} has only {item.quantity} units remaining (threshold: {item.threshold})",
                    item.id,
                    "inventory"
                )
    
    def show_add_dialog(self):
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Add Inventory Item")
        dialog.geometry("400x500")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Form fields
        name_label = ctk.CTkLabel(dialog, text="Name:")
        name_label.pack(pady=5)
        name_entry = ctk.CTkEntry(dialog, width=300)
        name_entry.pack(pady=5)
        
        category_label = ctk.CTkLabel(dialog, text="Category:")
        category_label.pack(pady=5)
        category_entry = ctk.CTkEntry(dialog, width=300)
        category_entry.pack(pady=5)
        
        quantity_label = ctk.CTkLabel(dialog, text="Quantity:")
        quantity_label.pack(pady=5)
        quantity_entry = ctk.CTkEntry(dialog, width=300)
        quantity_entry.pack(pady=5)
        
        location_label = ctk.CTkLabel(dialog, text="Location:")
        location_label.pack(pady=5)
        location_entry = ctk.CTkEntry(dialog, width=300)
        location_entry.pack(pady=5)
        
        def add_item():
            try:
                quantity = int(quantity_entry.get())
                threshold = int(quantity * 0.2)  # 20% of quantity
                
                item = InventoryItem(
                    id=f"INV{len(self.inventory) + 1:03d}",
                    name=name_entry.get(),
                    category=category_entry.get(),
                    quantity=quantity,
                    location=location_entry.get(),
                    threshold=threshold,
                    rfid_tag=f"RFID{random.randint(1000, 9999)}",
                    qr_code=f"QR{random.randint(1000, 9999)}"
                )
                self.inventory.append(item)
                self.update_table()
                self.alert_manager.add_alert(
                    "inventory",
                    "info",
                    f"Inventory item {item.name} has been added to the system.",
                    item.id,
                    "inventory"
                )
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        add_button = ctk.CTkButton(
            dialog,
            text="Add",
            command=add_item
        )
        add_button.pack(pady=20)
    
    def show_edit_dialog(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an item to edit")
            return
        
        item_id = self.tree.item(selected_item[0])["values"][0]
        item = next((i for i in self.inventory if i.id == item_id), None)
        
        if not item:
            messagebox.showerror("Error", "Item not found")
            return
        
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Edit Inventory Item")
        dialog.geometry("400x500")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Form fields
        name_label = ctk.CTkLabel(dialog, text="Name:")
        name_label.pack(pady=5)
        name_entry = ctk.CTkEntry(dialog, width=300)
        name_entry.insert(0, item.name)
        name_entry.pack(pady=5)
        
        category_label = ctk.CTkLabel(dialog, text="Category:")
        category_label.pack(pady=5)
        category_entry = ctk.CTkEntry(dialog, width=300)
        category_entry.insert(0, item.category)
        category_entry.pack(pady=5)
        
        quantity_label = ctk.CTkLabel(dialog, text="Quantity:")
        quantity_label.pack(pady=5)
        quantity_entry = ctk.CTkEntry(dialog, width=300)
        quantity_entry.insert(0, str(item.quantity))
        quantity_entry.pack(pady=5)
        
        location_label = ctk.CTkLabel(dialog, text="Location:")
        location_label.pack(pady=5)
        location_entry = ctk.CTkEntry(dialog, width=300)
        location_entry.insert(0, item.location)
        location_entry.pack(pady=5)
        
        def update_item():
            try:
                quantity = int(quantity_entry.get())
                threshold = int(quantity * 0.2)  # 20% of quantity
                
                item.name = name_entry.get()
                item.category = category_entry.get()
                item.quantity = quantity
                item.location = location_entry.get()
                item.threshold = threshold
                item.updated_at = datetime.now()
                
                self.update_table()
                self.alert_manager.add_alert(
                    "inventory",
                    "info",
                    f"Inventory item {item.name} has been updated.",
                    item.id,
                    "inventory"
                )
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        update_button = ctk.CTkButton(
            dialog,
            text="Update",
            command=update_item
        )
        update_button.pack(pady=20)
    
    def delete_item(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an item to delete")
            return
        
        item_id = self.tree.item(selected_item[0])["values"][0]
        item = next((i for i in self.inventory if i.id == item_id), None)
        
        if not item:
            messagebox.showerror("Error", "Item not found")
            return
        
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete {item.name}?"):
            self.inventory.remove(item)
            self.update_table()
            self.alert_manager.add_alert(
                "inventory",
                "warning",
                f"Inventory item {item.name} has been removed from the system.",
                item.id,
                "inventory"
            )
    
    def search_inventory(self):
        search_term = self.search_entry.get().lower()
        if not search_term:
            self.update_table()
            return
        
        filtered_items = [
            i for i in self.inventory
            if search_term in i.name.lower() or
               search_term in i.category.lower() or
               search_term in i.location.lower()
        ]
        
        self.update_table(filtered_items)
    
    def check_low_stock(self):
        low_stock_items = [i for i in self.inventory if i.quantity <= i.threshold]
        
        if low_stock_items:
            message = "\n".join([f"- {item.name} ({item.quantity} remaining, threshold: {item.threshold})" for item in low_stock_items])
            self.alert_manager.add_alert(
                "inventory",
                "warning",
                f"Low stock alert for the following items:\n{message}",
                None,
                "inventory"
            )
            messagebox.showwarning("Low Stock Alert", f"The following items are low on stock:\n{message}")
        else:
            messagebox.showinfo("Stock Check", "All items are above threshold levels.")
    
    def generate_qr_code(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an item to generate QR code")
            return
        
        item_id = self.tree.item(selected_item[0])["values"][0]
        item = next((i for i in self.inventory if i.id == item_id), None)
        
        if item:
            self.alert_manager.add_alert(
                "inventory",
                "info",
                f"QR code generated for {item.name}",
                item.id,
                "inventory"
            )
            messagebox.showinfo("QR Code", f"QR code generated for {item.name}: {item.qr_code}")
    
    def update_table(self, items=None):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add items
        items_to_show = items or self.inventory
        for item in items_to_show:
            status = "Low Stock" if item.quantity <= item.threshold else "In Stock"
            status_color = "red" if status == "Low Stock" else "green"
            
            self.tree.insert(
                "",
                "end",
                values=(
                    item.id,
                    item.name,
                    item.category,
                    item.quantity,
                    item.location,
                    status
                ),
                tags=(status_color,)
            )
        
        # Configure tag colors
        self.tree.tag_configure("red", foreground="red")
        self.tree.tag_configure("green", foreground="green") 
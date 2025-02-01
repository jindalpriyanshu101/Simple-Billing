import customtkinter as ctk
import sqlite3
from fpdf import FPDF
from tkinter import messagebox, ttk
from tkinter import simpledialog
from PIL import Image
from datetime import datetime
import random
import customtkinter as ctk
from PIL import Image, ImageDraw

# Database setup
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Create tables for inventory, users, and payment logs
cursor.execute('''CREATE TABLE IF NOT EXISTS inventory (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    product_mrp REAL NOT NULL,
    product_stock INTEGER NOT NULL
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS payment_logs (
    phone_number TEXT PRIMARY KEY,
    date TEXT NOT NULL,
    credit REAL NOT NULL,
    debit REAL NOT NULL,
    purchased_items TEXT NOT NULL,
    customer_details TEXT NOT NULL
)''')
conn.commit()
class SimpleBillingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DFC Fast Food")
        self.root.geometry("1100x700")
        self.root.configure(bg="#1a1a1a")  # Dark background for contrast

        ctk.set_appearance_mode("Dark")  # Ensuring a modern dark mode
        ctk.set_default_color_theme("blue")

        self.logged_in_user = None
        self.create_login_screen()


    def create_login_screen(self):
        """Create the ultimate login screen with perfect alignment & modern aesthetics."""
        self.clear_screen()

        # 🟢 Glassmorphic Login Card (Spaced & Well-Designed)
        login_frame = ctk.CTkFrame(
            self.root, corner_radius=30, fg_color="#2C2F33",  
            border_width=2, border_color="#7289DA",  
            width=1000, height=600
        )
        login_frame.pack(expand=True, pady=30)

        # 🟢 Centered Circular Logo with Border
        logo_image = Image.open("logo.png").resize((120, 120))  # Resize logo
        logo_image = logo_image.convert("RGBA")

        # Create a circular mask
        mask = Image.new("L", (120, 120), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, 120, 120), fill=255)  # Make it circular

        # Apply mask to the logo to make it circular
        circular_logo = Image.new("RGBA", (120, 120), (0, 0, 0, 0))
        circular_logo.paste(logo_image, (0, 0), mask)

        # Create border effect
        border_size = 5
        border_color = "#7289DA"
        border = Image.new("RGBA", (120 + border_size * 2, 120 + border_size * 2), (0, 0, 0, 0))
        border_draw = ImageDraw.Draw(border)
        border_draw.ellipse((0, 0, 120 + border_size * 2, 120 + border_size * 2), fill=border_color)  # Outer border
        border.paste(circular_logo, (border_size, border_size), circular_logo)

        # Convert image to CTkImage
        logo = ctk.CTkImage(dark_image=border, size=(130, 130))  # Slightly larger to fit border

        # 🟢 Circular Frame for Logo
        logo_frame = ctk.CTkFrame(login_frame, width=140, height=140, corner_radius=70, fg_color="#2C2F33")
        logo_frame.pack(pady=20)

        logo_label = ctk.CTkLabel(logo_frame, image=logo, text="")
        logo_label.pack(expand=True)

        # 🟢 Business Name & Owner (Centered & Best Font)
        ctk.CTkLabel(login_frame, text="DFC Fast Food", font=("Inter", 26, "bold"), text_color="#ffffff").pack(pady=(5, 0))
        ctk.CTkLabel(login_frame, text="Owner: Hasnain Mallah", font=("Inter", 16), text_color="#b0b0b0").pack(pady=(0, 15))

        # 🟢 Username Input (Properly Spaced)
        ctk.CTkLabel(login_frame, text="Username", font=("Poppins", 16), text_color="#ffffff").pack(anchor="w", padx=50, pady=(10, 5))
        self.username_entry = ctk.CTkEntry(
            login_frame, width=600, height=50, corner_radius=15,
            fg_color="#3B3F45", text_color="#ffffff"
        )
        self.username_entry.pack(pady=(0, 10))

        # 🟢 Password Input (Properly Spaced & Styled)
        ctk.CTkLabel(login_frame, text="Password", font=("Poppins", 16), text_color="#ffffff").pack(anchor="w", padx=10, pady=(10, 5))

        # Create a frame to hold the password entry & eye icon
        password_frame = ctk.CTkFrame(login_frame, fg_color="#3B3F45", corner_radius=15)
        password_frame.pack(pady=(0, 15))

        # Password Entry Field
        self.password_entry = ctk.CTkEntry(
            password_frame, width=500, height=50, corner_radius=15, show="*",
            fg_color="transparent", text_color="#ffffff", border_width=0  # Transparent to blend inside the frame
        )
        self.password_entry.pack(side="left", padx=(10, 5))

        # 🟢 Eye Icon Inside Input Box
        self.show_password = False
        def toggle_password():
            self.show_password = not self.show_password
            self.password_entry.configure(show="" if self.show_password else "*")

        eye_icon = ctk.CTkButton(
            password_frame, text="👁", font=("Poppins", 14), width=40, height=40,
            fg_color="transparent", hover_color="#5B6EAE",
            corner_radius=25, command=toggle_password
        )
        eye_icon.pack(side="right", padx=5)  # Inside the input box


        # 🟢 Animated Login Button (Best Look)
        login_btn = ctk.CTkButton(
            login_frame, text="Login", font=("Inter", 18, "bold"), text_color="#ffffff",
            fg_color="#7289DA", hover_color="#5B6EAE", corner_radius=25,
            width=400, height=50, command=self.login
        )
        login_btn.pack(pady=30)


    def clear_screen(self):
        """Clear the root window before loading a new screen."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def login(self):
        """Handle user login."""
        username = self.username_entry.get()
        password = self.password_entry.get()

        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()

        if user:
            self.logged_in_user = user
            if user[3] == 'admin':
                self.create_admin_screen()
            else:
                self.create_employee_screen()
        else:
            messagebox.showerror("Error", "Invalid username or password.")

    def create_admin_screen(self):
        """Create the admin dashboard."""
        self.clear_screen()

        admin_frame = ctk.CTkFrame(self.root)
        admin_frame.pack(expand=True)

        ctk.CTkButton(admin_frame, text="Manage Inventory", command=self.manage_inventory).pack(pady=10)
        ctk.CTkButton(admin_frame, text="View Payment Logs", command=self.view_payment_logs).pack(pady=10)
        ctk.CTkButton(admin_frame, text="Logout", command=self.logout).pack(pady=10)

    def create_employee_screen(self):
        """Create the employee billing screen."""
        self.clear_screen()

        employee_frame = ctk.CTkFrame(self.root)
        employee_frame.pack(expand=True, fill="both")

        ctk.CTkLabel(employee_frame, text="Customer Name:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.customer_name_entry = ctk.CTkEntry(employee_frame)
        self.customer_name_entry.grid(row=0, column=1, padx=10, pady=5)

        ctk.CTkLabel(employee_frame, text="Customer Phone:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.customer_phone_entry = ctk.CTkEntry(employee_frame)
        self.customer_phone_entry.grid(row=1, column=1, padx=10, pady=5)

        # Inventory Treeview
        self.inventory_frame = ctk.CTkScrollableFrame(employee_frame, fg_color="black")
        self.inventory_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky="nsew")
        self.inventory_table = self.create_treeview(self.inventory_frame, ["ID", "Name", "Price", "Stock"])
        self.populate_inventory()

        # Add to Bill Button
        ctk.CTkButton(employee_frame, text="Add to Bill", command=self.add_to_bill).grid(row=3, column=0, columnspan=2, pady=10)

        # Billing Treeview
        self.bill_frame = ctk.CTkScrollableFrame(employee_frame)
        self.bill_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky="nsew")
        self.bill_table = self.create_treeview(self.bill_frame, ["ID", "Name", "Quantity", "Price", "Total"])

        # Finalize Bill Button
        ctk.CTkButton(employee_frame, text="Finalize Bill", command=self.finalize_bill).grid(row=5, column=0, columnspan=2, pady=10)

        employee_frame.rowconfigure(2, weight=1)
        employee_frame.rowconfigure(4, weight=1)
        employee_frame.columnconfigure(1, weight=1)

    def create_treeview(self, parent, columns):
        """Create a Treeview with specified columns."""
        tree = ttk.Treeview(parent, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center")
        tree.pack(fill="both", expand=True)
        return tree

    def populate_inventory(self):
        """Fetch and display inventory items."""
        for item in self.inventory_table.get_children():
            self.inventory_table.delete(item)

        cursor.execute("SELECT * FROM inventory")
        for product in cursor.fetchall():
            self.inventory_table.insert("", "end", values=product)

    def finalize_bill(self):
        """Finalize and save the bill as a PDF."""
        if not self.bill_table.get_children():
            messagebox.showerror("Error", "No items in the bill.")
            return

        total_amount = 0
        order_number = random.randint(1000, 9999)
        date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        purchased_items = []

        customer_name = self.customer_name_entry.get()
        customer_phone = self.customer_phone_entry.get()

        if not customer_name or not customer_phone:
            messagebox.showerror("Error", "Please fill in customer details.")
            return

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Add logo
        pdf.image("logo.png", x=10, y=8, w=33)
        pdf.cell(200, 10, txt="DFC Fast Food Invoice", ln=True, align='C')
        pdf.cell(200, 10, txt=f"Order Number: {order_number}", ln=True)
        pdf.cell(200, 10, txt=f"Date & Time: {date_time}", ln=True)
        pdf.cell(200, 10, txt=f"Customer Name: {customer_name}", ln=True)
        pdf.cell(200, 10, txt=f"Phone: {customer_phone}", ln=True)
        pdf.cell(200, 10, txt="", ln=True)  # Empty line

        pdf.cell(50, 10, txt="Product", border=1)
        pdf.cell(30, 10, txt="Quantity", border=1)
        pdf.cell(30, 10, txt="Price", border=1)
        pdf.cell(30, 10, txt="Total", border=1, ln=True)

        for item in self.bill_table.get_children():
            product = self.bill_table.item(item, "values")
            product_id, product_name, quantity, price, total = product
            purchased_items.append(product_name)
            total_amount += float(total)

            pdf.cell(50, 10, txt=str(product_name), border=1)
            pdf.cell(30, 10, txt=str(quantity), border=1)
            pdf.cell(30, 10, txt=f"{price}", border=1)
            pdf.cell(30, 10, txt=f"{total}", border=1, ln=True)

        pdf.cell(200, 10, txt="", ln=True)  # Empty line
        pdf.cell(200, 10, txt=f"Total Amount: INR {total_amount}", ln=True)

        pdf.output("invoice.pdf")
        messagebox.showinfo("Success", "Invoice generated as invoice.pdf")

        # Handle payment
        amount_paid = float(simpledialog.askstring("Payment", "Enter amount paid:") or 0)
        debit = total_amount - amount_paid

        cursor.execute("INSERT OR REPLACE INTO payment_logs (phone_number, date, credit, debit, purchased_items, customer_details) VALUES (?, ?, ?, ?, ?, ?)",
                       (customer_phone, date_time, amount_paid, debit, ", ".join(purchased_items), customer_name))
        conn.commit()

        for item in self.bill_table.get_children():
            self.bill_table.delete(item)

    def manage_inventory(self):
        """Admin functionality to manage inventory."""
        self.clear_screen()

        admin_frame = ctk.CTkFrame(self.root)
        admin_frame.pack(expand=True, fill="both")

        self.inventory_table = self.create_treeview(admin_frame, ["ID", "Name", "Price", "Stock"])
        self.populate_inventory()

        ctk.CTkButton(admin_frame, text="Add Product", command=self.add_product_with_pass).pack(pady=5)
        ctk.CTkButton(admin_frame, text="Update Product", command=self.update_product_with_pass).pack(pady=5)
        ctk.CTkButton(admin_frame, text="Delete Product", command=self.delete_product_with_pass).pack(pady=5)
        ctk.CTkButton(admin_frame, text="Back", command=self.create_admin_screen).pack(pady=5)

    def add_product_with_pass(self):
        """Add a new product to the inventory with password protection."""
        password = simpledialog.askstring("Password Required", "Enter admin password:", show="*")
        if password != "adminpass":
            messagebox.showerror("Error", "Incorrect password.")
            return

        self.add_product()

    def update_product_with_pass(self):
        """
        Update a product in the inventory with password protection.
        """
        password = simpledialog.askstring("Password Required", "Enter admin password:", show="*")
        if password != "adminpass":
            messagebox.showerror("Error", "Incorrect password.")
            return

        self.update_product()

    def delete_product_with_pass(self):
        """Delete a product from the inventory with password protection."""
        password = simpledialog.askstring("Password Required", "Enter admin password:", show="*")
        if password != "adminpass":
            messagebox.showerror("Error", "Incorrect password.")
            return

        self.delete_product()

    def add_product(self):
        """Add a new product to the inventory."""
        add_window = ctk.CTkToplevel(self.root)
        add_window.title("Add Product")

        ctk.CTkLabel(add_window, text="Product Name:").pack(pady=5)
        name_entry = ctk.CTkEntry(add_window)
        name_entry.pack(pady=5)

        ctk.CTkLabel(add_window, text="Price:").pack(pady=5)
        price_entry = ctk.CTkEntry(add_window)
        price_entry.pack(pady=5)

        ctk.CTkLabel(add_window, text="Stock:").pack(pady=5)
        stock_entry = ctk.CTkEntry(add_window)
        stock_entry.pack(pady=5)

        def save_product():
            name = name_entry.get()
            price = price_entry.get()
            stock = stock_entry.get()

            if not name or not price or not stock:
                messagebox.showerror("Error", "All fields are required.")
                return

            try:
                cursor.execute("INSERT INTO inventory (product_name, product_mrp, product_stock) VALUES (?, ?, ?)", (name, float(price), int(stock)))
                conn.commit()
                messagebox.showinfo("Success", "Product added successfully.")
                add_window.destroy()
                self.populate_inventory()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ctk.CTkButton(add_window, text="Save", command=save_product).pack(pady=10)

    def update_product(self):
        """Update an existing product in the inventory."""
        selected_item = self.inventory_table.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a product to update.")
            return

        product = self.inventory_table.item(selected_item, "values")
        product_id, product_name, product_price, product_stock = product

        update_window = ctk.CTkToplevel(self.root)
        update_window.title("Update Product")

        ctk.CTkLabel(update_window, text="Product Name:").pack(pady=5)
        name_entry = ctk.CTkEntry(update_window)
        name_entry.insert(0, product_name)
        name_entry.pack(pady=5)

        ctk.CTkLabel(update_window, text="Price:").pack(pady=5)
        price_entry = ctk.CTkEntry(update_window)
        price_entry.insert(0, product_price)
        price_entry.pack(pady=5)

        ctk.CTkLabel(update_window, text="Stock:").pack(pady=5)
        stock_entry = ctk.CTkEntry(update_window)
        stock_entry.insert(0, product_stock)
        stock_entry.pack(pady=5)

        def save_changes():
            name = name_entry.get()
            price = price_entry.get()
            stock = stock_entry.get()

            if not name or not price or not stock:
                messagebox.showerror("Error", "All fields are required.")
                return

            try:
                cursor.execute("UPDATE inventory SET product_name = ?, product_mrp = ?, product_stock = ? WHERE product_id = ?", (name, float(price), int(stock), product_id))
                conn.commit()
                messagebox.showinfo("Success", "Product updated successfully.")
                update_window.destroy()
                self.populate_inventory()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ctk.CTkButton(update_window, text="Save Changes", command=save_changes).pack(pady=10)

    def delete_product(self):
        """Delete a product from the inventory."""
        selected_item = self.inventory_table.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a product to delete.")
            return

        product = self.inventory_table.item(selected_item, "values")
        product_id = product[0]

        sure = messagebox.askyesno("Confirm", "Are you sure you want to delete this product?")
        if sure:
            try:
                cursor.execute("DELETE FROM inventory WHERE product_id = ?", (product_id,))
                conn.commit()
                self.populate_inventory()
                messagebox.showinfo("Success", "Product deleted successfully.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def view_payment_logs(self):
        """View payment logs for admin users."""
        self.clear_screen()

        logs_frame = ctk.CTkFrame(self.root)
        logs_frame.pack(expand=True, fill="both")

        logs_table = self.create_treeview(logs_frame, ["Phone", "Date", "Credit", "Debit", "Items", "Customer"])

        cursor.execute("SELECT * FROM payment_logs")
        for log in cursor.fetchall():
            logs_table.insert("", "end", values=log)

        ctk.CTkButton(logs_frame, text="Back", command=self.create_admin_screen).pack(pady=10)

    def logout(self):
        """Logout the current user."""
        self.logged_in_user = None
        self.create_login_screen()

    def clear_screen(self):
        """Clear all widgets from the main window."""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def add_to_bill(self):
        """Add selected product to the bill."""
        selected_item = self.inventory_table.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a product to add to the bill.")
            return

        product = self.inventory_table.item(selected_item, "values")
        product_id, product_name, price, stock = int(product[0]), product[1], float(product[2]), int(product[3])

        if stock <= 0:
            messagebox.showerror("Error", f"{product_name} is out of stock.")
            return

        # Default quantity is 1
        quantity = 1
        total = round(price * quantity, 2)

        # Check if the product is already in the bill
        for bill_item in self.bill_table.get_children():
            bill_product = self.bill_table.item(bill_item, "values")
            if int(bill_product[0]) == product_id:
                quantity = int(bill_product[2]) + 1
                if quantity > stock:
                    messagebox.showerror("Error", f"Not enough stock for {product_name}.")
                    return

                total = round(price * quantity, 2)
                self.bill_table.item(bill_item, values=(product_id, product_name, quantity, price, total))
                self.update_stock(product_id, stock - 1)
                return

        # Add new product to the bill
        self.bill_table.insert("", "end", values=(product_id, product_name, quantity, price, total))
        self.update_stock(product_id, stock - 1)

    def update_stock(self, product_id, new_stock):
        """Update the stock of a product in the inventory."""
        cursor.execute("UPDATE inventory SET product_stock = ? WHERE product_id = ?", (new_stock, product_id))
        conn.commit()
        self.populate_inventory()

if __name__ == "__main__":
    root = ctk.CTk()
    app = SimpleBillingApp(root)
    root.mainloop()

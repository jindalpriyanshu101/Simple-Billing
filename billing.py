import customtkinter as ctk
import sqlite3
from fpdf import FPDF
from tkinter import messagebox, ttk

# Database setup
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Create tables for inventory and users
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
conn.commit()

class SimpleBillingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Billing App")
        self.root.geometry("800x600")

        ctk.set_appearance_mode("System")  # Light or Dark mode based on system settings
        ctk.set_default_color_theme("blue")

        self.logged_in_user = None
        self.create_login_screen()

    def create_login_screen(self):
        self.clear_screen()

        ctk.CTkLabel(self.root, text="Username:").pack(pady=5)
        self.username_entry = ctk.CTkEntry(self.root)
        self.username_entry.pack(pady=5)

        ctk.CTkLabel(self.root, text="Password:").pack(pady=5)
        self.password_entry = ctk.CTkEntry(self.root, show="*")
        self.password_entry.pack(pady=5)

        ctk.CTkButton(self.root, text="Login", command=self.login).pack(pady=10)

    def login(self):
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
        self.clear_screen()

        ctk.CTkButton(self.root, text="Manage Inventory", command=self.manage_inventory).pack(pady=10)
        ctk.CTkButton(self.root, text="Logout", command=self.logout).pack(pady=10)

    def create_employee_screen(self):
        self.clear_screen()

        ctk.CTkLabel(self.root, text="Customer Name:").pack(pady=5)
        self.customer_name_entry = ctk.CTkEntry(self.root)
        self.customer_name_entry.pack(pady=5)

        ctk.CTkLabel(self.root, text="Customer Phone:").pack(pady=5)
        self.customer_phone_entry = ctk.CTkEntry(self.root)
        self.customer_phone_entry.pack(pady=5)

        ctk.CTkLabel(self.root, text="Customer Email:").pack(pady=5)
        self.customer_email_entry = ctk.CTkEntry(self.root)
        self.customer_email_entry.pack(pady=5)

        # Inventory Treeview
        self.inventory_frame = ctk.CTkFrame(self.root)
        self.inventory_frame.pack(pady=10, fill="both", expand=True)
        self.inventory_table = self.create_treeview(self.inventory_frame, ["ID", "Name", "Price", "Stock"])
        self.populate_inventory()

        # Add to Bill Button
        ctk.CTkButton(self.root, text="Add to Bill", command=self.add_to_bill).pack(pady=10)

        # Billing Treeview
        self.bill_frame = ctk.CTkFrame(self.root)
        self.bill_frame.pack(pady=10, fill="both", expand=True)
        self.bill_table = self.create_treeview(self.bill_frame, ["ID", "Name", "Quantity", "Price", "Tax", "Total"])

        # Finalize Bill Button
        ctk.CTkButton(self.root, text="Finalize Bill", command=self.finalize_bill).pack(pady=10)

    def create_treeview(self, parent, columns):
        tree = ttk.Treeview(parent, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center")
        tree.pack(fill="both", expand=True)
        return tree

    def populate_inventory(self):
        for item in self.inventory_table.get_children():
            self.inventory_table.delete(item)

        cursor.execute("SELECT * FROM inventory")
        for product in cursor.fetchall():
            self.inventory_table.insert("", "end", values=product)

    def add_to_bill(self):
        selected_item = self.inventory_table.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a product to add to the bill.")
            return

        product = self.inventory_table.item(selected_item, "values")
        product_id, product_name, price, stock = int(product[0]), product[1], float(product[2]), int(product[3])

        if stock <= 0:
            messagebox.showerror("Error", f"{product_name} is out of stock.")
            return

        # Get quantity and calculate tax and total
        quantity = 1  # Default quantity
        tax = round(0.18 * price, 2)  # 18% GST
        total = round((price + tax) * quantity, 2)

        for bill_item in self.bill_table.get_children():
            bill_product = self.bill_table.item(bill_item, "values")
            if int(bill_product[0]) == product_id:
                quantity = int(bill_product[2]) + 1
                if quantity > stock:
                    messagebox.showerror("Error", f"Not enough stock for {product_name}.")
                    return

                total = round((price + tax) * quantity, 2)
                self.bill_table.item(bill_item, values=(product_id, product_name, quantity, price, tax, total))
                self.update_stock(product_id, stock - 1)
                return

        self.bill_table.insert("", "end", values=(product_id, product_name, quantity, price, tax, total))
        self.update_stock(product_id, stock - 1)

    def update_stock(self, product_id, new_stock):
        cursor.execute("UPDATE inventory SET product_stock = ? WHERE product_id = ?", (new_stock, product_id))
        conn.commit()
        self.populate_inventory()

    def finalize_bill(self):
        if not self.bill_table.get_children():
            messagebox.showerror("Error", "No items in the bill.")
            return

        total_amount = 0
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        customer_name = self.customer_name_entry.get()
        customer_phone = self.customer_phone_entry.get()
        customer_email = self.customer_email_entry.get()

        if not customer_name or not customer_phone or not customer_email:
            messagebox.showerror("Error", "Please fill in customer details.")
            return

        pdf.cell(200, 10, txt="Invoice", ln=True, align='C')
        pdf.cell(200, 10, txt=f"Customer Name: {customer_name}", ln=True)
        pdf.cell(200, 10, txt=f"Phone: {customer_phone}", ln=True)
        pdf.cell(200, 10, txt=f"Email: {customer_email}", ln=True)
        pdf.cell(200, 10, txt="", ln=True)  # Empty line

        pdf.cell(50, 10, txt="Product", border=1)
        pdf.cell(30, 10, txt="Quantity", border=1)
        pdf.cell(30, 10, txt="Price", border=1)
        pdf.cell(30, 10, txt="Tax", border=1)
        pdf.cell(30, 10, txt="Total", border=1, ln=True)

        for item in self.bill_table.get_children():
            product = self.bill_table.item(item, "values")
            product_id, product_name, quantity, price, tax, total = product
            total_amount += float(total)

            pdf.cell(50, 10, txt=str(product_name), border=1)
            pdf.cell(30, 10, txt=str(quantity), border=1)
            pdf.cell(30, 10, txt=f"{price}", border=1)
            pdf.cell(30, 10, txt=f"{tax}", border=1)
            pdf.cell(30, 10, txt=f"{total}", border=1, ln=True)

        pdf.cell(200, 10, txt="", ln=True)  # Empty line
        pdf.cell(200, 10, txt=f"Total Amount: INR {total_amount}", ln=True)

        pdf.output("invoice.pdf")
        messagebox.showinfo("Success", "Invoice generated as invoice.pdf")

        for item in self.bill_table.get_children():
            self.bill_table.delete(item)

    def manage_inventory(self):
        self.clear_screen()

        self.inventory_frame = ctk.CTkFrame(self.root)
        self.inventory_frame.pack(pady=10, fill="both", expand=True)
        self.inventory_table = self.create_treeview(self.inventory_frame, ["ID", "Name", "Price", "Stock"])
        self.populate_inventory()

        ctk.CTkButton(self.root, text="Add Product", command=self.add_product).pack(pady=5)
        ctk.CTkButton(self.root, text="Update Product", command=self.update_product).pack(pady=5)
        ctk.CTkButton(self.root, text="Delete Product", command=self.delete_product).pack(pady=5)
        ctk.CTkButton(self.root, text="Back", command=self.create_admin_screen).pack(pady=5)

    def add_product(self):
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
        selected_item = self.inventory_table.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a product to delete.")
            return

        product = self.inventory_table.item(selected_item, "values")
        product_id = product[0]

        sure = messagebox.askyesno("Confirm", "Are you sure you want to delete this product?")
        if sure:
            cursor.execute("DELETE FROM inventory WHERE product_id = ?", (product_id,))
            conn.commit()
            self.populate_inventory()

    def logout(self):
        self.logged_in_user = None
        self.create_login_screen()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = ctk.CTk()
    app = SimpleBillingApp(root)
    root.mainloop()

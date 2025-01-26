import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from fpdf import FPDF

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

# cursor.executemany('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', [
#     ('admin', 'admin123', 'admin'),
#     ('employee', 'emp123', 'employee')
# ])

conn.commit()

class SimpleBillingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Billing App")
        self.root.geometry("800x600")
        
        self.logged_in_user = None
        self.create_login_screen()

    def create_login_screen(self):
        self.clear_screen()

        tk.Label(self.root, text="Username:").pack(pady=5)
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack(pady=5)

        tk.Label(self.root, text="Password:").pack(pady=5)
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack(pady=5)

        tk.Button(self.root, text="Login", command=self.login).pack(pady=10)

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

        tk.Button(self.root, text="Manage Inventory", command=self.manage_inventory).pack(pady=10)
        tk.Button(self.root, text="Logout", command=self.logout).pack(pady=10)

    def create_employee_screen(self):
        self.clear_screen()

        tk.Label(self.root, text="Customer Name:").pack(pady=5)
        self.customer_name_entry = tk.Entry(self.root)
        self.customer_name_entry.pack(pady=5)

        tk.Label(self.root, text="Customer Phone:").pack(pady=5)
        self.customer_phone_entry = tk.Entry(self.root)
        self.customer_phone_entry.pack(pady=5)

        tk.Label(self.root, text="Customer Email:").pack(pady=5)
        self.customer_email_entry = tk.Entry(self.root)
        self.customer_email_entry.pack(pady=5)

        # Inventory Treeview
        self.inventory_tree = ttk.Treeview(self.root, columns=("ID", "Name", "Price", "Stock"), show="headings")
        self.inventory_tree.heading("ID", text="ID")
        self.inventory_tree.heading("Name", text="Product Name")
        self.inventory_tree.heading("Price", text="Price")
        self.inventory_tree.heading("Stock", text="Stock")
        self.inventory_tree.pack(pady=10, fill=tk.BOTH, expand=True)
        self.populate_inventory()

        # Add to Bill Button
        tk.Button(self.root, text="Add to Bill", command=self.add_to_bill).pack(pady=10)

        # Billing Treeview
        self.bill_tree = ttk.Treeview(self.root, columns=("ID", "Name", "Quantity", "Price", "Tax", "Total"), show="headings")
        self.bill_tree.heading("ID", text="ID")
        self.bill_tree.heading("Name", text="Product Name")
        self.bill_tree.heading("Quantity", text="Quantity")
        self.bill_tree.heading("Price", text="Price")
        self.bill_tree.heading("Tax", text="Tax")
        self.bill_tree.heading("Total", text="Total")
        self.bill_tree.pack(pady=10, fill=tk.BOTH, expand=True)

        # Finalize Bill Button
        tk.Button(self.root, text="Finalize Bill", command=self.finalize_bill).pack(pady=10)

    def populate_inventory(self):
        # Clear existing items in the inventory treeview
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)

        cursor.execute("SELECT * FROM inventory")
        for product in cursor.fetchall():
            self.inventory_tree.insert("", "end", values=product)

    def add_to_bill(self):
        selected_item = self.inventory_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a product to add to the bill.")
            return

        product = self.inventory_tree.item(selected_item, "values")
        product_id, product_name, price, stock = int(product[0]), product[1], float(product[2]), int(product[3])

        if stock <= 0:
            messagebox.showerror("Error", f"{product_name} is out of stock.")
            return

        # Get quantity and calculate tax and total
        quantity = 1  # Default quantity, can be made adjustable
        tax = round(0.18 * price, 2)  # 18% GST
        total = round((price + tax) * quantity, 2)

        # Check if the product is already in the bill
        for bill_item in self.bill_tree.get_children():
            bill_product = self.bill_tree.item(bill_item, "values")
            if int(bill_product[0]) == product_id:
                quantity = int(bill_product[2]) + 1
                if quantity > stock:
                    messagebox.showerror("Error", f"Not enough stock for {product_name}.")
                    return

                total = round((price + tax) * quantity, 2)
                self.bill_tree.item(bill_item, values=(product_id, product_name, quantity, price, tax, total))
                self.update_stock(product_id, stock - 1)
                return

        # Add new product to the bill
        self.bill_tree.insert("", "end", values=(product_id, product_name, quantity, price, tax, total))
        self.update_stock(product_id, stock - 1)

    def update_stock(self, product_id, new_stock):
        cursor.execute("UPDATE inventory SET product_stock = ? WHERE product_id = ?", (new_stock, product_id))
        conn.commit()
        self.populate_inventory()

    def finalize_bill(self):
        if not self.bill_tree.get_children():
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

        for item in self.bill_tree.get_children():
            product = self.bill_tree.item(item, "values")
            product_id, product_name, quantity, price, tax, total = product
            total_amount += float(total)

            pdf.cell(50, 10, txt=str(product_name), border=1)
            pdf.cell(30, 10, txt=str(quantity), border=1)
            pdf.cell(30, 10, txt=f"{price}", border=1)
            pdf.cell(30, 10, txt=f"{tax}", border=1)
            pdf.cell(30, 10, txt=f"{total}", border=1, ln=True)

        pdf.cell(200, 10, txt="", ln=True)  # Empty line
        pdf.cell(200, 10, txt=f"Total Amount: Rs.{total_amount}", ln=True)

        pdf.output("invoice.pdf")
        messagebox.showinfo("Success", "Invoice generated as invoice.pdf")

        # Clear the bill
        for item in self.bill_tree.get_children():
            self.bill_tree.delete(item)

    def manage_inventory(self):
        self.clear_screen()

        self.inventory_tree = ttk.Treeview(self.root, columns=("ID", "Name", "Price", "Stock"), show="headings")
        self.inventory_tree.heading("ID", text="ID")
        self.inventory_tree.heading("Name", text="Product Name")
        self.inventory_tree.heading("Price", text="Price")
        self.inventory_tree.heading("Stock", text="Stock")
        self.inventory_tree.pack(pady=10, fill=tk.BOTH, expand=True)
        self.populate_inventory()

        tk.Button(self.root, text="Add Product", command=self.add_product).pack(pady=5)
        tk.Button(self.root, text="Update Product", command=self.update_product).pack(pady=5)
        tk.Button(self.root, text="Delete Product", command=self.delete_product).pack(pady=5)
        tk.Button(self.root, text="Back", command=self.create_admin_screen).pack(pady=5)

    def add_product(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Add Product")

        tk.Label(add_window, text="Product Name:").pack(pady=5)
        name_entry = tk.Entry(add_window)
        name_entry.pack(pady=5)

        tk.Label(add_window, text="Price:").pack(pady=5)
        price_entry = tk.Entry(add_window)
        price_entry.pack(pady=5)

        tk.Label(add_window, text="Stock:").pack(pady=5)
        stock_entry = tk.Entry(add_window)
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

        tk.Button(add_window, text="Save", command=save_product).pack(pady=10)

    def update_product(self):
        selected_item = self.inventory_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a product to update.")
            return

        product = self.inventory_tree.item(selected_item, "values")
        product_id, product_name, product_price, product_stock = product

        update_window = tk.Toplevel(self.root)
        update_window.title("Update Product")

        tk.Label(update_window, text="Product Name:").pack(pady=5)
        name_entry = tk.Entry(update_window)
        name_entry.insert(0, product_name)
        name_entry.pack(pady=5)

        tk.Label(update_window, text="Price:").pack(pady=5)
        price_entry = tk.Entry(update_window)
        price_entry.insert(0, product_price)
        price_entry.pack(pady=5)

        tk.Label(update_window, text="Stock:").pack(pady=5)
        stock_entry = tk.Entry(update_window)
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

        tk.Button(update_window, text="Save Changes", command=save_changes).pack(pady=10)

    def delete_product(self):
        selected_item = self.inventory_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a product to delete.")
            return

        product = self.inventory_tree.item(selected_item, "values")
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
    root = tk.Tk()
    app = SimpleBillingApp(root)
    root.mainloop()

import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime
import json
import matplotlib.pyplot as plt

class ExpenseTracker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Simple Expense Tracker")
        self.root.geometry("800x600")

        self.expenses = []
        self.load_expenses()
        self.create_gui()

    def create_gui(self):
        input_frame = ttk.LabelFrame(self.root, text="Add New Expense", padding="10")
        input_frame.pack(fill="x", padx=10, pady=5)

        display_frame = ttk.LabelFrame(self.root, text="Expense List", padding="10")
        display_frame.pack(fill="both", expand=True, padx=10, pady=5)

        summary_frame = ttk.LabelFrame(self.root, text="Summary", padding="10")
        summary_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(input_frame, text="Date:").grid(row=0, column=0, padx=5, pady=5)
        self.date_entry = DateEntry(input_frame, width=20, date_pattern='dd/mm/yyyy')
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Category:").grid(row=0, column=2, padx=5, pady=5)
        self.categories = ['Food', 'Transport', 'Entertainment', 'Bills', 'Shopping', 'Other']
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(input_frame, textvariable=self.category_var, values=self.categories, width=17)
        self.category_combo.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(input_frame, text="Amount:").grid(row=1, column=0, padx=5, pady=5)
        self.amount_var = tk.StringVar()
        self.amount_entry = ttk.Entry(input_frame, textvariable=self.amount_var, width=23)
        self.amount_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Description:").grid(row=1, column=2, padx=5, pady=5)
        self.desc_var = tk.StringVar()
        self.desc_entry = ttk.Entry(input_frame, textvariable=self.desc_var, width=20)
        self.desc_entry.grid(row=1, column=3, padx=5, pady=5)

        ttk.Button(input_frame, text="Add Expense", command=self.add_expense).grid(row=2, column=1, pady=10)
        ttk.Button(input_frame, text="Clear Fields", command=self.clear_fields).grid(row=2, column=2, pady=10)

        columns = ('Date', 'Category', 'Amount', 'Description')
        self.tree = ttk.Treeview(display_frame, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(display_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.total_label = ttk.Label(summary_frame, text="Total Expenses: $0")
        self.total_label.pack(side="left", padx=10)

        self.category_total_label = ttk.Label(summary_frame, text="Highest Category: ")
        self.category_total_label.pack(side="left", padx=10)

        ttk.Button(summary_frame, text="View Pie Chart", command=self.show_pie_chart).pack(side="right", padx=10)

        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Delete", command=self.delete_expense)

        self.tree.bind("<Button-3>", self.show_context_menu)
        self.refresh_expense_list()

    def add_expense(self):
        try:
            date = self.date_entry.get_date().strftime("%d/%m/%Y")
            category = self.category_var.get()
            amount = float(self.amount_var.get())
            description = self.desc_var.get()

            if not category:
                messagebox.showerror("Error", "Please select a category!")
                return
            if amount <= 0:
                messagebox.showerror("Error", "Amount must be greater than 0!")
                return

            expense = {
                'date': date,
                'category': category,
                'amount': amount,
                'description': description
            }
            self.expenses.append(expense)
            self.save_expenses()
            self.refresh_expense_list()
            self.clear_fields()
            messagebox.showinfo("Success", "Expense added successfully!")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount!")

    def clear_fields(self):
        self.date_entry.set_date(datetime.now())
        self.category_var.set('')
        self.amount_var.set('')
        self.desc_var.set('')

    def refresh_expense_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for expense in self.expenses:
            try:
                datetime.strptime(expense['date'], "%d/%m/%Y")
            except ValueError:
                try:
                    expense['date'] = datetime.strptime(expense['date'], "%Y-%m-%d").strftime("%d/%m/%Y")
                except ValueError:
                    pass

        sorted_expenses = sorted(self.expenses, key=lambda x: datetime.strptime(x['date'], "%d/%m/%Y"), reverse=True)

        for expense in sorted_expenses:
            self.tree.insert('', 'end', values=(
                expense['date'],
                expense['category'],
                f"${expense['amount']:.2f}",
                expense['description']
            ))

        self.update_summary()

    def update_summary(self):
        total = sum(expense['amount'] for expense in self.expenses)
        self.total_label.config(text=f"Total Expenses: ${total:.2f}")

        category_totals = {}
        for expense in self.expenses:
            category = expense['category']
            category_totals[category] = category_totals.get(category, 0) + expense['amount']

        if category_totals:
            highest_category = max(category_totals.items(), key=lambda x: x[1])
            self.category_total_label.config(
                text=f"Highest Category: {highest_category[0]} (${highest_category[1]:.2f})"
            )

    def delete_expense(self):
        selected_item = self.tree.selection()
        if not selected_item:
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this expense?"):
            values = self.tree.item(selected_item)['values']
            for expense in self.expenses[:]:
                if (expense['date'] == values[0] and 
                    expense['category'] == values[1] and 
                    f"${expense['amount']:.2f}" == values[2] and 
                    expense['description'] == values[3]):
                    self.expenses.remove(expense)
                    break
            self.save_expenses()
            self.refresh_expense_list()

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def show_pie_chart(self):
        if not self.expenses:
            messagebox.showinfo("Info", "No expenses to display in pie chart.")
            return

        category_totals = {}
        for expense in self.expenses:
            category = expense['category']
            category_totals[category] = category_totals.get(category, 0) + expense['amount']

        categories = list(category_totals.keys())
        amounts = list(category_totals.values())

        plt.figure(figsize=(6, 6))
        plt.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90)
        plt.title("Expense Distribution by Category")
        plt.axis('equal')
        plt.tight_layout()
        plt.show()

    def save_expenses(self):
        try:
            with open('expenses.json', 'w') as f:
                json.dump(self.expenses, f)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save expenses: {str(e)}")

    def load_expenses(self):
        try:
            with open('expenses.json', 'r') as f:
                self.expenses = json.load(f)
        except FileNotFoundError:
            self.expenses = []
        except Exception as e:
            messagebox.showerror("Error", f"Could not load expenses: {str(e)}")
            self.expenses = []

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ExpenseTracker()
    app.run()

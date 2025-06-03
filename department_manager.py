
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import uuid
from datetime import datetime


class DepartmentManager:
    def __init__(self, parent_frame, db_manager, update_callback=None):
        self.parent_frame = parent_frame
        self.db = db_manager
        self.update_callback = update_callback
        self.dept_vars = {}
        self.create_widgets()

    def create_widgets(self):
        """Create department management interface"""

        left_panel = ttk.LabelFrame(
            self.parent_frame, text="Thông Tin Phòng Ban", padding="15")
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        dept_fields = [
            ("Mã Phòng Ban:", "dept_code"),
            ("Tên Phòng Ban:", "dept_name"),
            ("Trưởng Phòng:", "manager"),
            ("Số Điện Thoại:", "phone"),
            ("Email:", "email"),
            ("Địa Chỉ:", "address"),
            ("Ngân Sách (VND):", "budget"),
            ("Số NV Tối Đa:", "max_staff")
        ]

        for i, (label, var_name) in enumerate(dept_fields):
            ttk.Label(left_panel, text=label).grid(
                row=i, column=0, sticky=tk.W, pady=3)
            self.dept_vars[var_name] = tk.StringVar()
            widget = ttk.Entry(
                left_panel, textvariable=self.dept_vars[var_name], width=35)
            widget.grid(row=i, column=1, sticky=(
                tk.W, tk.E), pady=3, padx=(5, 0))

        ttk.Label(left_panel, text="Mô Tả:").grid(
            row=len(dept_fields), column=0, sticky=tk.W, pady=3)
        self.dept_description_text = tk.Text(left_panel, width=35, height=3)
        self.dept_description_text.grid(
            row=len(dept_fields), column=1, sticky=(tk.W, tk.E), pady=3, padx=(5, 0))

        dept_btn_frame = ttk.Frame(left_panel)
        dept_btn_frame.grid(row=len(dept_fields)+1,
                            column=0, columnspan=2, pady=(15, 0))

        ttk.Button(dept_btn_frame, text="Thêm", command=self.add_department).pack(
            side=tk.LEFT, padx=(0, 5))
        ttk.Button(dept_btn_frame, text="Cập Nhật", command=self.update_department).pack(
            side=tk.LEFT, padx=(0, 5))
        ttk.Button(dept_btn_frame, text="Xóa", command=self.delete_department).pack(
            side=tk.LEFT, padx=(0, 5))
        ttk.Button(dept_btn_frame, text="Làm Mới",
                   command=self.clear_form).pack(side=tk.LEFT)

        right_panel = ttk.LabelFrame(
            self.parent_frame, text="Danh Sách Phòng Ban", padding="15")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        search_frame = ttk.Frame(right_panel)
        search_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(search_frame, text="Tìm kiếm:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(
            search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=(5, 10))
        search_entry.bind('<KeyRelease>', self.search_departments)

        ttk.Button(search_frame, text="Làm Mới",
                   command=self.refresh_list).pack(side=tk.RIGHT)

        columns = ("Mã PB", "Tên Phòng Ban", "Trưởng Phòng",
                   "SĐT", "Email", "Số NV", "Ngân Sách")
        self.tree = ttk.Treeview(
            right_panel, columns=columns, show='headings', height=20)

        widths = [80, 200, 150, 120, 180, 80, 120]
        for col, width in zip(columns, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, minwidth=60)

        v_scroll = ttk.Scrollbar(
            right_panel, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_scroll.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind('<<TreeviewSelect>>', self.on_select)

        self.refresh_list()

    def add_department(self):
        """Add new department"""
        if not self.validate_input():
            return

        dept_data = {
            'id': str(uuid.uuid4()),
            'dept_code': self.dept_vars['dept_code'].get(),
            'dept_name': self.dept_vars['dept_name'].get(),
            'description': self.dept_description_text.get("1.0", tk.END).strip(),
            'manager': self.dept_vars['manager'].get(),
            'phone': self.dept_vars['phone'].get(),
            'email': self.dept_vars['email'].get(),
            'address': self.dept_vars['address'].get(),
            'budget': self.dept_vars['budget'].get(),
            'max_staff': int(self.dept_vars['max_staff'].get()) if self.dept_vars['max_staff'].get().isdigit() else 0,
            'created_date': datetime.now().isoformat(),
            'status': 'active'
        }

        try:
            self.db.insert_data('departments', dept_data)
            self.refresh_list()
            if self.update_callback:
                self.update_callback()
            self.clear_form()
            messagebox.showinfo("Thành công", "Đã thêm phòng ban thành công!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Lỗi", "Mã phòng ban đã tồn tại!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thêm phòng ban: {str(e)}")

    def update_department(self):
        """Update selected department"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                "Cảnh báo", "Vui lòng chọn phòng ban để cập nhật!")
            return

        if not self.validate_input():
            return

        dept_code = self.tree.item(selected[0])['values'][0]
        dept_data = {
            'dept_code': self.dept_vars['dept_code'].get(),
            'dept_name': self.dept_vars['dept_name'].get(),
            'description': self.dept_description_text.get("1.0", tk.END).strip(),
            'manager': self.dept_vars['manager'].get(),
            'phone': self.dept_vars['phone'].get(),
            'email': self.dept_vars['email'].get(),
            'address': self.dept_vars['address'].get(),
            'budget': self.dept_vars['budget'].get(),
            'max_staff': int(self.dept_vars['max_staff'].get()) if self.dept_vars['max_staff'].get().isdigit() else 0
        }

        try:
            self.db.update_data('departments', dept_data, {
                                'column': 'dept_code', 'value': dept_code})
            self.refresh_list()
            if self.update_callback:
                self.update_callback()
            self.clear_form()
            messagebox.showinfo(
                "Thành công", "Đã cập nhật phòng ban thành công!")
        except Exception as e:
            messagebox.showerror(
                "Lỗi", f"Không thể cập nhật phòng ban: {str(e)}")

    def delete_department(self):
        """Delete selected department"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                "Cảnh báo", "Vui lòng chọn phòng ban để xóa!")
            return

        dept_code = self.tree.item(selected[0])['values'][0]

        staff_count = self.db.execute_query(
            "SELECT COUNT(*) FROM staff WHERE department_id = (SELECT id FROM departments WHERE dept_code = ?)",
            [dept_code]
        )[0][0]

        if staff_count > 0:
            if not messagebox.askyesno("Xác nhận", f"Phòng ban có {staff_count} cán bộ. Bạn có chắc chắn muốn xóa?"):
                return

        try:

            dept_id = self.db.execute_query(
                "SELECT id FROM departments WHERE dept_code = ?", [dept_code]
            )[0][0]

            self.db.execute_query(
                "DELETE FROM kpi_assignments WHERE kpi_id IN (SELECT id FROM kpi WHERE department_id = ?)", [dept_id])
            self.db.execute_query(
                "DELETE FROM kpi_results WHERE kpi_id IN (SELECT id FROM kpi WHERE department_id = ?)", [dept_id])
            self.db.execute_query(
                "DELETE FROM kpi WHERE department_id = ?", [dept_id])
            self.db.execute_query(
                "DELETE FROM staff WHERE department_id = ?", [dept_id])
            self.db.delete_data(
                'departments', {'column': 'dept_code', 'value': dept_code})

            self.refresh_list()
            if self.update_callback:
                self.update_callback()
            self.clear_form()
            messagebox.showinfo(
                "Thành công", "Đã xóa phòng ban và dữ liệu liên quan!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xóa phòng ban: {str(e)}")

    def validate_input(self):
        """Validate form input"""
        required_fields = ['dept_code', 'dept_name', 'manager']
        for field in required_fields:
            if not self.dept_vars[field].get().strip():
                messagebox.showerror("Lỗi", f"Vui lòng nhập {field}!")
                return False
        return True

    def clear_form(self):
        """Clear all form fields"""
        for var in self.dept_vars.values():
            var.set("")
        self.dept_description_text.delete("1.0", tk.END)

    def on_select(self, event):
        """Handle tree selection"""
        selected = self.tree.selection()
        if selected:
            dept_code = self.tree.item(selected[0])['values'][0]
            dept_data = self.db.execute_query(
                "SELECT * FROM departments WHERE dept_code = ?", [dept_code]
            )
            if dept_data:
                dept = dept_data[0]
                self.dept_vars['dept_code'].set(dept[1])
                self.dept_vars['dept_name'].set(dept[2])
                self.dept_description_text.delete("1.0", tk.END)
                self.dept_description_text.insert("1.0", dept[3] or "")
                self.dept_vars['manager'].set(dept[4] or "")
                self.dept_vars['phone'].set(dept[5] or "")
                self.dept_vars['email'].set(dept[6] or "")
                self.dept_vars['address'].set(dept[7] or "")
                self.dept_vars['budget'].set(dept[8] or "")
                self.dept_vars['max_staff'].set(str(dept[9] or ""))

    def search_departments(self, event):
        """Search departments"""
        search_term = self.search_var.get().lower()

        for item in self.tree.get_children():
            self.tree.delete(item)

        query = """
            SELECT dept_code, dept_name, manager, phone, email, 
                   (SELECT COUNT(*) FROM staff WHERE department_id = departments.id) as staff_count,
                   budget
            FROM departments 
            WHERE (LOWER(dept_name) LIKE ? OR LOWER(dept_code) LIKE ? OR LOWER(manager) LIKE ?)
            AND status = 'active'
            ORDER BY dept_code
        """

        results = self.db.execute_query(
            query, [f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"])

        for row in results:
            self.tree.insert("", "end", values=row)

    def refresh_list(self):
        """Refresh department list"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        query = """
            SELECT dept_code, dept_name, manager, phone, email, 
                   (SELECT COUNT(*) FROM staff WHERE department_id = departments.id) as staff_count,
                   budget
            FROM departments 
            WHERE status = 'active'
            ORDER BY dept_code
        """

        results = self.db.execute_query(query)

        for row in results:
            self.tree.insert("", "end", values=row)

    def get_department_names(self):
        """Get list of department names for comboboxes"""
        return [row[0] for row in self.db.execute_query("SELECT dept_name FROM departments WHERE status = 'active' ORDER BY dept_name")]

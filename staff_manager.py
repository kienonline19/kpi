
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import uuid
from datetime import datetime


class StaffManager:
    def __init__(self, parent_frame, db_manager, update_callback=None):
        self.parent_frame = parent_frame
        self.db = db_manager
        self.update_callback = update_callback
        self.staff_vars = {}

        self.positions = ["Giám đốc", "Phó giám đốc", "Trưởng phòng", "Phó trưởng phòng",
                          "Chuyên viên chính", "Chuyên viên", "Nhân viên", "Thực tập sinh"]
        self.education_levels = ["Tiến sĩ", "Thạc sĩ",
                                 "Đại học", "Cao đẳng", "Trung cấp", "THPT"]

        self.create_widgets()

    def create_widgets(self):
        """Create staff management interface"""

        left_panel = ttk.LabelFrame(
            self.parent_frame, text="Thông Tin Cán Bộ", padding="15")
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        staff_fields = [
            ("Mã Cán Bộ:", "staff_code"),
            ("Họ và Tên:", "full_name"),
            ("Ngày Sinh:", "birth_date"),
            ("Giới Tính:", "gender"),
            ("CCCD/CMND:", "id_number"),
            ("Số Điện Thoại:", "phone"),
            ("Email:", "email"),
            ("Phòng Ban:", "department_id"),
            ("Chức Vụ:", "position"),
            ("Trình Độ:", "education"),
            ("Lương CB (VND):", "basic_salary"),
            ("Ngày Vào Làm:", "start_date"),
            ("Trạng Thái:", "status")
        ]

        for i, (label, var_name) in enumerate(staff_fields):
            ttk.Label(left_panel, text=label).grid(
                row=i, column=0, sticky=tk.W, pady=3)

            if var_name == "gender":
                self.staff_vars[var_name] = tk.StringVar(value="Nam")
                widget = ttk.Combobox(left_panel, textvariable=self.staff_vars[var_name],
                                      values=["Nam", "Nữ"], width=32)
            elif var_name == "department_id":
                self.staff_vars[var_name] = tk.StringVar()
                widget = ttk.Combobox(left_panel, textvariable=self.staff_vars[var_name],
                                      values=[], width=32)
                self.dept_combobox = widget
            elif var_name == "position":
                self.staff_vars[var_name] = tk.StringVar(
                    value=self.positions[0])
                widget = ttk.Combobox(left_panel, textvariable=self.staff_vars[var_name],
                                      values=self.positions, width=32)
            elif var_name == "education":
                self.staff_vars[var_name] = tk.StringVar(
                    value=self.education_levels[0])
                widget = ttk.Combobox(left_panel, textvariable=self.staff_vars[var_name],
                                      values=self.education_levels, width=32)
            elif var_name == "status":
                self.staff_vars[var_name] = tk.StringVar(value="active")
                widget = ttk.Combobox(left_panel, textvariable=self.staff_vars[var_name],
                                      values=["active", "inactive", "on_leave"], width=32)
            else:
                self.staff_vars[var_name] = tk.StringVar()
                widget = ttk.Entry(
                    left_panel, textvariable=self.staff_vars[var_name], width=35)

            widget.grid(row=i, column=1, sticky=(
                tk.W, tk.E), pady=3, padx=(5, 0))

        ttk.Label(left_panel, text="Địa Chỉ:").grid(
            row=len(staff_fields), column=0, sticky=tk.W, pady=3)
        self.address_text = tk.Text(left_panel, width=35, height=2)
        self.address_text.grid(row=len(staff_fields), column=1, sticky=(
            tk.W, tk.E), pady=3, padx=(5, 0))

        btn_frame = ttk.Frame(left_panel)
        btn_frame.grid(row=len(staff_fields)+1, column=0,
                       columnspan=2, pady=(15, 0))

        ttk.Button(btn_frame, text="Thêm", command=self.add_staff).pack(
            side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Cập Nhật", command=self.update_staff).pack(
            side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Xóa", command=self.delete_staff).pack(
            side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Làm Mới",
                   command=self.clear_form).pack(side=tk.LEFT)

        right_panel = ttk.LabelFrame(
            self.parent_frame, text="Danh Sách Cán Bộ", padding="15")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        filter_frame = ttk.Frame(right_panel)
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(filter_frame, text="Tìm kiếm:").grid(row=0, column=0)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(
            filter_frame, textvariable=self.search_var, width=25)
        search_entry.grid(row=0, column=1, padx=(5, 10))
        search_entry.bind('<KeyRelease>', self.search_staff)

        ttk.Label(filter_frame, text="Phòng ban:").grid(row=0, column=2)
        self.dept_filter_var = tk.StringVar(value="Tất cả")
        dept_filter_combo = ttk.Combobox(
            filter_frame, textvariable=self.dept_filter_var, width=20)
        dept_filter_combo.grid(row=0, column=3, padx=(5, 10))
        dept_filter_combo.bind('<<ComboboxSelected>>', self.filter_staff)
        self.dept_filter_combo = dept_filter_combo

        ttk.Button(filter_frame, text="Làm Mới", command=self.refresh_list).grid(
            row=0, column=4, padx=(10, 0))

        columns = ("Mã CB", "Họ Tên", "Phòng Ban", "Chức Vụ",
                   "SĐT", "Email", "Lương", "Trạng Thái")
        self.tree = ttk.Treeview(
            right_panel, columns=columns, show='headings', height=22)

        widths = [80, 150, 150, 120, 120, 180, 120, 100]
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
        self.update_department_comboboxes()

    def add_staff(self):
        """Add new staff member"""
        if not self.validate_input():
            return

        dept_name = self.staff_vars['department_id'].get()
        dept_id_result = self.db.execute_query(
            "SELECT id FROM departments WHERE dept_name = ?", [dept_name]
        )

        if not dept_id_result:
            messagebox.showerror("Lỗi", "Phòng ban không tồn tại!")
            return

        staff_data = {
            'id': str(uuid.uuid4()),
            'staff_code': self.staff_vars['staff_code'].get(),
            'full_name': self.staff_vars['full_name'].get(),
            'birth_date': self.staff_vars['birth_date'].get(),
            'gender': self.staff_vars['gender'].get(),
            'id_number': self.staff_vars['id_number'].get(),
            'phone': self.staff_vars['phone'].get(),
            'email': self.staff_vars['email'].get(),
            'address': self.address_text.get("1.0", tk.END).strip(),
            'department_id': dept_id_result[0][0],
            'position': self.staff_vars['position'].get(),
            'education': self.staff_vars['education'].get(),
            'basic_salary': self.staff_vars['basic_salary'].get(),
            'start_date': self.staff_vars['start_date'].get(),
            'status': self.staff_vars['status'].get(),
            'created_date': datetime.now().isoformat()
        }

        try:
            self.db.insert_data('staff', staff_data)
            self.refresh_list()
            if self.update_callback:
                self.update_callback()
            self.clear_form()
            messagebox.showinfo("Thành công", "Đã thêm cán bộ thành công!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Lỗi", "Mã cán bộ đã tồn tại!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thêm cán bộ: {str(e)}")

    def update_staff(self):
        """Update selected staff member"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                "Cảnh báo", "Vui lòng chọn cán bộ để cập nhật!")
            return

        if not self.validate_input():
            return

        staff_code = self.tree.item(selected[0])['values'][0]

        dept_name = self.staff_vars['department_id'].get()
        dept_id_result = self.db.execute_query(
            "SELECT id FROM departments WHERE dept_name = ?", [dept_name]
        )

        if not dept_id_result:
            messagebox.showerror("Lỗi", "Phòng ban không tồn tại!")
            return

        staff_data = {
            'staff_code': self.staff_vars['staff_code'].get(),
            'full_name': self.staff_vars['full_name'].get(),
            'birth_date': self.staff_vars['birth_date'].get(),
            'gender': self.staff_vars['gender'].get(),
            'id_number': self.staff_vars['id_number'].get(),
            'phone': self.staff_vars['phone'].get(),
            'email': self.staff_vars['email'].get(),
            'address': self.address_text.get("1.0", tk.END).strip(),
            'department_id': dept_id_result[0][0],
            'position': self.staff_vars['position'].get(),
            'education': self.staff_vars['education'].get(),
            'basic_salary': self.staff_vars['basic_salary'].get(),
            'start_date': self.staff_vars['start_date'].get(),
            'status': self.staff_vars['status'].get()
        }

        try:
            self.db.update_data('staff', staff_data, {
                                'column': 'staff_code', 'value': staff_code})
            self.refresh_list()
            if self.update_callback:
                self.update_callback()
            self.clear_form()
            messagebox.showinfo("Thành công", "Đã cập nhật cán bộ thành công!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể cập nhật cán bộ: {str(e)}")

    def delete_staff(self):
        """Delete selected staff member"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn cán bộ để xóa!")
            return

        staff_code = self.tree.item(selected[0])['values'][0]

        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa cán bộ này?"):
            try:

                staff_id = self.db.execute_query(
                    "SELECT id FROM staff WHERE staff_code = ?", [staff_code]
                )[0][0]

                self.db.delete_data('kpi_assignments', {
                                    'column': 'staff_id', 'value': staff_id})

                self.db.delete_data(
                    'staff', {'column': 'staff_code', 'value': staff_code})

                self.refresh_list()
                if self.update_callback:
                    self.update_callback()
                self.clear_form()
                messagebox.showinfo("Thành công", "Đã xóa cán bộ thành công!")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa cán bộ: {str(e)}")

    def validate_input(self):
        """Validate form input"""
        required_fields = ['staff_code',
                           'full_name', 'department_id', 'position']
        for field in required_fields:
            if not self.staff_vars[field].get().strip():
                messagebox.showerror("Lỗi", f"Vui lòng nhập {field}!")
                return False
        return True

    def clear_form(self):
        """Clear all form fields"""
        for var in self.staff_vars.values():
            var.set("")
        self.address_text.delete("1.0", tk.END)
        self.staff_vars['gender'].set("Nam")
        self.staff_vars['position'].set(self.positions[0])
        self.staff_vars['education'].set(self.education_levels[0])
        self.staff_vars['status'].set("active")

    def on_select(self, event):
        """Handle tree selection"""
        selected = self.tree.selection()
        if selected:
            staff_code = self.tree.item(selected[0])['values'][0]
            staff_data = self.db.execute_query("""
                SELECT s.*, d.dept_name FROM staff s 
                JOIN departments d ON s.department_id = d.id 
                WHERE s.staff_code = ?
            """, [staff_code])

            if staff_data:
                staff = staff_data[0]
                self.staff_vars['staff_code'].set(staff[1])
                self.staff_vars['full_name'].set(staff[2])
                self.staff_vars['birth_date'].set(staff[3] or "")
                self.staff_vars['gender'].set(staff[4] or "Nam")
                self.staff_vars['id_number'].set(staff[5] or "")
                self.staff_vars['phone'].set(staff[6] or "")
                self.staff_vars['email'].set(staff[7] or "")
                self.address_text.delete("1.0", tk.END)
                self.address_text.insert("1.0", staff[8] or "")
                self.staff_vars['department_id'].set(staff[17])
                self.staff_vars['position'].set(staff[10] or "")
                self.staff_vars['education'].set(staff[11] or "")
                self.staff_vars['basic_salary'].set(staff[12] or "")
                self.staff_vars['start_date'].set(staff[13] or "")
                self.staff_vars['status'].set(staff[14] or "active")

    def search_staff(self, event):
        """Search staff"""
        self.filter_staff()

    def filter_staff(self, event=None):
        """Filter staff list"""
        search_term = self.search_var.get().lower()
        dept_filter = self.dept_filter_var.get()

        for item in self.tree.get_children():
            self.tree.delete(item)

        query = """
            SELECT s.staff_code, s.full_name, d.dept_name, s.position, s.phone, s.email, s.basic_salary, s.status
            FROM staff s
            JOIN departments d ON s.department_id = d.id
            WHERE (LOWER(s.full_name) LIKE ? OR LOWER(s.staff_code) LIKE ?)
        """
        params = [f"%{search_term}%", f"%{search_term}%"]

        if dept_filter != "Tất cả":
            query += " AND d.dept_name = ?"
            params.append(dept_filter)

        query += " ORDER BY s.staff_code"

        results = self.db.execute_query(query, params)

        for row in results:
            self.tree.insert("", "end", values=row)

    def refresh_list(self):
        """Refresh staff list"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        query = """
            SELECT s.staff_code, s.full_name, d.dept_name, s.position, s.phone, s.email, s.basic_salary, s.status
            FROM staff s
            JOIN departments d ON s.department_id = d.id
            ORDER BY s.staff_code
        """

        results = self.db.execute_query(query)

        for row in results:
            self.tree.insert("", "end", values=row)

    def update_department_comboboxes(self):
        """Update department comboboxes with current data"""
        dept_names = [row[0] for row in self.db.execute_query(
            "SELECT dept_name FROM departments WHERE status = 'active' ORDER BY dept_name")]

        self.dept_combobox['values'] = dept_names

        self.dept_filter_combo['values'] = ["Tất cả"] + dept_names

    def get_staff_displays(self):
        """Get list of staff displays for comboboxes"""
        return [f"{row[0]} - {row[1]}" for row in self.db.execute_query("SELECT staff_code, full_name FROM staff WHERE status = 'active' ORDER BY staff_code")]

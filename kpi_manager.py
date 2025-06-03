# kpi_manager.py
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import uuid
from datetime import datetime

class KPIManager:
    def __init__(self, parent_frame, db_manager, update_callback=None):
        self.parent_frame = parent_frame
        self.db = db_manager
        self.update_callback = update_callback
        self.kpi_vars = {}
        
        # Predefined lists
        self.kpi_frequencies = ["Hàng ngày", "Hàng tuần", "Hàng tháng", "Hàng quý", "Hàng năm"]
        self.kpi_units = ["VND", "USD", "%", "Số lượng", "Tỷ lệ", "Điểm", "Giờ", "Ngày"]
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create KPI management interface"""
        # Left panel - KPI form
        left_panel = ttk.LabelFrame(self.parent_frame, text="Thông Tin KPI", padding="15")
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # KPI form fields
        kpi_fields = [
            ("Mã KPI:", "kpi_code"),
            ("Tên KPI:", "kpi_name"),
            ("Danh Mục:", "category_id"),
            ("Phòng Ban:", "department_id"),
            ("Đơn Vị Tính:", "unit"),
            ("Giá Trị Mục Tiêu:", "target_value"),
            ("Trọng Số (%):", "weight"),
            ("Tần Suất Đo:", "measurement_frequency"),
            ("Trạng Thái:", "status")
        ]
        
        for i, (label, var_name) in enumerate(kpi_fields):
            ttk.Label(left_panel, text=label).grid(row=i, column=0, sticky=tk.W, pady=3)
            
            if var_name == "category_id":
                self.kpi_vars[var_name] = tk.StringVar()
                widget = ttk.Combobox(left_panel, textvariable=self.kpi_vars[var_name],
                                    values=[], width=32)
                self.category_combobox = widget
            elif var_name == "department_id":
                self.kpi_vars[var_name] = tk.StringVar()
                widget = ttk.Combobox(left_panel, textvariable=self.kpi_vars[var_name],
                                    values=[], width=32)
                self.dept_combobox = widget
            elif var_name == "unit":
                self.kpi_vars[var_name] = tk.StringVar(value=self.kpi_units[0])
                widget = ttk.Combobox(left_panel, textvariable=self.kpi_vars[var_name],
                                    values=self.kpi_units, width=32)
            elif var_name == "measurement_frequency":
                self.kpi_vars[var_name] = tk.StringVar(value=self.kpi_frequencies[0])
                widget = ttk.Combobox(left_panel, textvariable=self.kpi_vars[var_name],
                                    values=self.kpi_frequencies, width=32)
            elif var_name == "status":
                self.kpi_vars[var_name] = tk.StringVar(value="active")
                widget = ttk.Combobox(left_panel, textvariable=self.kpi_vars[var_name],
                                    values=["active", "inactive", "draft"], width=32)
            else:
                self.kpi_vars[var_name] = tk.StringVar()
                widget = ttk.Entry(left_panel, textvariable=self.kpi_vars[var_name], width=35)
            
            widget.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=3, padx=(5, 0))
        
        # Description field
        ttk.Label(left_panel, text="Mô Tả:").grid(row=len(kpi_fields), column=0, sticky=tk.W, pady=3)
        self.description_text = tk.Text(left_panel, width=35, height=3)
        self.description_text.grid(row=len(kpi_fields), column=1, sticky=(tk.W, tk.E), pady=3, padx=(5, 0))
        
        # KPI buttons
        btn_frame = ttk.Frame(left_panel)
        btn_frame.grid(row=len(kpi_fields)+1, column=0, columnspan=2, pady=(15, 0))
        
        ttk.Button(btn_frame, text="Thêm", command=self.add_kpi).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Cập Nhật", command=self.update_kpi).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Xóa", command=self.delete_kpi).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Làm Mới", command=self.clear_form).pack(side=tk.LEFT)
        
        # Right panel - KPI list
        right_panel = ttk.LabelFrame(self.parent_frame, text="Danh Sách KPI", padding="15")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # KPI search and filter frame
        filter_frame = ttk.Frame(right_panel)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Search
        ttk.Label(filter_frame, text="Tìm kiếm:").grid(row=0, column=0)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, width=25)
        search_entry.grid(row=0, column=1, padx=(5, 10))
        search_entry.bind('<KeyRelease>', self.search_kpi)
        
        # Department filter
        ttk.Label(filter_frame, text="Phòng ban:").grid(row=0, column=2)
        self.dept_filter_var = tk.StringVar(value="Tất cả")
        dept_filter_combo = ttk.Combobox(filter_frame, textvariable=self.dept_filter_var, width=20)
        dept_filter_combo.grid(row=0, column=3, padx=(5, 10))
        dept_filter_combo.bind('<<ComboboxSelected>>', self.filter_kpi)
        self.dept_filter_combo = dept_filter_combo
        
        ttk.Button(filter_frame, text="Làm Mới", command=self.refresh_list).grid(row=0, column=4, padx=(10, 0))
        
        # KPI treeview
        columns = ("Mã KPI", "Tên KPI", "Phòng Ban", "Đơn Vị", "Mục Tiêu", "Trọng Số", "Tần Suất", "Trạng Thái")
        self.tree = ttk.Treeview(right_panel, columns=columns, show='headings', height=22)
        
        # Configure columns
        widths = [80, 200, 120, 80, 100, 80, 100, 80]
        for col, width in zip(columns, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, minwidth=60)
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(right_panel, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_scroll.set)
        
        # Pack treeview and scrollbars
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        
        # Load initial data
        self.refresh_list()
        self.update_comboboxes()
    
    def add_kpi(self):
        """Add new KPI"""
        if not self.validate_input():
            return
            
        # Get category and department IDs
        category_name = self.kpi_vars['category_id'].get()
        dept_name = self.kpi_vars['department_id'].get()
        
        category_id = None
        if category_name:
            cat_result = self.db.execute_query(
                "SELECT id FROM kpi_categories WHERE category_name = ?", [category_name]
            )
            if cat_result:
                category_id = cat_result[0][0]
        
        dept_id = None
        if dept_name:
            dept_result = self.db.execute_query(
                "SELECT id FROM departments WHERE dept_name = ?", [dept_name]
            )
            if dept_result:
                dept_id = dept_result[0][0]
        
        kpi_data = {
            'id': str(uuid.uuid4()),
            'kpi_code': self.kpi_vars['kpi_code'].get(),
            'kpi_name': self.kpi_vars['kpi_name'].get(),
            'description': self.description_text.get("1.0", tk.END).strip(),
            'category_id': category_id,
            'department_id': dept_id,
            'unit': self.kpi_vars['unit'].get(),
            'target_value': float(self.kpi_vars['target_value'].get()) if self.kpi_vars['target_value'].get() else 0,
            'weight': float(self.kpi_vars['weight'].get()) if self.kpi_vars['weight'].get() else 0,
            'measurement_frequency': self.kpi_vars['measurement_frequency'].get(),
            'created_date': datetime.now().isoformat(),
            'status': self.kpi_vars['status'].get()
        }
        
        try:
            self.db.insert_data('kpi', kpi_data)
            self.refresh_list()
            if self.update_callback:
                self.update_callback()
            self.clear_form()
            messagebox.showinfo("Thành công", "Đã thêm KPI thành công!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Lỗi", "Mã KPI đã tồn tại!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thêm KPI: {str(e)}")
    
    def update_kpi(self):
        """Update selected KPI"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn KPI để cập nhật!")
            return
            
        if not self.validate_input():
            return
            
        kpi_code = self.tree.item(selected[0])['values'][0]
        
        # Get category and department IDs
        category_name = self.kpi_vars['category_id'].get()
        dept_name = self.kpi_vars['department_id'].get()
        
        category_id = None
        if category_name:
            cat_result = self.db.execute_query(
                "SELECT id FROM kpi_categories WHERE category_name = ?", [category_name]
            )
            if cat_result:
                category_id = cat_result[0][0]
        
        dept_id = None
        if dept_name:
            dept_result = self.db.execute_query(
                "SELECT id FROM departments WHERE dept_name = ?", [dept_name]
            )
            if dept_result:
                dept_id = dept_result[0][0]
        
        kpi_data = {
            'kpi_code': self.kpi_vars['kpi_code'].get(),
            'kpi_name': self.kpi_vars['kpi_name'].get(),
            'description': self.description_text.get("1.0", tk.END).strip(),
            'category_id': category_id,
            'department_id': dept_id,
            'unit': self.kpi_vars['unit'].get(),
            'target_value': float(self.kpi_vars['target_value'].get()) if self.kpi_vars['target_value'].get() else 0,
            'weight': float(self.kpi_vars['weight'].get()) if self.kpi_vars['weight'].get() else 0,
            'measurement_frequency': self.kpi_vars['measurement_frequency'].get(),
            'status': self.kpi_vars['status'].get()
        }
        
        try:
            self.db.update_data('kpi', kpi_data, {'column': 'kpi_code', 'value': kpi_code})
            self.refresh_list()
            if self.update_callback:
                self.update_callback()
            self.clear_form()
            messagebox.showinfo("Thành công", "Đã cập nhật KPI thành công!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể cập nhật KPI: {str(e)}")
    
    def delete_kpi(self):
        """Delete selected KPI"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn KPI để xóa!")
            return
            
        kpi_code = self.tree.item(selected[0])['values'][0]
        
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa KPI này?"):
            try:
                # Get KPI ID
                kpi_id = self.db.execute_query(
                    "SELECT id FROM kpi WHERE kpi_code = ?", [kpi_code]
                )[0][0]
                
                # Delete related data
                self.db.delete_data('kpi_results', {'column': 'kpi_id', 'value': kpi_id})
                self.db.delete_data('kpi_assignments', {'column': 'kpi_id', 'value': kpi_id})
                self.db.delete_data('kpi', {'column': 'kpi_code', 'value': kpi_code})
                
                self.refresh_list()
                if self.update_callback:
                    self.update_callback()
                self.clear_form()
                messagebox.showinfo("Thành công", "Đã xóa KPI và dữ liệu liên quan!")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa KPI: {str(e)}")
    
    def validate_input(self):
        """Validate form input"""
        required_fields = ['kpi_code', 'kpi_name']
        for field in required_fields:
            if not self.kpi_vars[field].get().strip():
                messagebox.showerror("Lỗi", f"Vui lòng nhập {field}!")
                return False
        return True
    
    def clear_form(self):
        """Clear all form fields"""
        for var in self.kpi_vars.values():
            var.set("")
        self.description_text.delete("1.0", tk.END)
        self.kpi_vars['unit'].set(self.kpi_units[0])
        self.kpi_vars['measurement_frequency'].set(self.kpi_frequencies[0])
        self.kpi_vars['status'].set("active")
    
    def on_select(self, event):
        """Handle tree selection"""
        selected = self.tree.selection()
        if selected:
            kpi_code = self.tree.item(selected[0])['values'][0]
            kpi_data = self.db.execute_query("""
                SELECT k.*, c.category_name, d.dept_name 
                FROM kpi k
                LEFT JOIN kpi_categories c ON k.category_id = c.id
                LEFT JOIN departments d ON k.department_id = d.id
                WHERE k.kpi_code = ?
            """, [kpi_code])
            
            if kpi_data:
                kpi = kpi_data[0]
                self.kpi_vars['kpi_code'].set(kpi[1])
                self.kpi_vars['kpi_name'].set(kpi[2])
                self.description_text.delete("1.0", tk.END)
                self.description_text.insert("1.0", kpi[3] or "")
                self.kpi_vars['category_id'].set(kpi[13] or "")  # category_name from join
                self.kpi_vars['department_id'].set(kpi[14] or "")  # dept_name from join
                self.kpi_vars['unit'].set(kpi[6] or "")
                self.kpi_vars['target_value'].set(str(kpi[7] or ""))
                self.kpi_vars['weight'].set(str(kpi[8] or ""))
                self.kpi_vars['measurement_frequency'].set(kpi[9] or "")
                self.kpi_vars['status'].set(kpi[11] or "active")
    
    def search_kpi(self, event):
        """Search KPI"""
        self.filter_kpi()
    
    def filter_kpi(self, event=None):
        """Filter KPI list"""
        search_term = self.search_var.get().lower()
        dept_filter = self.dept_filter_var.get()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        query = """
            SELECT k.kpi_code, k.kpi_name, COALESCE(d.dept_name, 'Không có'), k.unit, 
                   k.target_value, k.weight, k.measurement_frequency, k.status
            FROM kpi k
            LEFT JOIN departments d ON k.department_id = d.id
            WHERE (LOWER(k.kpi_name) LIKE ? OR LOWER(k.kpi_code) LIKE ?)
        """
        params = [f"%{search_term}%", f"%{search_term}%"]
        
        if dept_filter != "Tất cả":
            query += " AND d.dept_name = ?"
            params.append(dept_filter)
        
        query += " ORDER BY k.kpi_code"
        
        results = self.db.execute_query(query, params)
        
        for row in results:
            self.tree.insert("", "end", values=row)
    
    def refresh_list(self):
        """Refresh KPI list"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        query = """
            SELECT k.kpi_code, k.kpi_name, COALESCE(d.dept_name, 'Không có'), k.unit, 
                   k.target_value, k.weight, k.measurement_frequency, k.status
            FROM kpi k
            LEFT JOIN departments d ON k.department_id = d.id
            ORDER BY k.kpi_code
        """
        
        results = self.db.execute_query(query)
        
        for row in results:
            self.tree.insert("", "end", values=row)
    
    def update_comboboxes(self):
        """Update comboboxes with current data"""
        # Update department comboboxes
        dept_names = [row[0] for row in self.db.execute_query("SELECT dept_name FROM departments WHERE status = 'active' ORDER BY dept_name")]
        self.dept_combobox['values'] = dept_names
        self.dept_filter_combo['values'] = ["Tất cả"] + dept_names
        
        # Update category comboboxes
        cat_names = [row[0] for row in self.db.execute_query("SELECT category_name FROM kpi_categories ORDER BY category_name")]
        self.category_combobox['values'] = cat_names
    
    def get_kpi_displays(self):
        """Get list of KPI displays for comboboxes"""
        return [f"{row[0]} - {row[1]}" for row in self.db.execute_query("SELECT kpi_code, kpi_name FROM kpi WHERE status = 'active' ORDER BY kpi_code")]
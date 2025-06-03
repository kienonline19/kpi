# main.py
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import uuid
from datetime import datetime

# Import các module
from database_manager import DatabaseManager
from department_manager import DepartmentManager
from staff_manager import StaffManager
from kpi_manager import KPIManager
from reports_manager import ReportsManager

class MainApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("Hệ Thống Quản Lý Tích Hợp - KPI, Phòng Ban, Cán Bộ")
        self.root.geometry("1600x1000")
        self.root.state('zoomed')
        
        # Initialize database
        self.db = DatabaseManager()
        
        # Predefined lists
        self.kpi_frequencies = ["Hàng ngày", "Hàng tuần", "Hàng tháng", "Hàng quý", "Hàng năm"]
        self.kpi_units = ["VND", "USD", "%", "Số lượng", "Tỷ lệ", "Điểm", "Giờ", "Ngày"]
        
        # Create main interface
        self.create_widgets()
        
        # Load sample data
        self.db.load_sample_data()
        
        # Update all comboboxes
        self.update_all_comboboxes()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="HỆ THỐNG QUẢN LÝ TÍCH HỢP", 
                               font=('Arial', 20, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_department_tab()
        self.create_staff_tab()
        self.create_kpi_tab()
        self.create_kpi_assignment_tab()
        self.create_kpi_results_tab()
        self.create_reports_tab()
        self.create_admin_tab()
        
    def create_department_tab(self):
        """Department management tab"""
        dept_frame = ttk.Frame(self.notebook)
        self.notebook.add(dept_frame, text="🏢 Phòng Ban")
        
        # Initialize department manager
        self.dept_manager = DepartmentManager(dept_frame, self.db, self.update_all_comboboxes)
        
    def create_staff_tab(self):
        """Staff management tab"""
        staff_frame = ttk.Frame(self.notebook)
        self.notebook.add(staff_frame, text="👥 Cán Bộ")
        
        # Initialize staff manager
        self.staff_manager = StaffManager(staff_frame, self.db, self.update_all_comboboxes)
        
    def create_kpi_tab(self):
        """KPI management tab"""
        kpi_frame = ttk.Frame(self.notebook)
        self.notebook.add(kpi_frame, text="📊 KPI")
        
        # Initialize KPI manager
        self.kpi_manager = KPIManager(kpi_frame, self.db, self.update_all_comboboxes)
        
    def create_kpi_assignment_tab(self):
        """KPI Assignment tab"""
        assign_frame = ttk.Frame(self.notebook)
        self.notebook.add(assign_frame, text="🎯 Phân Công KPI")
        
        # Top frame for assignment form
        top_frame = ttk.LabelFrame(assign_frame, text="Phân Công KPI cho Cán Bộ", padding="15")
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Assignment form
        assign_form = ttk.Frame(top_frame)
        assign_form.pack(fill=tk.X)
        
        ttk.Label(assign_form, text="Chọn KPI:").grid(row=0, column=0, padx=(0, 5))
        self.assign_kpi_var = tk.StringVar()
        self.assign_kpi_combo = ttk.Combobox(assign_form, textvariable=self.assign_kpi_var, width=30)
        self.assign_kpi_combo.grid(row=0, column=1, padx=(0, 10))
        
        ttk.Label(assign_form, text="Chọn Cán Bộ:").grid(row=0, column=2, padx=(0, 5))
        self.assign_staff_var = tk.StringVar()
        self.assign_staff_combo = ttk.Combobox(assign_form, textvariable=self.assign_staff_var, width=30)
        self.assign_staff_combo.grid(row=0, column=3, padx=(0, 10))
        
        ttk.Label(assign_form, text="Vai Trò:").grid(row=0, column=4, padx=(0, 5))
        self.assign_role_var = tk.StringVar(value="owner")
        assign_role_combo = ttk.Combobox(assign_form, textvariable=self.assign_role_var,
                                       values=["owner", "contributor", "reviewer"], width=15)
        assign_role_combo.grid(row=0, column=5, padx=(0, 10))
        
        ttk.Button(assign_form, text="Phân Công", command=self.assign_kpi).grid(row=0, column=6, padx=(10, 0))
        ttk.Button(assign_form, text="Hủy Phân Công", command=self.unassign_kpi).grid(row=0, column=7, padx=(5, 0))
        
        # Assignment list
        assign_list_frame = ttk.LabelFrame(assign_frame, text="Danh Sách Phân Công KPI", padding="15")
        assign_list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Assignment treeview
        assign_columns = ("KPI", "Tên KPI", "Cán Bộ", "Họ Tên", "Vai Trò", "Ngày Phân Công")
        self.assign_tree = ttk.Treeview(assign_list_frame, columns=assign_columns, show='headings', height=20)
        
        # Configure assignment columns
        assign_widths = [80, 250, 80, 150, 100, 120]
        for col, width in zip(assign_columns, assign_widths):
            self.assign_tree.heading(col, text=col)
            self.assign_tree.column(col, width=width, minwidth=60)
        
        # Assignment scrollbars
        assign_v_scroll = ttk.Scrollbar(assign_list_frame, orient=tk.VERTICAL, command=self.assign_tree.yview)
        self.assign_tree.configure(yscrollcommand=assign_v_scroll.set)
        
        # Pack assignment treeview and scrollbars
        self.assign_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        assign_v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
    def create_kpi_results_tab(self):
        """KPI Results tracking tab"""
        results_frame = ttk.Frame(self.notebook)
        self.notebook.add(results_frame, text="📈 Kết Quả KPI")
        
        # Top frame for results input
        top_frame = ttk.LabelFrame(results_frame, text="Nhập Kết Quả KPI", padding="15")
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Results form
        self.results_vars = {}
        results_fields = [
            ("Chọn KPI:", "kpi_id"),
            ("Kỳ Báo Cáo:", "period"),
            ("Giá Trị Thực Tế:", "actual_value"),
            ("Ghi Chú:", "note")
        ]
        
        for i, (label, var_name) in enumerate(results_fields):
            ttk.Label(top_frame, text=label).grid(row=i//2, column=(i%2)*2, sticky=tk.W, padx=(0, 5), pady=3)
            
            if var_name == "kpi_id":
                self.results_vars[var_name] = tk.StringVar()
                widget = ttk.Combobox(top_frame, textvariable=self.results_vars[var_name], width=30)
                self.results_kpi_combo = widget
            elif var_name == "period":
                self.results_vars[var_name] = tk.StringVar(value=datetime.now().strftime("%Y-%m"))
                widget = ttk.Entry(top_frame, textvariable=self.results_vars[var_name], width=32)
            else:
                self.results_vars[var_name] = tk.StringVar()
                widget = ttk.Entry(top_frame, textvariable=self.results_vars[var_name], width=32)
            
            widget.grid(row=i//2, column=(i%2)*2+1, sticky=(tk.W, tk.E), padx=(0, 20), pady=3)
        
        # Results buttons
        results_btn_frame = ttk.Frame(top_frame)
        results_btn_frame.grid(row=2, column=0, columnspan=4, pady=(15, 0))
        
        ttk.Button(results_btn_frame, text="Lưu Kết Quả", command=self.save_kpi_result).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(results_btn_frame, text="Làm Mới", command=self.clear_results_form).pack(side=tk.LEFT)
        
        # Results list
        results_list_frame = ttk.LabelFrame(results_frame, text="Lịch Sử Kết Quả KPI", padding="15")
        results_list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Filter frame
        filter_frame = ttk.Frame(results_list_frame)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(filter_frame, text="Lọc theo KPI:").grid(row=0, column=0)
        self.results_filter_var = tk.StringVar(value="Tất cả")
        results_filter_combo = ttk.Combobox(filter_frame, textvariable=self.results_filter_var, width=30)
        results_filter_combo.grid(row=0, column=1, padx=(5, 10))
        results_filter_combo.bind('<<ComboboxSelected>>', self.filter_results)
        self.results_filter_combo = results_filter_combo
        
        ttk.Button(filter_frame, text="Làm Mới", command=self.refresh_results_list).grid(row=0, column=2, padx=(10, 0))
        
        # Results treeview
        results_columns = ("KPI", "Tên KPI", "Kỳ", "Mục Tiêu", "Thực Tế", "Đạt (%)", "Ghi Chú", "Ngày Ghi")
        self.results_tree = ttk.Treeview(results_list_frame, columns=results_columns, show='headings', height=20)
        
        # Configure results columns
        results_widths = [80, 200, 80, 100, 100, 80, 150, 120]
        for col, width in zip(results_columns, results_widths):
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=width, minwidth=60)
        
        # Results scrollbars
        results_v_scroll = ttk.Scrollbar(results_list_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=results_v_scroll.set)
        
        # Pack results treeview and scrollbars
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        results_v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
    def create_reports_tab(self):
        """Reports and analytics tab"""
        reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(reports_frame, text="📋 Báo Cáo")
        
        # Initialize reports manager
        self.reports_manager = ReportsManager(reports_frame, self.db)
        
    def create_admin_tab(self):
        """Administration tab"""
        admin_frame = ttk.Frame(self.notebook)
        self.notebook.add(admin_frame, text="⚙️ Quản Trị")
        
        # KPI Categories management
        categories_frame = ttk.LabelFrame(admin_frame, text="Quản Lý Danh Mục KPI", padding="15")
        categories_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Category form
        cat_form_frame = ttk.Frame(categories_frame)
        cat_form_frame.pack(fill=tk.X)
        
        ttk.Label(cat_form_frame, text="Tên Danh Mục:").grid(row=0, column=0, padx=(0, 5))
        self.category_name_var = tk.StringVar()
        ttk.Entry(cat_form_frame, textvariable=self.category_name_var, width=30).grid(row=0, column=1, padx=(0, 10))
        
        ttk.Label(cat_form_frame, text="Mô Tả:").grid(row=0, column=2, padx=(0, 5))
        self.category_desc_var = tk.StringVar()
        ttk.Entry(cat_form_frame, textvariable=self.category_desc_var, width=40).grid(row=0, column=3, padx=(0, 10))
        
        ttk.Button(cat_form_frame, text="Thêm Danh Mục", command=self.add_category).grid(row=0, column=4, padx=(10, 0))
        
        # Categories list
        cat_list_frame = ttk.Frame(categories_frame)
        cat_list_frame.pack(fill=tk.X, pady=(10, 0))
        
        cat_columns = ("ID", "Tên Danh Mục", "Mô Tả", "Ngày Tạo")
        self.category_tree = ttk.Treeview(cat_list_frame, columns=cat_columns, show='headings', height=8)
        
        for col in cat_columns:
            self.category_tree.heading(col, text=col)
            self.category_tree.column(col, width=150, minwidth=100)
        
        cat_v_scroll = ttk.Scrollbar(cat_list_frame, orient=tk.VERTICAL, command=self.category_tree.yview)
        self.category_tree.configure(yscrollcommand=cat_v_scroll.set)
        
        self.category_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cat_v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Database statistics
        stats_frame = ttk.LabelFrame(admin_frame, text="Thống Kê Cơ Sở Dữ Liệu", padding="15")
        stats_frame.pack(fill=tk.BOTH, expand=True)
        
        self.stats_text = tk.Text(stats_frame, wrap=tk.WORD, font=('Consolas', 10), height=15)
        stats_scroll = ttk.Scrollbar(stats_frame, orient=tk.VERTICAL, command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=stats_scroll.set)
        
        self.stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        stats_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Update stats button
        ttk.Button(admin_frame, text="Cập Nhật Thống Kê", command=self.update_database_stats).pack(pady=10)
        
        # Load initial data
        self.refresh_category_list()
        self.update_database_stats()
    
    # KPI Assignment methods
    def assign_kpi(self):
        """Assign KPI to staff"""
        kpi_display = self.assign_kpi_var.get()
        staff_display = self.assign_staff_var.get()
        role = self.assign_role_var.get()
        
        if not kpi_display or not staff_display:
            messagebox.showerror("Lỗi", "Vui lòng chọn KPI và cán bộ!")
            return
        
        # Extract codes from display values
        kpi_code = kpi_display.split(" - ")[0]
        staff_code = staff_display.split(" - ")[0]
        
        # Get IDs
        kpi_id = self.db.execute_query("SELECT id FROM kpi WHERE kpi_code = ?", [kpi_code])[0][0]
        staff_id = self.db.execute_query("SELECT id FROM staff WHERE staff_code = ?", [staff_code])[0][0]
        
        # Check if assignment already exists
        existing = self.db.execute_query(
            "SELECT id FROM kpi_assignments WHERE kpi_id = ? AND staff_id = ?", 
            [kpi_id, staff_id]
        )
        
        if existing:
            messagebox.showerror("Lỗi", "Phân công này đã tồn tại!")
            return
        
        assignment_data = {
            'id': str(uuid.uuid4()),
            'kpi_id': kpi_id,
            'staff_id': staff_id,
            'assigned_date': datetime.now().isoformat(),
            'role': role
        }
        
        try:
            self.db.insert_data('kpi_assignments', assignment_data)
            self.refresh_assignment_list()
            messagebox.showinfo("Thành công", "Đã phân công KPI thành công!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể phân công KPI: {str(e)}")
    
    def unassign_kpi(self):
        """Unassign KPI from staff"""
        selected = self.assign_tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn phân công để hủy!")
            return
        
        kpi_code = self.assign_tree.item(selected[0])['values'][0]
        staff_code = self.assign_tree.item(selected[0])['values'][2]
        
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn hủy phân công này?"):
            try:
                # Get IDs
                kpi_id = self.db.execute_query("SELECT id FROM kpi WHERE kpi_code = ?", [kpi_code])[0][0]
                staff_id = self.db.execute_query("SELECT id FROM staff WHERE staff_code = ?", [staff_code])[0][0]
                
                # Delete assignment
                self.db.execute_query(
                    "DELETE FROM kpi_assignments WHERE kpi_id = ? AND staff_id = ?",
                    [kpi_id, staff_id]
                )
                
                self.refresh_assignment_list()
                messagebox.showinfo("Thành công", "Đã hủy phân công KPI!")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể hủy phân công: {str(e)}")
    
    def refresh_assignment_list(self):
        """Refresh assignment list"""
        for item in self.assign_tree.get_children():
            self.assign_tree.delete(item)
        
        query = """
            SELECT k.kpi_code, k.kpi_name, s.staff_code, s.full_name, ka.role, ka.assigned_date
            FROM kpi_assignments ka
            JOIN kpi k ON ka.kpi_id = k.id
            JOIN staff s ON ka.staff_id = s.id
            ORDER BY ka.assigned_date DESC
        """
        
        results = self.db.execute_query(query)
        
        for row in results:
            # Format date
            assigned_date = datetime.fromisoformat(row[5]).strftime("%d/%m/%Y")
            self.assign_tree.insert("", "end", values=row[:5] + (assigned_date,))
    
    # KPI Results methods
    def save_kpi_result(self):
        """Save KPI result"""
        if not self.validate_results_input():
            return
        
        kpi_display = self.results_vars['kpi_id'].get()
        period = self.results_vars['period'].get()
        actual_value = float(self.results_vars['actual_value'].get())
        note = self.results_vars['note'].get()
        
        # Extract KPI code
        kpi_code = kpi_display.split(" - ")[0]
        kpi_data = self.db.execute_query(
            "SELECT id, target_value FROM kpi WHERE kpi_code = ?", [kpi_code]
        )[0]
        
        kpi_id = kpi_data[0]
        target_value = kpi_data[1] or 1
        
        # Calculate achievement percentage
        achievement_percentage = (actual_value / target_value * 100) if target_value > 0 else 0
        
        result_data = {
            'id': str(uuid.uuid4()),
            'kpi_id': kpi_id,
            'period': period,
            'actual_value': actual_value,
            'achievement_percentage': achievement_percentage,
            'note': note,
            'recorded_by': 'System',
            'recorded_date': datetime.now().isoformat()
        }
        
        try:
            self.db.insert_data('kpi_results', result_data)
            self.refresh_results_list()
            self.clear_results_form()
            messagebox.showinfo("Thành công", "Đã lưu kết quả KPI thành công!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu kết quả: {str(e)}")
    
    def validate_results_input(self):
        """Validate results input"""
        if not self.results_vars['kpi_id'].get():
            messagebox.showerror("Lỗi", "Vui lòng chọn KPI!")
            return False
        if not self.results_vars['actual_value'].get():
            messagebox.showerror("Lỗi", "Vui lòng nhập giá trị thực tế!")
            return False
        try:
            float(self.results_vars['actual_value'].get())
        except ValueError:
            messagebox.showerror("Lỗi", "Giá trị thực tế phải là số!")
            return False
        return True
    
    def clear_results_form(self):
        """Clear results form"""
        for var in self.results_vars.values():
            var.set("")
        self.results_vars['period'].set(datetime.now().strftime("%Y-%m"))
    
    def filter_results(self, event=None):
        """Filter results"""
        self.refresh_results_list()
    
    def refresh_results_list(self):
        """Refresh results list"""
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        query = """
            SELECT k.kpi_code, k.kpi_name, kr.period, k.target_value, kr.actual_value, 
                   kr.achievement_percentage, kr.note, kr.recorded_date
            FROM kpi_results kr
            JOIN kpi k ON kr.kpi_id = k.id
            ORDER BY kr.recorded_date DESC
        """
        
        results = self.db.execute_query(query)
        
        for row in results:
            # Format date and percentage
            recorded_date = datetime.fromisoformat(row[7]).strftime("%d/%m/%Y")
            achievement = f"{row[5]:.1f}%" if row[5] else "0%"
            
            display_row = row[:5] + (achievement, row[6], recorded_date)
            self.results_tree.insert("", "end", values=display_row)
    
    # Category management
    def add_category(self):
        """Add KPI category"""
        category_name = self.category_name_var.get().strip()
        category_desc = self.category_desc_var.get().strip()
        
        if not category_name:
            messagebox.showerror("Lỗi", "Vui lòng nhập tên danh mục!")
            return
        
        category_data = {
            'id': str(uuid.uuid4()),
            'category_name': category_name,
            'description': category_desc,
            'created_date': datetime.now().isoformat()
        }
        
        try:
            self.db.insert_data('kpi_categories', category_data)
            self.refresh_category_list()
            self.update_all_comboboxes()
            self.category_name_var.set("")
            self.category_desc_var.set("")
            messagebox.showinfo("Thành công", "Đã thêm danh mục thành công!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Lỗi", "Tên danh mục đã tồn tại!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thêm danh mục: {str(e)}")
    
    def refresh_category_list(self):
        """Refresh category list"""
        for item in self.category_tree.get_children():
            self.category_tree.delete(item)
        
        categories = self.db.execute_query("SELECT * FROM kpi_categories ORDER BY category_name")
        
        for cat in categories:
            created_date = datetime.fromisoformat(cat[3]).strftime("%d/%m/%Y")
            self.category_tree.insert("", "end", values=(cat[0][:8] + "...", cat[1], cat[2], created_date))
    
    def update_database_stats(self):
        """Update database statistics display"""
        stats = []
        
        # Table counts
        tables = ['departments', 'staff', 'kpi_categories', 'kpi', 'kpi_assignments', 'kpi_results']
        for table in tables:
            count = self.db.execute_query(f"SELECT COUNT(*) FROM {table}")[0][0]
            stats.append(f"{table.upper()}: {count} bản ghi")
        
        # Active counts
        active_depts = self.db.execute_query("SELECT COUNT(*) FROM departments WHERE status = 'active'")[0][0]
        active_staff = self.db.execute_query("SELECT COUNT(*) FROM staff WHERE status = 'active'")[0][0]
        active_kpis = self.db.execute_query("SELECT COUNT(*) FROM kpi WHERE status = 'active'")[0][0]
        
        stats.extend([
            "",
            "TRẠNG THÁI HOẠT ĐỘNG:",
            f"Phòng ban hoạt động: {active_depts}",
            f"Cán bộ hoạt động: {active_staff}",
            f"KPI hoạt động: {active_kpis}"
        ])
        
        # Recent activity
        recent_kpi_results = self.db.execute_query(
            "SELECT COUNT(*) FROM kpi_results WHERE date(recorded_date) >= date('now', '-7 days')"
        )[0][0]
        
        stats.extend([
            "",
            "HOẠT ĐỘNG GẦN ĐÂY:",
            f"Kết quả KPI tuần qua: {recent_kpi_results}",
            f"Cập nhật lần cuối: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        ])
        
        # Display stats
        self.stats_text.delete("1.0", tk.END)
        self.stats_text.insert("1.0", "\n".join(stats))
    
    def update_all_comboboxes(self):
        """Update all comboboxes with current data"""
        # Update department managers
        if hasattr(self, 'dept_manager'):
            # Already handled in department manager
            pass
            
        if hasattr(self, 'staff_manager'):
            self.staff_manager.update_department_comboboxes()
            
        if hasattr(self, 'kpi_manager'):
            self.kpi_manager.update_comboboxes()
        
        # Update KPI assignment comboboxes
        if hasattr(self, 'assign_kpi_combo'):
            kpi_displays = [f"{row[0]} - {row[1]}" for row in self.db.execute_query("SELECT kpi_code, kpi_name FROM kpi WHERE status = 'active' ORDER BY kpi_code")]
            self.assign_kpi_combo['values'] = kpi_displays
            
        if hasattr(self, 'assign_staff_combo'):
            staff_displays = [f"{row[0]} - {row[1]}" for row in self.db.execute_query("SELECT staff_code, full_name FROM staff WHERE status = 'active' ORDER BY staff_code")]
            self.assign_staff_combo['values'] = staff_displays
        
        # Update KPI results comboboxes
        if hasattr(self, 'results_kpi_combo'):
            kpi_displays = [f"{row[0]} - {row[1]}" for row in self.db.execute_query("SELECT kpi_code, kpi_name FROM kpi WHERE status = 'active' ORDER BY kpi_code")]
            self.results_kpi_combo['values'] = kpi_displays
            
        if hasattr(self, 'results_filter_combo'):
            kpi_displays = [f"{row[0]} - {row[1]}" for row in self.db.execute_query("SELECT kpi_code, kpi_name FROM kpi WHERE status = 'active' ORDER BY kpi_code")]
            self.results_filter_combo['values'] = ["Tất cả"] + kpi_displays
        
        # Refresh assignment and results lists
        if hasattr(self, 'assign_tree'):
            self.refresh_assignment_list()
        if hasattr(self, 'results_tree'):
            self.refresh_results_list()

def main():
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()

if __name__ == "__main__":
    main()

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import json
import os
from datetime import datetime


class ReportsManager:
    def __init__(self, parent_frame, db_manager):
        self.parent_frame = parent_frame
        self.db = db_manager
        self.create_widgets()

    def create_widgets(self):
        """Create reports interface"""

        options_frame = ttk.LabelFrame(
            self.parent_frame, text="Tùy Chọn Báo Cáo", padding="15")
        options_frame.pack(fill=tk.X, pady=(0, 10))

        btn_frame1 = ttk.Frame(options_frame)
        btn_frame1.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(btn_frame1, text="Báo Cáo Tổng Quan",
                   command=self.generate_overview_report).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame1, text="Báo Cáo KPI Theo Phòng Ban",
                   command=self.generate_dept_kpi_report).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame1, text="Báo Cáo Hiệu Suất Cán Bộ",
                   command=self.generate_staff_performance_report).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame1, text="Báo Cáo KPI Chi Tiết",
                   command=self.generate_detailed_kpi_report).pack(side=tk.LEFT)

        btn_frame2 = ttk.Frame(options_frame)
        btn_frame2.pack(fill=tk.X)

        ttk.Button(btn_frame2, text="Xuất Dữ Liệu Excel",
                   command=self.export_all_data).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame2, text="Sao Lưu Cơ Sở Dữ Liệu",
                   command=self.backup_database).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame2, text="Khôi Phục Dữ Liệu",
                   command=self.restore_database).pack(side=tk.LEFT)

        display_frame = ttk.LabelFrame(
            self.parent_frame, text="Kết Quả Báo Cáo", padding="15")
        display_frame.pack(fill=tk.BOTH, expand=True)

        self.report_text = tk.Text(
            display_frame, wrap=tk.WORD, font=('Consolas', 10))
        report_scroll = ttk.Scrollbar(
            display_frame, orient=tk.VERTICAL, command=self.report_text.yview)
        self.report_text.configure(yscrollcommand=report_scroll.set)

        self.report_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        report_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def generate_overview_report(self):
        """Generate comprehensive overview report"""

        total_depts = self.db.execute_query(
            "SELECT COUNT(*) FROM departments WHERE status = 'active'")[0][0]
        total_staff = self.db.execute_query(
            "SELECT COUNT(*) FROM staff WHERE status = 'active'")[0][0]
        total_kpis = self.db.execute_query(
            "SELECT COUNT(*) FROM kpi WHERE status = 'active'")[0][0]
        total_assignments = self.db.execute_query(
            "SELECT COUNT(*) FROM kpi_assignments")[0][0]

        dept_stats = self.db.execute_query("""
            SELECT d.dept_name, COUNT(s.id) as staff_count
            FROM departments d
            LEFT JOIN staff s ON d.id = s.department_id AND s.status = 'active'
            WHERE d.status = 'active'
            GROUP BY d.id, d.dept_name
            ORDER BY staff_count DESC
            LIMIT 1
        """)

        top_dept = dept_stats[0] if dept_stats else ("Không có", 0)

        total_results = self.db.execute_query(
            "SELECT COUNT(*) FROM kpi_results")[0][0]
        avg_achievement = self.db.execute_query(
            "SELECT AVG(achievement_percentage) FROM kpi_results"
        )[0][0] or 0

        report = f"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                        BÁO CÁO TỔNG QUAN HỆ THỐNG QUẢN LÝ                                        ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝

📊 THỐNG KÊ TỔNG QUAN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Tổng số phòng ban: {total_depts}
• Tổng số cán bộ: {total_staff}
• Tổng số KPI: {total_kpis}
• Tổng số phân công KPI: {total_assignments}
• Số kết quả KPI đã ghi nhận: {total_results}

🏆 HIỆU SUẤT TỔNG THỂ:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Tỷ lệ đạt KPI trung bình: {avg_achievement:.1f}%
• Phòng ban có nhiều nhân viên nhất: {top_dept[0]} ({top_dept[1]} người)
• Tỷ lệ phân công KPI: {(total_assignments/total_kpis*100) if total_kpis > 0 else 0:.1f}%

📅 Báo cáo được tạo lúc: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """

        self.display_report(report)

    def generate_dept_kpi_report(self):
        """Generate department KPI performance report"""
        dept_kpi_stats = self.db.execute_query("""
            SELECT d.dept_name, 
                   COUNT(DISTINCT k.id) as total_kpis,
                   COUNT(DISTINCT ka.id) as assigned_kpis,
                   COUNT(DISTINCT kr.id) as completed_results,
                   AVG(kr.achievement_percentage) as avg_achievement
            FROM departments d
            LEFT JOIN kpi k ON d.id = k.department_id
            LEFT JOIN kpi_assignments ka ON k.id = ka.kpi_id
            LEFT JOIN kpi_results kr ON k.id = kr.kpi_id
            WHERE d.status = 'active'
            GROUP BY d.id, d.dept_name
            ORDER BY avg_achievement DESC
        """)

        report = f"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                        BÁO CÁO KPI THEO PHÒNG BAN                                                ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝

"""

        for dept in dept_kpi_stats:
            dept_name, total_kpis, assigned_kpis, completed_results, avg_achievement = dept
            avg_achievement = avg_achievement or 0

            report += f"""
🏢 PHÒNG BAN: {dept_name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Tổng số KPI: {total_kpis}
• KPI đã phân công: {assigned_kpis}
• Kết quả đã ghi nhận: {completed_results}
• Tỷ lệ đạt KPI trung bình: {avg_achievement:.1f}%
• Tỷ lệ hoàn thành: {(completed_results/total_kpis*100) if total_kpis > 0 else 0:.1f}%

"""

        report += f"📅 Báo cáo được tạo lúc: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"

        self.display_report(report)

    def generate_staff_performance_report(self):
        """Generate staff performance report"""
        staff_performance = self.db.execute_query("""
            SELECT s.staff_code, s.full_name, d.dept_name, s.position,
                   COUNT(DISTINCT ka.id) as assigned_kpis,
                   COUNT(DISTINCT kr.id) as completed_results,
                   AVG(kr.achievement_percentage) as avg_achievement
            FROM staff s
            JOIN departments d ON s.department_id = d.id
            LEFT JOIN kpi_assignments ka ON s.id = ka.staff_id
            LEFT JOIN kpi k ON ka.kpi_id = k.id
            LEFT JOIN kpi_results kr ON k.id = kr.kpi_id
            WHERE s.status = 'active'
            GROUP BY s.id, s.staff_code, s.full_name, d.dept_name, s.position
            HAVING assigned_kpis > 0
            ORDER BY avg_achievement DESC
        """)

        report = f"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                        BÁO CÁO HIỆU SUẤT CÁN BỘ                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝

👥 HIỆU SUẤT CÁN BỘ THEO KPI:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""

        for staff in staff_performance:
            staff_code, full_name, dept_name, position, assigned_kpis, completed_results, avg_achievement = staff
            avg_achievement = avg_achievement or 0

            report += f"""
👤 {full_name} ({staff_code})
   • Phòng ban: {dept_name}
   • Chức vụ: {position}
   • KPI được phân công: {assigned_kpis}
   • Kết quả đã ghi nhận: {completed_results}
   • Tỷ lệ đạt KPI trung bình: {avg_achievement:.1f}%
   • Tỷ lệ hoàn thành: {(completed_results/assigned_kpis*100) if assigned_kpis > 0 else 0:.1f}%

"""

        report += f"📅 Báo cáo được tạo lúc: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"

        self.display_report(report)

    def generate_detailed_kpi_report(self):
        """Generate detailed KPI report"""
        kpi_details = self.db.execute_query("""
            SELECT k.kpi_code, k.kpi_name, d.dept_name, k.unit, k.target_value, k.weight,
                   COUNT(DISTINCT ka.id) as assigned_count,
                   COUNT(DISTINCT kr.id) as result_count,
                   AVG(kr.achievement_percentage) as avg_achievement,
                   MAX(kr.recorded_date) as last_update
            FROM kpi k
            LEFT JOIN departments d ON k.department_id = d.id
            LEFT JOIN kpi_assignments ka ON k.id = ka.kpi_id
            LEFT JOIN kpi_results kr ON k.id = kr.kpi_id
            WHERE k.status = 'active'
            GROUP BY k.id, k.kpi_code, k.kpi_name, d.dept_name, k.unit, k.target_value, k.weight
            ORDER BY k.kpi_code
        """)

        report = f"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                           BÁO CÁO CHI TIẾT KPI                                                   ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝

📊 CHI TIẾT TỪNG KPI:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""

        for kpi in kpi_details:
            kpi_code, kpi_name, dept_name, unit, target_value, weight, assigned_count, result_count, avg_achievement, last_update = kpi
            avg_achievement = avg_achievement or 0
            last_update_str = datetime.fromisoformat(last_update).strftime(
                "%d/%m/%Y") if last_update else "Chưa có"

            report += f"""
📈 KPI: {kpi_code} - {kpi_name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Phòng ban: {dept_name or 'Không xác định'}
• Đơn vị tính: {unit}
• Giá trị mục tiêu: {target_value} {unit}
• Trọng số: {weight}%
• Số người được phân công: {assigned_count}
• Số kết quả đã ghi nhận: {result_count}
• Tỷ lệ đạt trung bình: {avg_achievement:.1f}%
• Cập nhật lần cuối: {last_update_str}

"""

        report += f"📅 Báo cáo được tạo lúc: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"

        self.display_report(report)

    def display_report(self, report_text):
        """Display report in the text widget"""
        self.report_text.delete("1.0", tk.END)
        self.report_text.insert("1.0", report_text)

    def export_all_data(self):
        """Export all data to Excel-compatible CSV files"""
        export_dir = filedialog.askdirectory(title="Chọn thư mục xuất dữ liệu")
        if not export_dir:
            return

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            dept_data = self.db.execute_query("SELECT * FROM departments")
            dept_file = os.path.join(
                export_dir, f"departments_{timestamp}.csv")
            with open(dept_file, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Mã PB", "Tên PB", "Mô tả", "Trưởng phòng", "SĐT",
                                "Email", "Địa chỉ", "Ngân sách", "Số NV tối đa", "Ngày tạo", "Trạng thái"])
                writer.writerows(dept_data)

            staff_data = self.db.execute_query("""
                SELECT s.*, d.dept_name 
                FROM staff s 
                LEFT JOIN departments d ON s.department_id = d.id
            """)
            staff_file = os.path.join(export_dir, f"staff_{timestamp}.csv")
            with open(staff_file, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Mã CB", "Họ tên", "Ngày sinh", "Giới tính", "CCCD", "SĐT", "Email", "Địa chỉ",
                                "ID PB", "Chức vụ", "Trình độ", "Lương", "Ngày vào làm", "Trạng thái", "Ngày tạo", "Tên phòng ban"])
                writer.writerows(staff_data)

            kpi_data = self.db.execute_query("""
                SELECT k.*, c.category_name, d.dept_name 
                FROM kpi k
                LEFT JOIN kpi_categories c ON k.category_id = c.id
                LEFT JOIN departments d ON k.department_id = d.id
            """)
            kpi_file = os.path.join(export_dir, f"kpi_{timestamp}.csv")
            with open(kpi_file, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Mã KPI", "Tên KPI", "Mô tả", "ID danh mục", "ID phòng ban", "Đơn vị",
                                "Mục tiêu", "Trọng số", "Tần suất", "Ngày tạo", "Trạng thái", "Tên danh mục", "Tên phòng ban"])
                writer.writerows(kpi_data)

            results_data = self.db.execute_query("""
                SELECT kr.*, k.kpi_code, k.kpi_name
                FROM kpi_results kr
                JOIN kpi k ON kr.kpi_id = k.id
            """)
            results_file = os.path.join(
                export_dir, f"kpi_results_{timestamp}.csv")
            with open(results_file, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "ID KPI", "Kỳ", "Giá trị thực tế", "% Đạt",
                                "Ghi chú", "Người ghi", "Ngày ghi", "Mã KPI", "Tên KPI"])
                writer.writerows(results_data)

            messagebox.showinfo(
                "Thành công", f"Đã xuất dữ liệu vào thư mục:\n{export_dir}")

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xuất dữ liệu: {str(e)}")

    def backup_database(self):
        """Backup database to JSON file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Sao lưu cơ sở dữ liệu"
        )

        if filename:
            try:
                backup_data = {
                    'backup_date': datetime.now().isoformat(),
                    'departments': self.db.execute_query("SELECT * FROM departments"),
                    'staff': self.db.execute_query("SELECT * FROM staff"),
                    'kpi_categories': self.db.execute_query("SELECT * FROM kpi_categories"),
                    'kpi': self.db.execute_query("SELECT * FROM kpi"),
                    'kpi_assignments': self.db.execute_query("SELECT * FROM kpi_assignments"),
                    'kpi_results': self.db.execute_query("SELECT * FROM kpi_results")
                }

                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(backup_data, f, ensure_ascii=False, indent=2)

                messagebox.showinfo(
                    "Thành công", f"Đã sao lưu cơ sở dữ liệu vào {filename}")

            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể sao lưu: {str(e)}")

    def restore_database(self):
        """Restore database from JSON file"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Khôi phục cơ sở dữ liệu"
        )

        if filename:
            if messagebox.askyesno("Xác nhận", "Khôi phục sẽ xóa toàn bộ dữ liệu hiện tại. Bạn có chắc chắn?"):
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        backup_data = json.load(f)

                    tables = ['kpi_results', 'kpi_assignments',
                              'kpi', 'kpi_categories', 'staff', 'departments']
                    for table in tables:
                        self.db.execute_query(f"DELETE FROM {table}")

                    for table, data in backup_data.items():
                        if table != 'backup_date' and data:
                            for row in data:
                                placeholders = ', '.join(['?' for _ in row])
                                query = f"INSERT INTO {table} VALUES ({placeholders})"
                                self.db.execute_query(query, row)

                    messagebox.showinfo(
                        "Thành công", "Đã khôi phục cơ sở dữ liệu thành công!")

                except Exception as e:
                    messagebox.showerror(
                        "Lỗi", f"Không thể khôi phục: {str(e)}")

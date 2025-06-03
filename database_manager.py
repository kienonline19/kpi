# database_manager.py
import sqlite3
import uuid
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="management_system.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with all required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Departments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS departments (
                id TEXT PRIMARY KEY,
                dept_code TEXT UNIQUE NOT NULL,
                dept_name TEXT NOT NULL,
                description TEXT,
                manager TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                budget TEXT,
                max_staff INTEGER,
                created_date TEXT,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        # Staff table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS staff (
                id TEXT PRIMARY KEY,
                staff_code TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                birth_date TEXT,
                gender TEXT,
                id_number TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                department_id TEXT,
                position TEXT,
                education TEXT,
                basic_salary TEXT,
                start_date TEXT,
                status TEXT DEFAULT 'active',
                created_date TEXT,
                FOREIGN KEY (department_id) REFERENCES departments (id)
            )
        ''')
        
        # KPI Categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS kpi_categories (
                id TEXT PRIMARY KEY,
                category_name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_date TEXT
            )
        ''')
        
        # KPI table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS kpi (
                id TEXT PRIMARY KEY,
                kpi_code TEXT UNIQUE NOT NULL,
                kpi_name TEXT NOT NULL,
                description TEXT,
                category_id TEXT,
                department_id TEXT,
                unit TEXT,
                target_value REAL,
                weight REAL,
                measurement_frequency TEXT,
                created_date TEXT,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (category_id) REFERENCES kpi_categories (id),
                FOREIGN KEY (department_id) REFERENCES departments (id)
            )
        ''')
        
        # KPI Assignments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS kpi_assignments (
                id TEXT PRIMARY KEY,
                kpi_id TEXT,
                staff_id TEXT,
                assigned_date TEXT,
                role TEXT,
                FOREIGN KEY (kpi_id) REFERENCES kpi (id),
                FOREIGN KEY (staff_id) REFERENCES staff (id)
            )
        ''')
        
        # KPI Results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS kpi_results (
                id TEXT PRIMARY KEY,
                kpi_id TEXT,
                period TEXT,
                actual_value REAL,
                achievement_percentage REAL,
                note TEXT,
                recorded_by TEXT,
                recorded_date TEXT,
                FOREIGN KEY (kpi_id) REFERENCES kpi (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        results = cursor.fetchall()
        conn.commit()
        conn.close()
        return results
    
    def insert_data(self, table, data):
        """Insert data into a table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        cursor.execute(query, list(data.values()))
        conn.commit()
        conn.close()
    
    def update_data(self, table, data, condition):
        """Update data in a table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {condition['column']} = ?"
        
        params = list(data.values()) + [condition['value']]
        cursor.execute(query, params)
        conn.commit()
        conn.close()
    
    def delete_data(self, table, condition):
        """Delete data from a table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = f"DELETE FROM {table} WHERE {condition['column']} = ?"
        cursor.execute(query, [condition['value']])
        conn.commit()
        conn.close()
    
    def load_sample_data(self):
        """Load sample data for demonstration"""
        try:
            # Check if data already exists
            if self.execute_query("SELECT COUNT(*) FROM departments")[0][0] > 0:
                return
            
            # Sample categories
            categories = [
                ('cat1', 'Tài Chính', 'KPI liên quan đến tài chính và ngân sách'),
                ('cat2', 'Kinh Doanh', 'KPI liên quan đến bán hàng và khách hàng'),
                ('cat3', 'Nhân Sự', 'KPI liên quan đến quản lý nhân sự'),
                ('cat4', 'Chất Lượng', 'KPI liên quan đến chất lượng sản phẩm/dịch vụ')
            ]
            
            for cat_id, name, desc in categories:
                self.insert_data('kpi_categories', {
                    'id': cat_id,
                    'category_name': name,
                    'description': desc,
                    'created_date': datetime.now().isoformat()
                })
            
            # Sample departments
            departments = [
                ('dept1', 'PB001', 'Phòng Tài Chính', 'Quản lý tài chính và kế toán', 'Nguyễn Thị Lan', '024-3844-1234', 'taichinh@company.com', 'Tầng 3', '500000000', 8),
                ('dept2', 'PB002', 'Phòng Kinh Doanh', 'Phát triển kinh doanh và marketing', 'Trần Văn Minh', '024-3844-1235', 'kinhdoanh@company.com', 'Tầng 4', '800000000', 12),
                ('dept3', 'PB003', 'Phòng Nhân Sự', 'Quản lý nhân sự và đào tạo', 'Lê Thị Hoa', '024-3844-1236', 'nhansu@company.com', 'Tầng 2', '300000000', 6)
            ]
            
            for dept_id, code, name, desc, manager, phone, email, address, budget, max_staff in departments:
                self.insert_data('departments', {
                    'id': dept_id,
                    'dept_code': code,
                    'dept_name': name,
                    'description': desc,
                    'manager': manager,
                    'phone': phone,
                    'email': email,
                    'address': address,
                    'budget': budget,
                    'max_staff': max_staff,
                    'created_date': datetime.now().isoformat(),
                    'status': 'active'
                })
            
            # Sample staff
            staff_data = [
                ('staff1', 'NV001', 'Nguyễn Văn An', '1985-03-15', 'Nam', '123456789012', '0912345678', 'an.nguyen@company.com', '123 Đường ABC', 'dept1', 'Chuyên viên', 'Đại học', '15000000', '2020-01-15'),
                ('staff2', 'NV002', 'Trần Thị Bình', '1990-07-22', 'Nữ', '123456789013', '0912345679', 'binh.tran@company.com', '456 Đường DEF', 'dept2', 'Trưởng phòng', 'Thạc sĩ', '25000000', '2019-06-01'),
                ('staff3', 'NV003', 'Lê Văn Cường', '1988-11-08', 'Nam', '123456789014', '0912345680', 'cuong.le@company.com', '789 Đường GHI', 'dept3', 'Phó trưởng phòng', 'Đại học', '20000000', '2021-03-01')
            ]
            
            for staff_id, code, name, birth, gender, id_num, phone, email, address, dept_id, position, education, salary, start_date in staff_data:
                self.insert_data('staff', {
                    'id': staff_id,
                    'staff_code': code,
                    'full_name': name,
                    'birth_date': birth,
                    'gender': gender,
                    'id_number': id_num,
                    'phone': phone,
                    'email': email,
                    'address': address,
                    'department_id': dept_id,
                    'position': position,
                    'education': education,
                    'basic_salary': salary,
                    'start_date': start_date,
                    'status': 'active',
                    'created_date': datetime.now().isoformat()
                })
            
            # Sample KPIs
            kpi_data = [
                ('kpi1', 'KPI001', 'Doanh Thu Hàng Tháng', 'cat2', 'dept2', 'VND', 100000000, 30, 'Hàng tháng'),
                ('kpi2', 'KPI002', 'Tỷ Lệ Hài Lòng Khách Hàng', 'cat4', 'dept2', '%', 90, 25, 'Hàng quý'),
                ('kpi3', 'KPI003', 'Chi Phí Vận Hành', 'cat1', 'dept1', 'VND', 50000000, 20, 'Hàng tháng'),
                ('kpi4', 'KPI004', 'Tỷ Lệ Nhân Viên Được Đào Tạo', 'cat3', 'dept3', '%', 80, 15, 'Hàng quý')
            ]
            
            for kpi_id, code, name, cat_id, dept_id, unit, target, weight, freq in kpi_data:
                self.insert_data('kpi', {
                    'id': kpi_id,
                    'kpi_code': code,
                    'kpi_name': name,
                    'description': f'Mô tả cho {name}',
                    'category_id': cat_id,
                    'department_id': dept_id,
                    'unit': unit,
                    'target_value': target,
                    'weight': weight,
                    'measurement_frequency': freq,
                    'created_date': datetime.now().isoformat(),
                    'status': 'active'
                })
            
            # Sample KPI assignments
            assignments = [
                ('assign1', 'kpi1', 'staff2', 'owner'),
                ('assign2', 'kpi2', 'staff2', 'owner'),
                ('assign3', 'kpi3', 'staff1', 'owner'),
                ('assign4', 'kpi4', 'staff3', 'owner')
            ]
            
            for assign_id, kpi_id, staff_id, role in assignments:
                self.insert_data('kpi_assignments', {
                    'id': assign_id,
                    'kpi_id': kpi_id,
                    'staff_id': staff_id,
                    'assigned_date': datetime.now().isoformat(),
                    'role': role
                })
            
            # Sample results
            results = [
                ('result1', 'kpi1', '2024-01', 95000000, 95.0, 'Đạt mục tiêu tháng 1'),
                ('result2', 'kpi1', '2024-02', 105000000, 105.0, 'Vượt mục tiêu tháng 2'),
                ('result3', 'kpi2', '2024-Q1', 92, 102.2, 'Khách hàng rất hài lòng'),
                ('result4', 'kpi3', '2024-01', 48000000, 96.0, 'Tiết kiệm chi phí tốt')
            ]
            
            for result_id, kpi_id, period, actual, achievement, note in results:
                self.insert_data('kpi_results', {
                    'id': result_id,
                    'kpi_id': kpi_id,
                    'period': period,
                    'actual_value': actual,
                    'achievement_percentage': achievement,
                    'note': note,
                    'recorded_by': 'System',
                    'recorded_date': datetime.now().isoformat()
                })
                
        except Exception as e:
            print(f"Error loading sample data: {str(e)}")

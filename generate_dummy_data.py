"""Standalone dummy data generation script."""

import os
import sys
sys.path.insert(0, '/home/runner/work/TEP/TEP')

from datetime import date, datetime, timezone, timedelta

def generate_dummy_data():
    """Generate dummy data for development environment."""
    from src.config import Settings
    from src.database import engine
    from sqlalchemy import text
    
    settings = Settings()
    if settings.ENVIRONMENT.lower() != "development":
        print("Not in development environment, skipping dummy data generation")
        return
    
    print("Generating dummy data for development environment...")
    
    try:
        with engine.connect() as conn:
            trans = conn.begin()
            
            try:
                # Insert basic org units (beyond root which is id=0)
                conn.execute(text("""
                    INSERT OR IGNORE INTO org_units (id, name) VALUES 
                    (1, 'Engineering'),
                    (2, 'Sales'), 
                    (3, 'Marketing')
                """))
                
                # Insert departments
                conn.execute(text("""
                    INSERT OR IGNORE INTO departments (id, name) VALUES
                    (1, 'Backend Development'),
                    (2, 'Sales Team')
                """))
                
                # Insert holiday groups
                conn.execute(text("""
                    INSERT OR IGNORE INTO holiday_groups (id, name) VALUES
                    (1, 'US Holidays')
                """))
                
                # Insert holidays
                conn.execute(text("""
                    INSERT OR IGNORE INTO holidays (name, start_date, end_date, holiday_group_id) VALUES
                    ('New Year''s Day', '2024-01-01', '2024-01-01', 1),
                    ('Independence Day', '2024-07-04', '2024-07-04', 1)
                """))
                
                # Insert sample employees (beyond root employee id=0)
                today = date.today().isoformat()
                conn.execute(text(f"""
                    INSERT OR IGNORE INTO employees (id, badge_number, first_name, last_name, payroll_type, payroll_sync, workweek_type, time_type, allow_clocking, allow_delete, org_unit_id, manager_id, holiday_group_id) VALUES
                    (1, 'EMP001', 'John', 'Doe', 'salary', '{today}', 'standard', 1, 1, 1, 1, NULL, 1),
                    (2, 'EMP002', 'Jane', 'Smith', 'hourly', '{today}', 'standard', 1, 1, 1, 2, 1, 1)
                """))
                
                # Simple password hash for demo (in real app would import bcrypt)
                # Using a pre-computed hash for 'password123'
                hashed_pw = '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW'
                
                # Insert sample users (beyond root user id=0)
                conn.execute(text("""
                    INSERT OR IGNORE INTO users (id, badge_number, password) VALUES
                    (1, 'EMP001', :password),
                    (2, 'EMP002', :password)
                """), {"password": hashed_pw})
                
                # Insert auth roles (beyond root role id=0)
                conn.execute(text("""
                    INSERT OR IGNORE INTO auth_roles (id, name) VALUES
                    (1, 'Employee'),
                    (2, 'Manager')
                """))
                
                # Insert basic permissions
                conn.execute(text("""
                    INSERT OR IGNORE INTO auth_role_permissions (resource, auth_role_id) VALUES
                    ('employee.read', 1),
                    ('timeclock.create', 1),
                    ('employee.read', 2),
                    ('employee.update', 2)
                """))
                
                # Insert role memberships
                conn.execute(text("""
                    INSERT OR IGNORE INTO auth_role_memberships (auth_role_id, user_id) VALUES
                    (1, 2),  -- Jane is Employee
                    (2, 1)   -- John is Manager
                """))
                
                # Insert department memberships
                conn.execute(text("""
                    INSERT OR IGNORE INTO department_memberships (department_id, employee_id) VALUES
                    (1, 1),  -- John in Backend
                    (1, 2)   -- Jane in Backend
                """))
                
                # Insert a sample timeclock entry
                clock_time = (datetime.now(timezone.utc) - timedelta(hours=8)).isoformat()
                conn.execute(text(f"""
                    INSERT OR IGNORE INTO timeclock (badge_number, clock_in) VALUES
                    ('EMP001', '{clock_time}')
                """))
                
                trans.commit()
                print("Dummy data generation completed successfully!")
                print(f"Database: {settings.get_database_url()}")
                return True
                
            except Exception as e:
                trans.rollback()
                print(f"Error generating dummy data: {e}")
                return False
                
    except Exception as e:
        print(f"Database connection error: {e}")
        return False

if __name__ == "__main__":
    success = generate_dummy_data()
    if success:
        # Let's verify some of the data was inserted
        from src.database import engine
        from sqlalchemy import text
        
        print("\nVerifying dummy data:")
        with engine.connect() as conn:
            # Check org units
            result = conn.execute(text("SELECT COUNT(*) FROM org_units WHERE id > 0"))
            print(f"Org units created: {result.scalar()}")
            
            # Check employees
            result = conn.execute(text("SELECT COUNT(*) FROM employees WHERE id > 0"))
            print(f"Employees created: {result.scalar()}")
            
            # Check users
            result = conn.execute(text("SELECT COUNT(*) FROM users WHERE id > 0"))
            print(f"Users created: {result.scalar()}")
            
            # List some data
            print("\nSample employees:")
            result = conn.execute(text("SELECT badge_number, first_name, last_name FROM employees WHERE id > 0"))
            for row in result:
                print(f"  - {row[0]}: {row[1]} {row[2]}")
    else:
        sys.exit(1)
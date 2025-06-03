from __init__ import CURSOR, CONN


class Employee:
    # Dictionary of objects saved to the database
    all = {}

    def __init__(self, name, job_title, department_id=None, id=None):
        self.id = id
        self.name = name
        self.job_title = job_title
        self.department_id = department_id

    def __repr__(self):
        return f"<Employee {self.id}: {self.name}, {self.job_title}, Department {self.department_id}>"

    @classmethod
    def create_table(cls):
        """Create the employees table with foreign key to departments"""
        sql = """
            CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT,
            job_title TEXT,
            department_id INTEGER,
            FOREIGN KEY (department_id) REFERENCES departments(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """Drop the employees table"""
        sql = "DROP TABLE IF EXISTS employees"
        CURSOR.execute(sql)
        CONN.commit()
        cls.all.clear()

    def save(self):
        """Save the employee to the database (insert or update)"""
        if self.id is None:
            # Insert new record
            sql = """
                INSERT INTO employees (name, job_title, department_id)
                VALUES (?, ?, ?)
            """
            params = (self.name, self.job_title, self.department_id)
            CURSOR.execute(sql, params)
            CONN.commit()
            self.id = CURSOR.lastrowid
            type(self).all[self.id] = self
        else:
            # Update existing record
            self.update()

    def update(self):
        """Update the employee's database record"""
        sql = """
            UPDATE employees
            SET name = ?, job_title = ?, department_id = ?
            WHERE id = ?
        """
        params = (self.name, self.job_title, self.department_id, self.id)
        CURSOR.execute(sql, params)
        CONN.commit()
        type(self).all[self.id] = self

    def delete(self):
        """Delete the employee's database record"""
        sql = "DELETE FROM employees WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        del type(self).all[self.id]
        self.id = None

    @classmethod
    def create(cls, name, job_title, department_id=None):
        """Create and save a new employee"""
        employee = cls(name, job_title, department_id)
        employee.save()
        return employee

    @classmethod
    def instance_from_db(cls, row):
        """Create an Employee instance from a database row"""
        employee = cls.all.get(row[0])
        if employee:
            employee.name = row[1]
            employee.job_title = row[2]
            employee.department_id = row[3]
        else:
            employee = cls(row[1], row[2], row[3], row[0])
            cls.all[employee.id] = employee
        return employee

    @classmethod
    def get_all(cls):
        """Get all employees from the database"""
        sql = "SELECT * FROM employees"
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @classmethod
    def find_by_id(cls, id):
        """Find an employee by ID"""
        sql = "SELECT * FROM employees WHERE id = ?"
        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row) if row else None

    @classmethod
    def find_by_name(cls, name):
        """Return an Employee object corresponding to first table row matching specified name"""
        sql = """
            SELECT *
            FROM employees
            WHERE name = ?
        """

        row = CURSOR.execute(sql, (name,)).fetchone()
        return cls.instance_from_db(row) if row else None

    def get_department(self):
        """Get the department this employee belongs to"""
        from department import Department  # Import here to avoid circular imports

        if self.department_id:
            return Department.find_by_id(self.department_id)
        return None

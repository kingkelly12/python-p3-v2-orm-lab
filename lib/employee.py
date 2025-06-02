from __init__ import CONN, CURSOR

class Employee:
    all = {}

    def __init__(self, name, job_title, department_id, id=None):
        self.id = id
        self.name = name  # This will use the name setter
        self.job_title = job_title
        self.department_id = department_id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise ValueError("Name must be a string")
        if len(value) < 1:
            raise ValueError("Name cannot be empty")
        self._name = value

    def __repr__(self):
        return f"<Employee {self.id}: {self.name}, {self.job_title}, Department ID: {self.department_id}>"
    
    @property
    def job_title(self):
        return self._job_title
    
    @job_title.setter
    def job_title(self, value):
        if not isinstance(value, str):
            raise ValueError("Job title must be a string")
        if len(value) == 0:
            raise ValueError("Job title cannot be empty")
        self._job_title = value
        
    def __str__(self):
        return f"{self.name} - {self.job_title} (Department ID: {self.department_id})"
    
    @property
    def department(self):
        return self._department
    
    @department.setter
    def department(self, value):
        if not isinstance(value, department):  # Assuming Department is the class
            raise ValueError("Department must be a Department instance")
        self._department = value

    @classmethod
    def create_table(cls):
        sql = """
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY,
                name TEXT,
                job_title TEXT,
                department_id INTEGER,
                FOREIGN KEY (department_id) REFERENCES departments(id)
            )
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        sql = """
            DROP TABLE IF EXISTS employees;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        if self.id is None:
            sql = """
                INSERT INTO employees (name, job_title, department_id)
                VALUES (?, ?, ?)
            """
            CURSOR.execute(sql, (self.name, self.job_title, self.department_id))
            CONN.commit()
            self.id = CURSOR.lastrowid
            Employee.all[self.id] = self
        else:
            self.update()

    @classmethod
    def create(cls, name, job_title, department_id):
        employee = cls(name, job_title, department_id)
        employee.save()
        return employee

    @classmethod
    def instance_from_db(cls, row):
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
    def find_by_id(cls, id):
        sql = """
            SELECT *
            FROM employees
            WHERE id = ?
        """
        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row) if row else None

    @classmethod
    def find_by_name(cls, name):
        sql = """
            SELECT *
            FROM employees
            WHERE name = ?
            LIMIT 1
        """
        row = CURSOR.execute(sql, (name,)).fetchone()
        return cls.instance_from_db(row) if row else None

    def update(self):
        sql = """
            UPDATE employees
            SET name = ?, job_title = ?, department_id = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.name, self.job_title, self.department_id, self.id))
        CONN.commit()

    def delete(self):
        sql = """
            DELETE FROM employees
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        del Employee.all[self.id]
        self.id = None

    @classmethod
    def get_all(cls):
        sql = """
            SELECT *
            FROM employees
        """
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]

    def reviews(self):
        """Get all reviews for this employee"""
        from review import Review
        sql = """
            SELECT *
            FROM reviews
            WHERE employee_id = ?
        """
        rows = CURSOR.execute(sql, (self.id,)).fetchall()
        return [Review.instance_from_db(row) for row in rows]

    def get_department(self):
        """Get the department this employee belongs to"""
        from department import Department
        return Department.find_by_id(self.department_id)
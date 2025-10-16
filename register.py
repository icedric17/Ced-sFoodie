import sys
from mysql.connector import Error
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton,
    QMessageBox, QLabel
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
from db import kuha_databse


class Register(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Register")
        self.setGeometry(0, 0, 1920, 1080)
        self.setStyleSheet("background-color: #4A0E13; color: white;")
        self.setWindowIcon(QIcon('Logo (2).png'))
        self.showMaximized()

        # === Parent Layout ===
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # === Container ===
        container = QWidget()
        container.setFixedSize(600, 700)
        container.setStyleSheet("""
            QWidget {
                background-color: ##E53935;
                border-radius: 15px;
                padding: 30px;
            }
        """)

        layout = QVBoxLayout(container)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # === Title ===
        title = QLabel("Create an Account")
        title.setFont(QFont("Arial", 26, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # === Input Fields ===
        self.username_input = self.create_input("Enter Username")
        layout.addWidget(self.username_input)

        self.fullname_input = self.create_input("Enter Full Name")
        layout.addWidget(self.fullname_input)

        self.email_input = self.create_input("Enter Email")
        layout.addWidget(self.email_input)

        self.phone_input = self.create_input("Enter Phone Number")
        layout.addWidget(self.phone_input)

        self.address_input = self.create_input("Enter Address")
        layout.addWidget(self.address_input)

        self.password_input = self.create_input("Enter Password", is_password=True)
        layout.addWidget(self.password_input)

        self.confirm_input = self.create_input("Confirm Password", is_password=True)
        layout.addWidget(self.confirm_input)

        # === Register Button ===
        register_btn = QPushButton("Register")
        register_btn.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        register_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        register_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFCC00;
                color: white;
                border-radius: 10px;
                padding: 10px;
                margin-top: 15px;
            }
            QPushButton:hover {
                background-color: #FFFF00;
            }
        """)
        register_btn.clicked.connect(self.register_user)
        layout.addWidget(register_btn)

        # === Back to Login Button ===
        back_btn = QPushButton("Back to Login")
        back_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border-radius: 10px;
                padding: 10px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #e53935;
            }
        """)
        back_btn.clicked.connect(self.back_to_login)
        layout.addWidget(back_btn)

        main_layout.addWidget(container)
        self.setLayout(main_layout)

    # === Input field factory ===
    def create_input(self, placeholder, is_password=False):
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        input_field.setFont(QFont("Arial", 14))
        input_field.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border-radius: 10px;
                background-color: white;
                color: black;
                margin-top: 10px;
            }
        """)
        if is_password:
            input_field.setEchoMode(QLineEdit.EchoMode.Password)
        return input_field

    # === Registration logic ===
    def register_user(self):
        username = self.username_input.text().strip()
        fullname = self.fullname_input.text().strip()
        email = self.email_input.text().strip()
        phone = self.phone_input.text().strip()
        address = self.address_input.text().strip()
        password = self.password_input.text().strip()
        confirm = self.confirm_input.text().strip()

        # --- Basic validation ---
        if not all([username, fullname, email, phone, address, password, confirm]):
            QMessageBox.warning(self, "Error", "Please fill in all fields.")
            return

        if password != confirm:
            QMessageBox.warning(self, "Error", "Passwords do not match.")
            return

        connection = None
        try:
            connection = kuha_databse()
            cursor = connection.cursor()

            # Check duplicate username or email
            cursor.execute("SELECT * FROM accounts WHERE username = %s", (username,))
            if cursor.fetchone():
                QMessageBox.warning(self, "Error", "Username already exists.")
                return

            cursor.execute("SELECT * FROM customers WHERE email = %s", (email,))
            if cursor.fetchone():
                QMessageBox.warning(self, "Error", "Email already registered.")
                return

            # Insert into accounts table (default role: customer)
            insert_account = "INSERT INTO accounts (username, password, role) VALUES (%s, %s, %s)"
            cursor.execute(insert_account, (username, password, "customer"))
            account_id = cursor.lastrowid

            # Insert into customers table
            insert_customer = """
                INSERT INTO customers (account_id, name, email, phone, address)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(insert_customer, (account_id, fullname, email, phone, address))
            connection.commit()

            QMessageBox.information(self, "Success", "Account registered successfully!")
            self.clear_fields()
            self.back_to_login()

        except Error as e:
            QMessageBox.critical(self, "Database Error", f"Error: {e}")
        finally:
            if connection and connection.is_connected():
                connection.close()

    # === Clear inputs ===
    def clear_fields(self):
        for field in [
            self.username_input, self.fullname_input, self.email_input,
            self.phone_input, self.address_input, self.password_input, self.confirm_input
        ]:
            field.clear()

    # === Back to login page ===
    def back_to_login(self):
        from login import Login
        self.hide()
        self.login_window = Login()
        self.login_window.showMaximized()

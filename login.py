import sys
from mysql.connector import Error
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton,
    QMessageBox, QLabel, QHBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
from db import kuha_databse  # <-- your database connection file


class Login(QWidget):
    def __init__(self, user_data=None):
        self.user_data = user_data
        super().__init__()
        self.setWindowTitle("Login")
        self.setGeometry(0, 0, 1920, 1080)
        self.setStyleSheet("background-color: #4A0E13; color: white;")
        self.setWindowIcon(QIcon('Logo (2).png'))
        self.showMaximized()
        
        # --- Outer layout ---
        outer_layout = QHBoxLayout()
        outer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # --- Container ---
        self.container = QWidget()
        self.container.setFixedSize(500, 450)
        self.container.setStyleSheet("""
            background-color: #E53935;
            border-radius: 15px;
            border: 2px solid #333;
        """)

        # --- Inner layout ---
        inner_layout = QVBoxLayout()
        inner_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        inner_layout.setContentsMargins(40, 40, 40, 40)
        inner_layout.setSpacing(20)

        # --- Title ---
        title = QLabel("Login")
        title.setFont(QFont("Arial", 30, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        inner_layout.addWidget(title)

        # --- Username ---
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        self.username_input.setFont(QFont("Arial", 14))
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border-radius: 10px;
                background-color: white;
                color: black;
            }
        """)
        inner_layout.addWidget(self.username_input)

        # --- Password ---
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setFont(QFont("Arial", 14))
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border-radius: 10px;
                background-color: white;
                color: black;
            }
        """)
        inner_layout.addWidget(self.password_input)

        # --- Login Button ---
        login_btn = QPushButton("Login")
        login_btn.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFB400;
                color: white;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #F9A602;
            }
        """)
        login_btn.clicked.connect(self.check_login)
        inner_layout.addWidget(login_btn)

        # --- Register Button ---
        register_btn = QPushButton("Create an Account")
        register_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        register_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        register_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF6600;
                color: white;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #FF6633;
            }
        """)
        register_btn.clicked.connect(self.open_register_page)
        inner_layout.addWidget(register_btn)

        # --- Final layout setup ---
        self.container.setLayout(inner_layout)
        outer_layout.addWidget(self.container)
        self.setLayout(outer_layout)

    # --- Open Register Page ---
    def open_register_page(self):
        from register import Register
        self.hide()
        self.register_window = Register()
        self.register_window.showMaximized()

    # --- Check Login ---
    def check_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Please fill in all fields.")
            return

        connection = None
        try:
            connection = kuha_databse()
            cursor = connection.cursor(dictionary=True)

            query = """
                SELECT a.ID, a.role, c.customer_id, c.name AS Fullname, c.email, c.phone, c.address
                FROM accounts a
                LEFT JOIN customers c
                ON a.ID = c.account_id
                WHERE username = %s AND password = %s
            """
            cursor.execute(query, (username, password))
            user = cursor.fetchone()
        
            if user:
                role = user["role"].lower()
                QMessageBox.information(self, "Login Successful", f"Welcome, {username} ({role})!")

                if role == "admin":
                    self.open_admin_page(user)
                else:
                    self.open_user_home(user)
            else:
                QMessageBox.warning(self, "Login Failed", "Invalid username or password.")

        except Error as e:
            QMessageBox.critical(self, "Database Error", f"Error: {e}")
        finally:
            if connection and connection.is_connected():
                connection.close()

    # --- Open User Home Page ---
    def open_user_home(self, user_data):
        from user_home import CustomerHomePage
        self.home = CustomerHomePage(user_data)
        self.home.showMaximized()
        self.close()

    # --- Open Admin Page ---
    def open_admin_page(self, user_data):
        from AdminDashboard import AdminDashboard
        self.admin = AdminDashboard(user_data)
        self.admin.showMaximized()
        self.close()


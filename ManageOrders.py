import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFrame,
    QTableWidget, QTableWidgetItem, QApplication, QMessageBox, QHeaderView
)
from PyQt6.QtGui import QFont, QIcon, QPixmap
from PyQt6.QtCore import Qt
import mysql.connector
from db import kuha_databse


class ManageOrders(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.setWindowTitle("Manage Orders")
        self.setGeometry(0, 0, 1920, 1080)
        self.showMaximized()
        self.setStyleSheet("background-color: #121212; color: white;")
        self.setWindowIcon(QIcon('Logo (2).png'))

        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(0)

        # === Sidebar ===
        sidebar_container = QWidget()
        sidebar_container.setStyleSheet("background-color: #1E1E1E;")
        sidebar_container.setFixedWidth(600)
        sidebar = QVBoxLayout(sidebar_container)
        sidebar.setSpacing(25)
        sidebar.setContentsMargins(40, 40, 40, 40)

        # Logo
        logo = QLabel()
        pixmap = QPixmap("Logo (2).png")
        pixmap = pixmap.scaled(210, 190, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar.addWidget(logo)


        base_btn = """
            QPushButton {
                background-color: #2C2C2C;
                color: #E0E0E0;
                font-size: 20px;
                padding: 20px;
                border-radius: 12px;
                font-weight: bold;
                min-width: 250px;
                min-height: 80px;
            }
            QPushButton:hover {
                background-color: #3D3D3D;
            }
        """
        active_btn = """
            QPushButton {
                background-color: #3A3A3A;
                color: white;
                font-size: 20px;
                padding: 20px;
                border-radius: 12px;
                font-weight: bold;
                min-width: 250px;
                min-height: 80px;
            }
            QPushButton:hover {
                background-color: #4A4A4A;
            }
        """

        logout_btn_n = """
            QPushButton {
                background-color: red;
                color: white;
                font-size: 20px;
                padding: 20px;
                border-radius: 12px;
                font-weight: bold;
                min-width: 250px;
                min-height: 80px;
            }
            QPushButton:hover {
                background-color: dark-red;
            }
        """

        dashboard_btn = QPushButton("📊 Dashboard")
        dashboard_btn.setStyleSheet(base_btn)
        dashboard_btn.clicked.connect(self.open_dashboard)
        sidebar.addWidget(dashboard_btn)

        manage_orders_btn = QPushButton("🛒 Manage Orders")
        manage_orders_btn.setStyleSheet(active_btn)
        sidebar.addWidget(manage_orders_btn)

        manage_menu_btn = QPushButton("📋 Manage Menu")
        manage_menu_btn.setStyleSheet(base_btn)
        manage_menu_btn.clicked.connect(self.open_manage_menu)
        sidebar.addWidget(manage_menu_btn)

        manage_users_btn = QPushButton("👥 Manage Users")
        manage_users_btn.setStyleSheet(base_btn)
        sidebar.addWidget(manage_users_btn)

        logout_btn = QPushButton("🚪 Logout")
        logout_btn.setStyleSheet(logout_btn_n)
        logout_btn.clicked.connect(self.logout)
        sidebar.addWidget(logout_btn)

        sidebar.addStretch()
        main_layout.addWidget(sidebar_container)

        # === Main Content Area ===
        content_area = QFrame()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(50, 50, 50, 50)

        title = QLabel("Manage Customer Orders")
        title.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: white;")
        content_layout.addWidget(title)

        # === Orders Table ===
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(6)
        self.orders_table.setHorizontalHeaderLabels(["Order ID", "Customer", "Order Date", "Status", "Total (₱)", "Actions"])
        self.orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.orders_table.setStyleSheet("""
            QTableWidget {
                background-color: #1E1E1E;
                color: white;
                font-size: 16px;
                border: none;
            }
            QHeaderView::section {
                background-color: #2C2C2C;
                color: white;
                font-weight: bold;
                padding: 10px;
            }
        """)
        content_layout.addWidget(self.orders_table)

        # Load data
        self.load_orders()

        main_layout.addWidget(content_area)

    def load_orders(self):
        """Fetch and display all orders"""
        try:
            db = kuha_databse()
            cursor = db.cursor()

            query = """
                SELECT o.order_id, c.name, o.order_date, o.status, o.total_amount
                FROM orders o
                LEFT JOIN customers c ON o.customer_id = c.customer_id
                ORDER BY o.order_date DESC
            """
            cursor.execute(query)
            results = cursor.fetchall()

            self.orders_table.setRowCount(0)
            for row_idx, row_data in enumerate(results):
                self.orders_table.insertRow(row_idx)
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.orders_table.setItem(row_idx, col_idx, item)

                # Add Update Button
                update_btn = QPushButton("Update Status")
                update_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        font-weight: bold;
                        border-radius: 8px;
                        padding: 8px;
                    }
                    QPushButton:hover {
                        background-color: #45A049;
                    }
                """)
                update_btn.clicked.connect(lambda _, order_id=row_data[0], status=row_data[3]: self.update_status(order_id, status))
                self.orders_table.setCellWidget(row_idx, 5, update_btn)

            cursor.close()
            db.close()

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Database Error", f"Error loading orders: {err}")

    def update_status(self, order_id, current_status):
        """Cycle through Pending → Preparing → Completed"""
        next_status = {
            "Pending": "Preparing",
            "Preparing": "Completed",
            "Completed": "Completed",
            "Cancelled": "Cancelled"
        }.get(current_status, "Pending")

        try:
            db = kuha_databse()
            cursor = db.cursor()
            cursor.execute("UPDATE orders SET status = %s WHERE order_id = %s", (next_status, order_id))
            db.commit()
            cursor.close()
            db.close()

            QMessageBox.information(self, "Success", f"Order #{order_id} updated to '{next_status}'.")
            self.load_orders()

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error", f"Failed to update order: {err}")

    def logout(self):
        from login import Login
        self.login = Login()
        self.login.showMaximized()
        self.close()

    def open_dashboard(self):
        from AdminDashboard import AdminDashboard
        self.dashboard = AdminDashboard(self.user_data)
        self.dashboard.showMaximized()
        self.close()
    
    def open_manage_menu(self):
        from ManageMenu import ManageMenu
        self.manage_menu = ManageMenu(self.user_data)
        self.manage_menu.showMaximized()
        self.close()

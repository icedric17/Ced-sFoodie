import sys
from mysql.connector import Error
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QMessageBox
)
from PyQt6.QtGui import QFont, QPixmap, QIcon, QCursor
from PyQt6.QtCore import Qt
from db import kuha_databse


class CustomerOrders(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.setWindowTitle("My Orders - Food Ordering System")
        self.setGeometry(0, 0, 1920, 1080)
        self.showMaximized()
        self.setWindowIcon(QIcon('Logo (2).png'))
        self.setStyleSheet("background-color: #121212; color: white;")

        # --- Main Layout ---
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(0)

        # === Sidebar ===
        sidebar_container = QWidget()
        sidebar_container.setStyleSheet("background-color: #1E1E1E;")
        sidebar = QVBoxLayout(sidebar_container)
        sidebar.setSpacing(25)
        sidebar.setContentsMargins(40, 40, 40, 40)

        # Logo
        logo = QLabel()
        pixmap = QPixmap("Logo (2).png")
        pixmap = pixmap.scaled(210, 190, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Button Styles
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
        logout_btn = """
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

        # Sidebar Buttons
        self.home_btn = QPushButton("Home")
        self.home_btn.setStyleSheet(base_btn)
        self.home_btn.clicked.connect(self.open_home)

        self.pos_btn = QPushButton("POS")
        self.pos_btn.setStyleSheet(base_btn)
        self.pos_btn.clicked.connect(self.open_pos)

        self.orders_btn = QPushButton("Orders")
        self.orders_btn.setStyleSheet(active_btn)

        self.logout_btn = QPushButton("Logout")
        self.logout_btn.setStyleSheet(logout_btn)
        self.logout_btn.clicked.connect(self.logout)

        sidebar.addStretch(1)
        sidebar.addWidget(logo)
        sidebar.addWidget(self.home_btn)
        sidebar.addWidget(self.pos_btn)
        sidebar.addWidget(self.orders_btn)
        sidebar.addWidget(self.logout_btn)
        sidebar.addStretch(1)

        # === MAIN CONTENT ===
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(60, 50, 60, 50)

        title = QLabel("🧾 My Orders")
        title.setFont(QFont("Arial", 30, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(title)

        # Table
        self.table = QTableWidget()
        self.table.setStyleSheet("""
            QHeaderView::section {
                background-color: #1f1f1f;
                color: #00BFFF;
                font-size: 20px;
                font-weight: bold;
                padding: 5px;
            }
            QTableWidget {
                background-color: #1e1e1e;
                border: 1px solid #333;
                font-size: 20px;
                gridline-color: #333;
                font-size: 14px;
            }
        """)
        
        content_layout.addWidget(self.table)

        # Refresh Button
        refresh_btn = QPushButton("Refresh Orders")
        refresh_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #00BFFF;
                color: white;
                font-size: 16px;
                border-radius: 10px;
                padding: 12px 25px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #009ACD;
            }
        """)
        refresh_btn.clicked.connect(self.load_orders)
        content_layout.addWidget(refresh_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(sidebar_container, 1)
        main_layout.addLayout(content_layout, 3)

        self.load_orders()

    # --- Database Query ---
    def load_orders(self):
        try:
            connection = kuha_databse()
            cursor = connection.cursor()
            query = """
                SELECT 
                    o.order_id,
                    o.order_date,
                    o.status,
                    o.total_amount,
                    p.payment_method,
                    p.amount_paid,
                    p.change_amount,
                    GROUP_CONCAT(CONCAT(m.name, ' x', oi.quantity) SEPARATOR ', ') AS items_ordered
                FROM orders o
                JOIN order_items oi ON o.order_id = oi.order_id
                JOIN menu_items m ON oi.item_id = m.item_id
                LEFT JOIN payments p ON o.order_id = p.order_id
                WHERE o.customer_id = %s
                GROUP BY o.order_id;
            """
            cursor.execute(query, (self.user_data["customer_id"],))
            rows = cursor.fetchall()

            headers = [
                "Order ID", "Order Date", "Status", "Total Amount",
                "Payment Method", "Amount Paid", "Change", "Items Ordered"
            ]
            self.table.setColumnCount(len(headers))
            self.table.setHorizontalHeaderLabels(headers)
            self.table.setRowCount(len(rows))

            for row_index, row_data in enumerate(rows):
                for col_index, col_data in enumerate(row_data):
                    item = QTableWidgetItem(str(col_data))
                    item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                    self.table.setItem(row_index, col_index, item)
            
            
            self.table.setColumnWidth(0, 120)   
            self.table.setColumnWidth(1, 160)  
            self.table.setColumnWidth(2, 100)   
            self.table.setColumnWidth(3, 200)   
            self.table.setColumnWidth(4, 180)   
            self.table.setColumnWidth(5, 200)   
            self.table.setColumnWidth(6, 150)
            self.table.setColumnWidth(7, 150)
            self.table.setFixedSize(1300, 500)
        

        except Error as e:
            QMessageBox.critical(self, "Database Error", f"Error loading orders:\n{e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    # --- Navigation Functions ---
    def open_pos(self):
        from POS import POSPage
        self.pos_page = POSPage(self.user_data)
        self.pos_page.showMaximized()
        self.close()

    def open_home(self):
        from user_home import CustomerHomePage
        self.home = CustomerHomePage(self.user_data)
        self.home.showMaximized()
        self.close()

    def logout(self):
        from login import Login
        self.logout = Login()
        self.logout.showMaximized()
        self.close()

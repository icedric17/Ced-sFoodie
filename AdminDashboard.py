import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QApplication, QFrame
)
from PyQt6.QtGui import QFont, QIcon, QPixmap
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import mysql.connector
from db import kuha_databse


class SalesBarGraph(FigureCanvas):
    def __init__(self):
        self.fig = Figure(facecolor="#121212")
        super().__init__(self.fig)
        self.ax = self.fig.add_subplot(111)
        self.fig.subplots_adjust(bottom=0.25)
        self.load_data()

    def load_data(self):
        """Fetch total sales per menu item from database."""
        try:
            db = kuha_databse()
            cursor = db.cursor()

            query = """
                SELECT m.name, SUM(oi.quantity * m.price) AS total_sales
                FROM order_items oi
                JOIN menu_items m ON oi.item_id = m.item_id
                JOIN orders o ON oi.order_id = o.order_id
                WHERE o.status != 'Cancelled'
                GROUP BY m.name
                ORDER BY total_sales DESC
            """
            cursor.execute(query)
            results = cursor.fetchall()

            if results:
                items = [row[0] for row in results]
                totals = [float(row[1]) for row in results]

                self.ax.bar(items, totals, color="#4CAF50")
                self.ax.set_facecolor("#1E1E1E")
                self.ax.set_title("Total Sales per Menu Item", color="white", fontsize=16, pad=20)
                self.ax.set_xlabel("Menu Items", color="white", fontsize=12)
                self.ax.set_ylabel("Total Sales (₱)", color="white", fontsize=12)
                self.ax.tick_params(axis='x', rotation=25, colors='white')
                self.ax.tick_params(axis='y', colors='white')

                for spine in self.ax.spines.values():
                    spine.set_color("white")

                self.fig.tight_layout()
            else:
                self.ax.text(0.5, 0.5, "No sales data found",
                            color="white", ha="center", va="center", fontsize=14)

            cursor.close()
            db.close()

        except mysql.connector.Error as err:
            print("Database Error:", err)


class AdminDashboard(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.setWindowTitle("Admin Dashboard")
        self.setGeometry(0, 0, 1920, 1080)
        self.showMaximized()
        self.setStyleSheet("background-color: #121212;")
        self.setWindowIcon(QIcon('Logo (2).png'))

        # === Main Layout ===
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


        # Sidebar Buttons
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
        dashboard_btn.setStyleSheet(active_btn)
        sidebar.addWidget(dashboard_btn)
        
        manage_orders_btn = QPushButton("🛒 Manage Orders")
        manage_orders_btn.setStyleSheet(base_btn)
        manage_orders_btn.clicked.connect(self.open_manage_orders)
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

        title = QLabel("Admin Dashboard Overview")
        title.setStyleSheet("color: white;")
        title.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(title)

        # Add the Bar Graph
        chart = SalesBarGraph()
        content_layout.addWidget(chart)

        main_layout.addWidget(content_area)
    
    def logout(self):
        from login import Login
        self.login = Login()
        self.login.showMaximized()
        self.close()
    
    def open_manage_orders(self):
        from ManageOrders import ManageOrders
        self.manage_orders = ManageOrders(self.user_data)
        self.manage_orders.showMaximized()
        self.close()
    
    def open_manage_menu(self):
        from ManageMenu import ManageMenu
        self.manage_menu = ManageMenu(self.user_data)
        self.manage_menu.showMaximized()
        self.close()
    


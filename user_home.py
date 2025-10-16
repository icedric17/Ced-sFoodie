import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QScrollArea, QVBoxLayout
)
from PyQt6.QtGui import QFont, QIcon, QPixmap
from PyQt6.QtCore import Qt
from db import kuha_databse

class CustomerHomePage(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.setWindowTitle("Customer Home Page")
        self.setGeometry(0, 0, 1920, 1080)
        self.showMaximized()
        self.setStyleSheet("background-color: ##E53935;")
        self.setWindowIcon(QIcon('Logo (2).png'))

        # === Main Layout ===
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(0)

        # === Sidebar ===
        sidebar_container = QWidget()
        sidebar_container.setStyleSheet("background-color: #4A0E13;")
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
                background-color: #FF6A00;
                color: #E0E0E0;
                font-size: 20px;
                padding: 20px;
                border-radius: 12px;
                font-weight: bold;
                min-width: 250px;
                min-height: 80px;
            }
            QPushButton:hover {
                background-color: #FF8C00;
            }
        """

        active_btn = """
            QPushButton {
                background-color: #FF6A00;
                color: white;
                font-size: 20px;
                padding: 20px;
                border-radius: 12px;
                font-weight: bold;
                min-width: 250px;
                min-height: 80px;
            }
            QPushButton:hover {
                background-color: #FF8C00;
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

        # Buttons
        self.home_btn = QPushButton("Home")
        self.home_btn.setStyleSheet(active_btn)

        self.pos_btn = QPushButton("POS")
        self.pos_btn.setStyleSheet(base_btn)
        self.pos_btn.clicked.connect(self.open_pos)

        self.orders_btn = QPushButton("Orders")
        self.orders_btn.setStyleSheet(base_btn)
        self.orders_btn.clicked.connect(self.open_orders)

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

        # === Main Content ===
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(80, 60, 80, 60)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # --- Welcome Label ---
        welcome_label = QLabel(f"Welcome back, {self.user_data.get('Fullname', 'Customer')}!")
        welcome_label.setFont(QFont("Arial", 36, QFont.Weight.Bold))
        welcome_label.setStyleSheet("color: white; margin-bottom: 20px;")
        right_layout.addWidget(welcome_label)

        subtitle_label = QLabel("Here's a quick look at your recent activity:")
        subtitle_label.setFont(QFont("Arial", 20))
        subtitle_label.setStyleSheet("color: #CCCCCC; margin-bottom: 30px;")
        right_layout.addWidget(subtitle_label)

        # --- Recent Activity Box ---
        activity_frame = QFrame()
        activity_frame.setStyleSheet("""
            QFrame {
                background-color: #1E1E1E;
                border-radius: 20px;
                padding: 30px;
            }
        """)
        activity_layout = QVBoxLayout(activity_frame)
        activity_layout.setSpacing(15)

        # Fetch recent activity from DB
        recent_activities = self.fetch_recent_activity()

        if recent_activities:
            for name, price, quantity, date in recent_activities:
                label = QLabel(f"🛒 {name} — ₱{price:.2f} - Quantity: {quantity} |  Ordered on: {date}")
                label.setFont(QFont("Arial", 16))
                label.setStyleSheet("color: #FFFFFF;")
                activity_layout.addWidget(label)
        else:
            no_label = QLabel("No recent activity found.")
            no_label.setFont(QFont("Arial", 16))
            no_label.setStyleSheet("color: #AAAAAA;")
            activity_layout.addWidget(no_label)

        right_layout.addWidget(activity_frame)
        right_layout.addStretch(1)

        # Combine layouts
        main_layout.addWidget(sidebar_container, 1)
        main_layout.addLayout(right_layout, 3)

    def fetch_recent_activity(self):
        """Fetch recent customer orders from DB (e.g., last 5 items)."""
        try:
            conn = kuha_databse()
            cursor = conn.cursor()
            query = """
                SELECT m.name, m.price, o_r.quantity, o.order_date
                FROM order_items o_r
                JOIN menu_items m ON o_r.item_id = m.item_id
                JOIN orders o ON o_r.order_id = o.order_id
                JOIN customers c ON o.customer_id = c.customer_id
                WHERE o.customer_id = %s
                ORDER BY o.order_date DESC
                LIMIT 5
            """
            cursor.execute(query, (self.user_data.get("customer_id"),))
            return cursor.fetchall()
        except Exception as e:
            print("Error fetching recent activity:", e)
            return []
        finally:
            try:
                if conn.is_connected():
                    conn.close()
            except:
                pass
            
    def logout(self):
        from login import Login
        self.logout = Login()
        self.logout.showMaximized()
        self.close()

    def open_pos(self):
        from POS import POSPage
        self.pos_page = POSPage(self.user_data)
        self.pos_page.showMaximized()
        self.close()
        
    def open_orders(self):
        from order import CustomerOrders
        self.orders_page = CustomerOrders(self.user_data)
        self.orders_page.showMaximized()
        self.close()
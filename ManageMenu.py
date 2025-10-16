import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView,
    QDialog, QFormLayout, QLineEdit, QDoubleSpinBox, QComboBox, QDialogButtonBox
)
from PyQt6.QtGui import QFont, QIcon, QPixmap
from PyQt6.QtCore import Qt
import mysql.connector
from db import kuha_databse


class ManageMenu(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.setWindowTitle("Manage Menu")
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
        dashboard_btn.setStyleSheet(base_btn)
        dashboard_btn.clicked.connect(self.back_to_dashboard)
        sidebar.addWidget(dashboard_btn)
        
        manage_orders_btn = QPushButton("🛒 Manage Orders")
        manage_orders_btn.setStyleSheet(base_btn)
        manage_orders_btn.clicked.connect(self.open_manage_orders)
        sidebar.addWidget(manage_orders_btn)
        
        manage_menu_btn = QPushButton("📋 Manage Menu")
        manage_menu_btn.setStyleSheet(active_btn)
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
        
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(60, 50, 60, 50)
        
        # Title
        title = QLabel("🍽️ Manage Menu Items")
        title.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(title)
        
        # Buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("➕ Add Item")
        add_btn.setStyleSheet(self.button_style("#4CAF50"))
        add_btn.clicked.connect(self.add_item)

        btn_layout.addWidget(add_btn)
        content_layout.addLayout(btn_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.verticalHeader().setDefaultSectionSize(70)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Category", "Price", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("""
            QHeaderView::section {
                background-color: #1E1E1E;
                color: white;
                font-weight: bold;
                padding: 10px;
            }
            QTableWidget {
                background-color: #1E1E1E;
                color: white;
                font-size: 16px;
                gridline-color: #333;
            }
            QTableWidget::item:selected {
                background-color: #333;
            }
        """)
        self.table.setFixedHeight(700)
        content_layout.addWidget(self.table)
        
        main_layout.addWidget(sidebar_container, 1)
        main_layout.addLayout(content_layout, 3)

        self.load_menu_items()

    def button_style(self, color):
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                padding: 14px 25px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 18px;
            }}
            QPushButton:hover {{
                background-color: #555;
            }}
        """

    def load_menu_items(self):
        """Load menu items from the database."""
        try:
            db = kuha_databse()
            cursor = db.cursor()

            cursor.execute("SELECT item_id, name, category, price FROM menu_items")
            results = cursor.fetchall()
            self.table.setRowCount(0)

            for row_number, row_data in enumerate(results):
                self.table.insertRow(row_number)
                for col, data in enumerate(row_data):
                    self.table.setItem(row_number, col, QTableWidgetItem(str(data)))

                # Add Action Buttons (fixed visibility and size)
                edit_btn = QPushButton("✏️ Edit")
                edit_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #FFC107;
                        color: black;
                        font-weight: bold;
                        font-size: 10px;
                        border-radius: 10px;
                        padding: 10px 25px;
                        min-width: 40px;
                        min-height: 15px;
                    }
                    QPushButton:hover {
                        background-color: #FFD54F;
                    }
                """)
                edit_btn.clicked.connect(lambda _, id=row_data[0]: self.edit_item(id))

                delete_btn = QPushButton("🗑️ Delete")
                delete_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #F44336;
                        color: white;
                        font-weight: bold;
                        font-size: 10px;
                        border-radius: 10px;
                        padding: 10px 25px;
                        min-width: 40px;
                        min-height: 15px;
                    }
                    QPushButton:hover {
                        background-color: #E53935;
                    }
                """)
                delete_btn.clicked.connect(lambda _, id=row_data[0]: self.delete_item(id))

                # Layout to hold both buttons
                action_layout = QHBoxLayout()
                action_layout.setContentsMargins(5, 5, 5, 5)
                action_layout.setSpacing(20)
                action_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                action_layout.addWidget(edit_btn)
                action_layout.addWidget(delete_btn)

                action_widget = QWidget()
                action_widget.setLayout(action_layout)
                action_widget.setStyleSheet("background-color: transparent;")
                self.table.setCellWidget(row_number, 4, action_widget)


            cursor.close()
            db.close()

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Database Error", str(err))

    def add_item(self):
        dialog = MenuItemDialog()
        if dialog.exec():
            name, category, price = dialog.get_data()
            try:
                db = kuha_databse()
                cursor = db.cursor()
                cursor.execute(
                    "INSERT INTO menu_items (name, category, price) VALUES (%s, %s, %s)",
                    (name, category, price)
                )
                db.commit()
                cursor.close()
                db.close()
                QMessageBox.information(self, "Success", "Menu item added successfully.")
                self.load_menu_items()
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error", str(err))

    def edit_item(self, item_id):
        try:
            db = kuha_databse()
            cursor = db.cursor()
            cursor.execute("SELECT name, category, price FROM menu_items WHERE item_id = %s", (item_id,))
            item = cursor.fetchone()
            cursor.close()
            db.close()

            if not item:
                QMessageBox.warning(self, "Not Found", "Menu item not found.")
                return

            dialog = MenuItemDialog(item[0], item[1], item[2])
            if dialog.exec():
                name, category, price = dialog.get_data()
                db = kuha_databse()
                cursor = db.cursor()
                cursor.execute("""
                    UPDATE menu_items
                    SET name=%s, category=%s, price=%s
                    WHERE item_id=%s
                """, (name, category, price, item_id))
                db.commit()
                cursor.close()
                db.close()
                QMessageBox.information(self, "Success", "Menu item updated.")
                self.load_menu_items()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error", str(err))

    def delete_item(self, item_id):
        confirm = QMessageBox.question(
            self, "Confirm Delete", "Are you sure you want to delete this item?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                db = kuha_databse()
                cursor = db.cursor()
                cursor.execute("DELETE FROM menu_items WHERE item_id = %s", (item_id,))
                db.commit()
                cursor.close()
                db.close()
                QMessageBox.information(self, "Deleted", "Menu item deleted successfully.")
                self.load_menu_items()
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error", str(err))

    def back_to_dashboard(self):
        from AdminDashboard import AdminDashboard
        self.dashboard = AdminDashboard(self.user_data)
        self.dashboard.showMaximized()
        self.close()
    
    def open_manage_orders(self):
        from ManageOrders import ManageOrders
        self.manage_orders = ManageOrders(self.user_data)
        self.manage_orders.showMaximized()
        self.close()
    
    def logout(self):
        from login import Login
        self.login = Login()
        self.login.showMaximized()
        self.close()
    
    


class MenuItemDialog(QDialog):
    def __init__(self, name="", category="", price=0.0):
        super().__init__()
        self.setWindowTitle("Menu Item Details")
        self.setStyleSheet("background-color: #1E1E1E; color: white; font-size: 16px;")
        self.setFixedWidth(400)

        layout = QFormLayout(self)
        self.name_input = QLineEdit(name)
        self.category_input = QComboBox()
        self.category_input.addItems(["Drinks", "Snacks", "Meals", "Desserts"])
        if category:
            index = self.category_input.findText(category)
            if index >= 0:
                self.category_input.setCurrentIndex(index)

        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 100000)
        self.price_input.setValue(float(price))
        self.price_input.setPrefix("₱ ")
        self.price_input.setDecimals(2)

        layout.addRow("Name:", self.name_input)
        layout.addRow("Category:", self.category_input)
        layout.addRow("Price:", self.price_input)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_data(self):
        return (
            self.name_input.text(),
            self.category_input.currentText(),
            self.price_input.value()
        )

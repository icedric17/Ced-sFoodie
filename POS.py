import sys
from mysql.connector import Error
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLineEdit, QScrollArea, QFrame, QSpacerItem, QSizePolicy,
    QDialog, QFormLayout, QSpinBox, QMessageBox
)
from PyQt6.QtGui import QFont, QPixmap, QIcon
from PyQt6.QtCore import Qt
from db import kuha_databse


class POSPage(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.setWindowTitle("Point of Sale - Food Ordering System")
        self.setGeometry(0, 0, 1920, 1080)
        self.showMaximized()
        self.setWindowIcon(QIcon('Logo (2).png'))
        self.setStyleSheet("background-color: #121212; color: white;")

        # --- Main Layout ---
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

        # Buttons
        self.home_btn = QPushButton("Home")
        self.home_btn.setStyleSheet(base_btn)
        self.home_btn.clicked.connect(self.open_home)
        
        self.pos_btn = QPushButton("POS")
        self.pos_btn.setStyleSheet(active_btn)

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

        # === MAIN CONTENT ===
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(60, 50, 60, 50)

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search for menu items...")
        self.search_bar.setFont(QFont("Arial", 16))
        self.search_bar.setStyleSheet("""
            QLineEdit {
                background-color: #2C2C2C;
                color: white;
                border-radius: 15px;
                padding: 12px 20px;
            }
        """)
        self.search_bar.textChanged.connect(self.filter_items)
        content_layout.addWidget(self.search_bar)

        # Scroll area for menu items
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background-color: transparent; border: none;")
        self.product_container = QWidget()
        self.grid_layout = QGridLayout(self.product_container)
        self.grid_layout.setSpacing(25)
        scroll_area.setWidget(self.product_container)
        content_layout.addWidget(scroll_area)

        # Add to main layout
        main_layout.addWidget(sidebar_container, 1)
        main_layout.addLayout(content_layout, 3)

        # Load items
        self.load_menu_items()

    def load_menu_items(self):
        try:
            connection = kuha_databse()
            cursor = connection.cursor()
            cursor.execute("SELECT item_id, name, price FROM menu_items")
            self.menu_items = cursor.fetchall()
        except Exception as e:
            print("Error loading menu items:", e)
            self.menu_items = []
        finally:
            if connection and connection.is_connected():
                connection.close()
        self.display_items(self.menu_items)

    def display_items(self, items):
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        row, col = 0, 0
        for item_id, name, price in items:
            card = self.create_item_card(item_id, name, price)
            self.grid_layout.addWidget(card, row, col)
            col += 1
            if col >= 3:
                col = 0
                row += 1

    def create_item_card(self, item_id, name, price):
        card = QFrame()
        card.setStyleSheet("background-color: #1E1E1E; border-radius: 15px; padding: 15px;")
        layout = QVBoxLayout(card)

        name_label = QLabel(name)
        name_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        price_label = QLabel(f"₱{price:.2f}")
        price_label.setFont(QFont("Arial", 16))
        price_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        qty_input = QSpinBox()
        qty_input.setRange(1, 100)
        qty_input.setStyleSheet("background-color: #2C2C2C; color: white; padding: 5px; border-radius: 5px; width: 60px;")
        qty_input.setAlignment(Qt.AlignmentFlag.AlignCenter)

        add_btn = QPushButton("Add Order")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #3A3A3A;
                color: white;
                border-radius: 8px;
                padding: 10px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #4A4A4A;
            }
        """)
        add_btn.clicked.connect(lambda: self.confirm_order(item_id, name, price, qty_input.value()))

        layout.addWidget(name_label)
        layout.addWidget(price_label)
        layout.addWidget(qty_input)
        layout.addWidget(add_btn)
        return card

    def confirm_order(self, item_id, name, price, quantity):
        dialog = QDialog(self)
        dialog.setWindowTitle("Payment")
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1E1E1E;
                color: white;
            }
            QLabel {
                font-size: 18px;
            }
            QLineEdit {
                background-color: #2C2C2C;
                color: white;
                padding: 10px;
                border-radius: 8px;
                font-size: 16px;
            }
            QPushButton {
                background-color: #007BFF;
                color: white;
                padding: 12px;
                border-radius: 10px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #0066CC;
            }
        """)

        dialog.resize(500, 350)

        form = QFormLayout(dialog)
        form.setSpacing(20)
        form.setContentsMargins(40, 40, 40, 40)

        total_amount = price * quantity
        total_label = QLabel(f"Total: ₱{total_amount:.2f}")
        total_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        amount_input = QLineEdit()
        amount_input.setPlaceholderText("Enter amount paid")

        order_btn = QPushButton("Order Now")
        order_btn.clicked.connect(lambda: self.process_order(
            dialog, item_id, name, price, quantity, total_amount, amount_input.text()
        ))

        form.addRow(total_label)
        form.addRow("Amount Paid:", amount_input)
        form.addRow("", order_btn)

        dialog.exec()


    def process_order(self, dialog, item_id, name, price, quantity, total_amount, amount_text):

        amount_paid = float(amount_text)
        total_amount = float(total_amount)

        if amount_paid < total_amount:
            QMessageBox.warning(self, "Insufficient", "The amount paid is not enough.")
            return

        try:

            connection = kuha_databse()
            cursor = connection.cursor()

            cursor.execute("INSERT INTO orders (customer_id, total_amount) VALUES (%s, %s)",
                        (self.user_data['customer_id'], total_amount))
            connection.commit()
            order_id = cursor.lastrowid
            
            cursor.execute("INSERT INTO order_items (order_id, item_id, quantity, subtotal) VALUES (%s, %s, %s, %s)",
                        (order_id, item_id, quantity, total_amount))
            connection.commit()
            
            change = amount_paid - total_amount

            cursor.execute("INSERT INTO payments (order_id, amount_paid, change_amount) VALUES (%s, %s, %s)",
                        (order_id, amount_paid, change))
            connection.commit()
            
            QMessageBox.information(self, "Receipt",
                                    f"✅ Order Successful!\n\nItem: {name}\nQuantity: {quantity}\nTotal: ₱{total_amount:.2f}\n"
                                    f"Amount Paid: ₱{amount_paid:.2f}\nChange: ₱{change:.2f}")
            dialog.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error processing order: {e}")
        finally:
            if connection.is_connected():
                connection.close()

    def filter_items(self, text):
        filtered = [i for i in self.menu_items if text.lower() in i[1].lower()]
        self.display_items(filtered)

    def logout(self):
        from login import Login
        self.logout = Login()
        self.logout.showMaximized()
        self.close()

    def open_home(self):
        from user_home import CustomerHomePage
        self.home = CustomerHomePage(self.user_data)
        self.home.showMaximized()
        self.close()
        
    def open_orders(self):
        from order import CustomerOrders
        self.orders_page = CustomerOrders(self.user_data)
        self.orders_page.showMaximized()
        self.close()


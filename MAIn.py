import sys
from mysql.connector import Error
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
)
from PyQt6.QtGui import QFont, QPixmap, QCursor, QIcon
from PyQt6.QtCore import Qt
from db import kuha_databse


class WelcomePage(QWidget):
    def __init__(self, user_data=None):
        super().__init__()
        self.user_data = user_data
        self.setWindowTitle("Food Ordering System")
        self.setGeometry(0, 0, 1920, 1080)
        self.showMaximized()
        self.setWindowIcon(QIcon('Logo (2).png'))

        # --- Full Dark Background ---
        self.setStyleSheet("background-color: #2C0B0E;")  # deep red-black

        # --- Main Layout ---
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # --- Card Container ---
        self.container = QWidget()
        self.container.setStyleSheet("""
            background-color: #4A0E13;
            border-radius: 20px;
            padding: 40px;
            border: 2px solid #66181E;cli
        """)
        self.container.setFixedSize(1600, 900)

        card_layout = QVBoxLayout()
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # --- Logo and Text Layout ---
        logo_text_layout = QHBoxLayout()
        logo_text_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Logo
        logo = QLabel()
        pixmap = QPixmap("Logo (2).png")
        pixmap = pixmap.scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        logo.setPixmap(pixmap)

        # Title Texts
        title_layout = QVBoxLayout()
        title_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        clinic_label = QLabel("CED Foodie")
        clinic_label.setFont(QFont("Arial", 90, QFont.Weight.Bold))
        clinic_label.setStyleSheet("color: #FFCDD2; padding-top: 120px;")  # light gray text

        appointment_label = QLabel("Food Ordering System")
        appointment_label.setFont(QFont("Arial", 60))
        appointment_label.setStyleSheet("""
            color: #EF9A9A; padding-bottom: 120px;
        """)

        title_layout.addWidget(clinic_label)
        title_layout.addWidget(appointment_label)

        logo_text_layout.addWidget(logo)
        logo_text_layout.addLayout(title_layout)

        # --- Buttons Layout ---
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Common button style
        button_style = """
            QPushButton {
                border-radius: 20px;
                padding: 10px 40px;
                color: white;
                font-size: 18px;
                font-weight: bold;
                border: none;
                transition: 0.3s;
            }
            QPushButton:hover {
                transform: scale(1.05);
            }
        """

        # --- Login Button (Dark Gray) ---
        self.login_button = QPushButton("Login")
        self.login_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.login_button.setStyleSheet(button_style + """
                QPushButton {
            background-color: #B71C1C;
     }
        QPushButton:hover {
            background-color: #C62828;
            }
        """)
        self.login_button.setFixedSize(250, 70)
        self.login_button.clicked.connect(self.open_login)

        # --- Register Button (Charcoal) ---
        self.register_button = QPushButton("Register")
        self.register_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.register_button.setStyleSheet(button_style + """
              QPushButton {
            background-color: #E53935;
        }
        QPushButton:hover {
            background-color: #EF5350;
            }
        """)
        self.register_button.setFixedSize(250, 70)
        self.register_button.clicked.connect(self.open_register)

        button_layout.addWidget(self.login_button)
        button_layout.addSpacing(200)
        button_layout.addWidget(self.register_button)

        # --- Add to card ---
        card_layout.addLayout(logo_text_layout)
        card_layout.addSpacing(50)
        card_layout.addLayout(button_layout)

        self.container.setLayout(card_layout)
        main_layout.addWidget(self.container, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(main_layout)

    def open_login(self):
        from login import Login
        self.login_window = Login()
        self.login_window.showMaximized()
        self.close()

    def open_register(self):
        from register import Register
        self.register_window = Register()
        self.register_window.showMaximized()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WelcomePage()
    window.show()
    sys.exit(app.exec())

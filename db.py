import mysql.connector 

def kuha_databse():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="ced's_foodie"
    )
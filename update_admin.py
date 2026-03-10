import sqlite3
from werkzeug.security import generate_password_hash
import os

DATABASE = 'quiz_system.db'

def update_admin():
    if not os.path.exists(DATABASE):
        print(f"Database {DATABASE} not found.")
        return

    db = sqlite3.connect(DATABASE)
    new_username = 'admin1@gmail.com'
    new_password = generate_password_hash('Admin.123')

    try:
        # Try to find the existing admin and update. 
        # Since 'admin' was the previous default, we'll update that specific record if it exists,
        # otherwise we'll ensure a record with the new username exists.
        
        cursor = db.cursor()
        cursor.execute("SELECT id FROM admins WHERE username = 'admin' LIMIT 1")
        admin = cursor.fetchone()
        
        if admin:
            cursor.execute("UPDATE admins SET username = ?, password = ? WHERE id = ?", 
                           (new_username, new_password, admin[0]))
            print(f"Updated existing admin record (ID: {admin[0]})")
        else:
            # Check if admin1@gmail.com already exists
            cursor.execute("SELECT id FROM admins WHERE username = ? LIMIT 1", (new_username,))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO admins (username, password) VALUES (?, ?)", 
                               (new_username, new_password))
                print(f"Inserted new admin record: {new_username}")
            else:
                print(f"Admin record for {new_username} already exists.")
        
        db.commit()
        print("Success: Admin credentials updated in local database.")
    except Exception as e:
        print(f"Error updating database: {e}")
    finally:
        db.close()

if __name__ == '__main__':
    update_admin()

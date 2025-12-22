# check_db.py
from app import app, db
from sqlalchemy import inspect

with app.app_context():
    inspector = inspect(db.engine)
    
    print("Таблицы в базе данных:")
    print(inspector.get_table_names())
    
    print("\nКолонки в таблице 'novel':")
    columns = inspector.get_columns('novel')
    for col in columns:
        print(f"  - {col['name']} ({col['type']})")
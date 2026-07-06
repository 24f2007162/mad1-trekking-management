from pathlib import Path
import sqlite3

db_path = Path("instance") / "trekking.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

prices = {
    "Kedarkantha": 6999,
    "Sandakphu": 7499,
    "Kuari Pass": 5999,
    "Hampta Pass": 9999,
    "Valley of Flowers": 8499,
    "Goechala": 11999,
    "Rupin Pass": 12999,
    "Roopkund": 10999,
    "Tarsar Marsar": 9499
}

for trek, price in prices.items():
    cursor.execute(
        "UPDATE treks SET price=? WHERE name=?",
        (price, trek)
    )

conn.commit()
conn.close()

print("Trek prices updated.")
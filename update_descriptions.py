from pathlib import Path
import sqlite3

db_path = Path("instance") / "trekking.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

descriptions = {

    "Rajgad Trek":
    "Explore the historic capital of Chhatrapati Shivaji Maharaj while enjoying scenic trails, ancient fortifications and panoramic Sahyadri views.",

    "Roop Kund Trek":
    "Journey to the mysterious Skeleton Lake surrounded by snow-capped Himalayan peaks and breathtaking alpine landscapes.",

    "Brahmatal Trek":
    "A spectacular winter trek known for frozen lakes, snow-covered forests and magnificent views of Mt. Trishul and Nanda Ghunti.",

    "Har ki Dun":
    "Walk through charming Himalayan villages, lush valleys and ancient forests in one of Uttarakhand's most beautiful trekking destinations.",

    "Triund Trek":
    "A beginner-friendly trek offering stunning views of the Dhauladhar range and a memorable overnight camping experience.",

    "Dayara Bugyal Trek":
    "Discover vast alpine meadows, dense forests and magnificent Himalayan vistas throughout every season of the year.",

    "KedarKantha Trek":
    "One of India's most popular winter treks featuring snowy trails, pine forests and an unforgettable summit sunrise.",

    "Valley of Flowers":
    "A UNESCO World Heritage Site famous for colorful Himalayan flowers blooming across breathtaking alpine meadows.",

    "Sandakphu":
    "Witness spectacular views of Everest, Kanchenjunga and other Himalayan giants from the highest point in West Bengal.",

    "Tarsar Marsar":
    "Experience Kashmir's pristine alpine lakes, rolling meadows and peaceful mountain landscapes unlike anywhere else.",

    "Hampta pass":
    "Cross from lush green Kullu Valley into the dramatic cold desert of Lahaul on this unforgettable crossover trek.",

    "Rupin pass":
    "A thrilling high-altitude trek featuring waterfalls, hanging villages, snow bridges and dramatic mountain scenery.",

    "Goechala Trek":
    "Reach one of the closest viewpoints of Mount Kanchenjunga through forests, glaciers and spectacular Himalayan terrain.",

    "Kuari Pass":
    "Follow the famous Curzon Trail through oak forests and alpine meadows with stunning views of Nanda Devi.",

    "Buran Ghati":
    "An adventurous trek combining dense forests, beautiful meadows, hidden lakes and exciting snow wall descents.",

    "Kumara Parvatha":
    "One of Karnataka's toughest treks offering dense forests, rolling grasslands and rewarding summit views of the Western Ghats.",

    "Kodhchadri Trek":
    "Trek through evergreen forests to a scenic hilltop known for mesmerizing sunsets and views of the Arabian Sea.",

    "Chadar Trek":
    "Walk across the frozen Zanskar River in Ladakh on one of the world's most unique winter trekking experiences."

}

for trek_name, description in descriptions.items():

    cursor.execute(
        """
        UPDATE treks
        SET description = ?
        WHERE name = ?
        """,
        (description, trek_name)
    )

    print(f"{trek_name} -> {cursor.rowcount} row(s) updated")

conn.commit()
conn.close()

print("\n All trek descriptions updated successfully!")
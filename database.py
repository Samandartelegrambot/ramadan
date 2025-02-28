import sqlite3

def init_db():
    conn = sqlite3.connect("ramazan.db")
    c = conn.cursor()

    # Regions jadvali
    c.execute('''CREATE TABLE IF NOT EXISTS regions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)''')

    # Districts jadvali (region_id va name kombinatsiyasi unique)
    c.execute('''CREATE TABLE IF NOT EXISTS districts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, region_id INTEGER, name TEXT, sahar_diff INTEGER, iftor_diff INTEGER,
                  FOREIGN KEY (region_id) REFERENCES regions(id),
                  UNIQUE(region_id, name))''')

    # Ramazan times jadvali (date unique)
    c.execute('''CREATE TABLE IF NOT EXISTS ramazan_times
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT UNIQUE, sahar_time TEXT, iftor_time TEXT)''')

    # Ma'lumotlarni qo'shish
    regions = [
        "Toshkent shahri", "Qoraqolpoqiston Respublikasi", "Toshkent viloyati", "Jizzax viloyati",
        "Andijon viloyati", "Namangan viloyati", "Farg‘ona viloyati", "Sirdaryo viloyati",
        "Samarqand viloyati", "Qashqadaryo viloyati", "Surxondaryo viloyati", "Buxoro viloyati",
        "Navoiy viloyati", "Xorazm viloyati"
    ]

    for region in regions:
        c.execute("INSERT OR IGNORE INTO regions (name) VALUES (?)", (region,))

    districts_data = [
        ("Andijon viloyati", "Andijon", -12, -13),
        ("Andijon viloyati", "Xonobod", -14, -15),
        ("Andijon viloyati", "Shahrixon", -10, -12),
        ("Andijon viloyati", "Xo‘jaobod", -12, -14),
        ("Namangan viloyati", "Namangan", -9, -10),
        ("Namangan viloyati", "Pop", -6, -7),
        ("Farg‘ona viloyati", "Farg‘ona", -7, -9),
        ("Farg‘ona viloyati", "Rishton", -6, -9),
        ("Farg‘ona viloyati", "Qo‘qon", -5, -7),
        ("Farg‘ona viloyati", "Quva", -9, -11),
        ("Farg‘ona viloyati", "Chortoq", -10, -11),
        ("Farg‘ona viloyati", "Kosonsoy", -9, -9),
        ("Toshkent viloyati", "Toshkent shahri", 0, 0),
        ("Toshkent viloyati", "Angren", -3, -4),
        ("Toshkent viloyati", "Parkent", -2, -2),
        ("Toshkent viloyati", "Bekobod", +2, +1),
        ("Sirdaryo viloyati", "Guliston", +3, +2),
        ("Sirdaryo viloyati", "Yangiyer", +3, +2),
        ("Sirdaryo viloyati", "Sayxunobod", +3, +2),
        ("Sirdaryo viloyati", "Boyovut", +3, +2),
        ("Sirdaryo viloyati", "Xovos", +3, +2),
        ("Jizzax viloyati", "Jizzax", +8, +7),
        ("Jizzax viloyati", "Zomin", +6, +4),
        ("Jizzax viloyati", "Forish", +9, +8),
        ("Jizzax viloyati", "G‘allaorol", +10, +8),
        ("Samarqand viloyati", "Samarqand", +15, +13),
        ("Samarqand viloyati", "Ishtixon", +13, +11),
        ("Samarqand viloyati", "Urgut", +11, +9),
        ("Samarqand viloyati", "Kattaqo‘rg‘on", +14, +12),
        ("Samarqand viloyati", "Mirbozor", +16, +14),
        ("Qashqadaryo viloyati", "Qarshi", +18, +15),
        ("Qashqadaryo viloyati", "Dehqonobod", +15, +12),
        ("Qashqadaryo viloyati", "Koson", +17, +15),
        ("Qashqadaryo viloyati", "Muborak", +19, +17),
        ("Qashqadaryo viloyati", "Shahrisabz", +14, +11),
        ("Qashqadaryo viloyati", "G‘uzor", +17, +14),
        ("Surxondaryo viloyati", "Termiz", +14, +9),
        ("Surxondaryo viloyati", "Boysun", +13, +9),
        ("Surxondaryo viloyati", "Sho‘rchi", +11, +7),
        ("Buxoro viloyati", "Buxoro", +24, +22),
        ("Buxoro viloyati", "Gazli", +25, +24),
        ("Buxoro viloyati", "G‘ijduvon", +19, +18),
        ("Navoiy viloyati", "Navoiy", +20, +21),
        ("Navoiy viloyati", "Zarafshon", +20, +18),
        ("Navoiy viloyati", "Konimex", +19, +18),
        ("Navoiy viloyati", "Nurota", +15, +14),
        ("Navoiy viloyati", "Uchquduq", +10, +9),
        ("Qoraqolpoqiston Respublikasi", "Nukus", +38, +39),
        ("Qoraqolpoqiston Respublikasi", "Mo‘ynoq", +37, +40),
        ("Qoraqolpoqiston Respublikasi", "Taxtako‘pir", +31, +33),
        ("Qoraqolpoqiston Respublikasi", "Qo‘ng‘irot", +40, +42),
        ("Qoraqolpoqiston Respublikasi", "Qorako‘l", +27, +26),
    ]

    for region_name, district_name, sahar_diff, iftor_diff in districts_data:
        c.execute("SELECT id FROM regions WHERE name=?", (region_name,))
        region_id = c.fetchone()
        if region_id:
            c.execute("INSERT OR IGNORE INTO districts (region_id, name, sahar_diff, iftor_diff) VALUES (?, ?, ?, ?)",
                      (region_id[0], district_name, sahar_diff, iftor_diff))

    ramazan_dates = [
        ("1-mart", "5:40", "18:17"), ("2-mart", "5:38", "18:18"), ("3-mart", "5:37", "18:19"),
        ("4-mart", "5:35", "18:20"), ("5-mart", "5:33", "18:21"), ("6-mart", "5:32", "18:22"),
        ("7-mart", "5:30", "18:24"), ("8-mart", "5:29", "18:25"), ("9-mart", "5:27", "18:26"),
        ("10-mart", "5:25", "18:27"), ("11-mart", "5:24", "18:28"), ("12-mart", "5:22", "18:29"),
        ("13-mart", "5:20", "18:30"), ("14-mart", "5:19", "18:32"), ("15-mart", "5:17", "18:33"),
        ("16-mart", "5:15", "18:34"), ("17-mart", "5:13", "18:35"), ("18-mart", "5:12", "18:36"),
        ("19-mart", "5:10", "18:37"), ("20-mart", "5:08", "18:38"), ("21-mart", "5:06", "18:39"),
        ("22-mart", "5:04", "18:40"), ("23-mart", "5:03", "18:41"), ("24-mart", "5:01", "18:42"),
        ("25-mart", "4:59", "18:43"), ("26-mart", "4:57", "18:44"), ("27-mart", "4:55", "18:45"),
        ("28-mart", "4:54", "18:47"), ("29-mart", "4:52", "18:48"), ("30-mart", "4:50", "18:49"),
    ]

    for date, sahar_time, iftor_time in ramazan_dates:
        c.execute("INSERT OR IGNORE INTO ramazan_times (date, sahar_time, iftor_time) VALUES (?, ?, ?)",
                  (date, sahar_time, iftor_time))

    conn.commit()
    conn.close()
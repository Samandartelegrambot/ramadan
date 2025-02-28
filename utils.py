from datetime import datetime, timedelta

def adjust_time(base_time, minutes_diff):
    try:
        hours, minutes = map(int, base_time.split(":"))
        total_minutes = hours * 60 + minutes + minutes_diff
        days = total_minutes // (24 * 60)  # Kunlar soni
        total_minutes = total_minutes % (24 * 60)  # Kun ichidagi qoldiq
        new_hours = total_minutes // 60
        new_minutes = total_minutes % 60
        return f"{new_hours:02d}:{new_minutes:02d}", days
    except ValueError:
        return "Vaqt formati noto‘g‘ri", 0
import json
import os
from datetime import datetime, timedelta

def generate_ics_calendar():
    profile_path = "data/profile/athlete_profile.json"
    if not os.path.exists(profile_path):
        print("Profile not found.")
        return

    with open(profile_path, "r", encoding="utf-8") as f:
        profile = json.load(f)

    schedule = profile.get("training_schedule", {})
    
    # Generate RFC-5545 iCalendar standard output
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//HiveAlignment//CrunchAndReflection//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:Hive Health & Reflection Routine"
    ]

    days_map = {
        "monday": "MO",
        "tuesday": "TU",
        "wednesday": "WE",
        "thursday": "TH",
        "friday": "FR",
        "sunday": "SU"
    }

    # Recurring events definition
    for day_name, details in schedule.items():
        byday = days_map.get(day_name)
        if not byday:
            continue

        title = f"[Fitness] {details['focus']}" if day_name != "sunday" else f"❤️ {details['focus']}"
        desc = f"Location: {details['location']}\\nDuration: {details['duration_minutes']} min"
        
        if day_name == "sunday":
            desc += "\\n\\nReflection Prompts:\\n1. What went well this week?\\n2. Where did we feel stretched?\\n3. How can I support you next week?\\n4. Work/Life/Academic check-in."

        lines.extend([
            "BEGIN:VEVENT",
            f"SUMMARY:{title}",
            f"DESCRIPTION:{desc}",
            f"LOCATION:{details['location']}",
            f"RRULE:FREQ=WEEKLY;BYDAY={byday}",
            f"UID:{day_name}-hive-alignment@afrodojo.github.io",
            "STATUS:CONFIRMED",
            "TRANSP:OPAQUE",
            "END:VEVENT"
        ])

    lines.append("END:VCALENDAR")

    out_dir = "data/calendar"
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "routine_schedule.ics")
    
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\r\n".join(lines) + "\r\n")

    print(f"Generated universal calendar subscription file: {out_file}")

if __name__ == "__main__":
    generate_ics_calendar()

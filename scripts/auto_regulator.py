import json
import os
from datetime import datetime, timezone

def generate_prescription():
    whoop_file = "data/telemetry/whoop.json"
    if not os.path.exists(whoop_file):
        print("whoop.json not found, skipping prescription generation.")
        return

    with open(whoop_file, "r") as f:
        data = json.load(f)

    rec_score = int(data.get("recovery_score", 50))
    hrv = float(data.get("hrv_ms", 0.0))
    rhr = float(data.get("rhr_bpm", 0.0))
    current_strain = float(data.get("current_strain", 0.0))
    zone = data.get("recovery_zone", "YELLOW").upper()
    phase = data.get("phase", "morning").lower()

    # Dynamic Gate Rules
    if zone == "GREEN" or rec_score >= 66:
        status_badge = "🟩 GREEN — HIGH ADAPTIVE CAPACITY"
        volume = "Full Volume (4 sets × 12–15 reps)"
        rpe_target = "RPE 7.5 – 8.5"
        load_mod = "+2.5% Progressive Microcycle Overload"
        rest_interval = "90–120s compound / 60s isolation"
        primary_movements = "High axial loading: Barbell Back Squat, Weighted Pull-Ups, Overhead Press"
        conditioning = "High-Intensity Functional Intervals or Lactate Threshold threshold intervals"
        acwr_status = "1.02 (Optimal Overload Zone: 0.80 – 1.10)"
    elif zone == "YELLOW" or rec_score >= 34:
        status_badge = "🟨 YELLOW — MAINTENANCE / HOMEOSTASIS"
        volume = "Moderate Volume (3 sets × 8–10 reps capped)"
        rpe_target = "RPE 6.5 – 7.0 (Strict Cap)"
        load_mod = "-10% Load Reduction vs Baseline"
        rest_interval = "Extended Rest (+30s: 120–150s)"
        primary_movements = "Reduced spine loading: Dumbbell Bulgarian Split Squat, Chest-Supported Rows"
        conditioning = "Zone 2 Steady State aerobic pacing (120–135 BPM)"
        acwr_status = "0.92 (Safe Equilibrium Zone: 0.80 – 1.10)"
    else:
        status_badge = "🟥 RED — SYMPATHETIC OVERLOAD / PARASYMPATHETIC BLUNTING"
        volume = "Suppressed Axial Loading"
        rpe_target = "< 5.0 Active Flush"
        load_mod = "Axial S&C Swapped for Parasympathetic Reset"
        rest_interval = "N/A"
        primary_movements = "20 min Therabody Percussive Therapy + 4-4-4-4 Box Breathing"
        conditioning = "Zone 2 Ergometer Rowing or Incline Treadmill Walking (< 130 BPM)"
        acwr_status = "0.78 (Deload / Systemic Flush Required)"

    # Render Prescription Markdown
    markdown = f"""
## 🏋️ Tactical S&C Auto-Regulation Prescription

> **Status:** `{status_badge}`  
> **Recovery:** `{rec_score}%` | **HRV (rMSSD):** `{hrv} ms` | **RHR:** `{rhr} bpm` | **ACWR Gate:** `{acwr_status}`

| Parameter | Prescribed Target |
| :--- | :--- |
| **Volume Allocation** | {volume} |
| **Intensity Gate** | `{rpe_target}` |
| **Load Overload Modulation** | **{load_mod}** |
| **Inter-Set Recovery** | {rest_interval} |
| **Movement Selections** | {primary_movements} |
| **Conditioning Protocol** | {conditioning} |
"""

    os.makedirs("data/telemetry", exist_ok=True)
    with open("data/telemetry/prescription.md", "w", encoding="utf-8") as f:
        f.write(markdown.strip() + "\n")

    # Append prescription to latest_briefing.md
    briefing_file = "data/telemetry/latest_briefing.md"
    if os.path.exists(briefing_file):
        with open(briefing_file, "r", encoding="utf-8") as f:
            briefing_content = f.read()

        if "## 🏋️ Tactical S&C Auto-Regulation Prescription" not in briefing_content:
            combined = briefing_content.strip() + "\n\n---\n\n" + markdown.strip() + "\n"
            with open(briefing_file, "w", encoding="utf-8") as f:
                f.write(combined)

    # Append to README inside marker if available
    readme_file = "README.md"
    if os.path.exists(readme_file):
        with open(readme_file, "r", encoding="utf-8") as f:
            readme_text = f.read()

        if "<!-- AUTO_REGULATION_START -->" in readme_text:
            import re
            pattern = r"<!-- AUTO_REGULATION_START -->[\s\S]*?<!-- AUTO_REGULATION_END -->"
            replacement = f"<!-- AUTO_REGULATION_START -->\n\n{markdown.strip()}\n\n<!-- AUTO_REGULATION_END -->"
            updated = re.sub(pattern, replacement, readme_text)
            with open(readme_file, "w", encoding="utf-8") as f:
                f.write(updated)

    print("Auto-regulation prescription generated successfully.")

if __name__ == "__main__":
    generate_prescription()

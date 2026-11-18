import os
import re

INDEX_PATH = os.path.join("docs", "index.html")
SW_PATH = os.path.join("docs", "sw.js")


def validate_js_syntax(code):
    i = 0
    n = len(code)
    line = 1
    stack = []
    state = "NORMAL"
    last_significant_char = ""
    str_start_line = 1
    regex_line = 1
    in_char_class = False

    while i < n:
        ch = code[i]
        nxt = code[i + 1] if i + 1 < n else ""

        if state == "NORMAL":
            if ch == "\n":
                line += 1
                i += 1
                continue
            if ch.isspace():
                i += 1
                continue
            if ch == "/" and nxt == "/":
                state = "LINE_COMMENT"
                i += 2
                continue
            if ch == "/" and nxt == "*":
                state = "BLOCK_COMMENT"
                i += 2
                continue
            if ch == "'":
                state = "SQ"
                str_start_line = line
                i += 1
                continue
            if ch == '"':
                state = "DQ"
                str_start_line = line
                i += 1
                continue
            if ch == "`":
                state = "TPL"
                i += 1
                continue
            if ch == "/" and last_significant_char in ("", "(", "[", "{", ",", ";", "=", ":", "!", "&", "|", "?", "+", "-", "*", "%", "~", "^", "<", ">"):
                state = "REGEX"
                regex_line = line
                in_char_class = False
                i += 1
                continue
            if ch in "{([":
                stack.append((ch, line))
                last_significant_char = ch
                i += 1
                continue
            if ch in "})]":
                if not stack:
                    raise SyntaxError(f"Unmatched closing '{ch}' at line {line}")
                top, open_line = stack.pop()
                if top == "${" and ch == "}":
                    state = "TPL"
                    i += 1
                    continue
                expected = {"{": "}", "(": ")", "[": "]"}[top]
                if ch != expected:
                    raise SyntaxError(f"Mismatched '{ch}' at line {line}; expected '{expected}' for '{top}' opened at line {open_line}")
                last_significant_char = ch
                i += 1
                continue
            last_significant_char = ch
            i += 1

        elif state == "LINE_COMMENT":
            if ch == "\n":
                line += 1
                state = "NORMAL"
            i += 1

        elif state == "BLOCK_COMMENT":
            if ch == "\n":
                line += 1
            elif ch == "*" and nxt == "/":
                state = "NORMAL"
                i += 2
                continue
            i += 1

        elif state == "SQ":
            if ch == "\\":
                i += 2
                continue
            if ch == "\n":
                raise SyntaxError(f"Unterminated single-quoted string starting at line {str_start_line}")
            if ch == "'":
                state = "NORMAL"
                last_significant_char = "'"
            i += 1

        elif state == "DQ":
            if ch == "\\":
                i += 2
                continue
            if ch == "\n":
                raise SyntaxError(f"Unterminated double-quoted string starting at line {str_start_line}")
            if ch == '"':
                state = "NORMAL"
                last_significant_char = '"'
            i += 1

        elif state == "TPL":
            if ch == "\\":
                i += 2
                continue
            if ch == "\n":
                line += 1
                i += 1
                continue
            if ch == "$" and nxt == "{":
                stack.append(("${", line))
                state = "NORMAL"
                last_significant_char = "{"
                i += 2
                continue
            if ch == "`":
                state = "NORMAL"
                last_significant_char = "`"
            i += 1

        elif state == "REGEX":
            if ch == "\\":
                i += 2
                continue
            if ch == "\n":
                raise SyntaxError(f"Unterminated regex literal at line {regex_line}")
            if ch == "[":
                in_char_class = True
            elif ch == "]":
                in_char_class = False
            elif ch == "/" and not in_char_class:
                state = "NORMAL"
                last_significant_char = "/"
            i += 1

    if state != "NORMAL":
        raise SyntaxError(f"Unclosed state {state} at EOF (line {line})")
    if stack:
        raise SyntaxError(f"Unclosed delimiters at EOF: {stack}")


def main():
    if not os.path.exists(INDEX_PATH):
        raise FileNotFoundError(f"Could not find {INDEX_PATH}. Run from repository root.")

    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Add "Adaptive Workouts" tab button in cockpit navigation
    old_tab_btn = r"""      <button type="button" onclick="switchTab('tab-wearables')" id="btn-tab-wearables" class="tab-btn px-4 py-2 rounded-lg text-sm font-semibold text-rose-400 hover:text-rose-300 transition">WHOOP &amp; Wearables</button>"""

    new_tab_btn = r"""      <button type="button" onclick="switchTab('tab-wearables')" id="btn-tab-wearables" class="tab-btn px-4 py-2 rounded-lg text-sm font-semibold text-rose-400 hover:text-rose-300 transition">WHOOP &amp; Wearables</button>
      <button type="button" onclick="switchTab('tab-workouts')" id="btn-tab-workouts" class="tab-btn px-4 py-2 rounded-lg text-sm font-semibold text-emerald-400 hover:text-emerald-300 transition">Adaptive Workouts (Shoulder &amp; Back)</button>"""

    if "switchTab('tab-workouts')" not in html and old_tab_btn in html:
        html = html.replace(old_tab_btn, new_tab_btn, 1)

    # 2. Add quick shortcut button on the top Wearables strip
    old_top_dash_btn = r"""        <button type="button" onclick="switchTab('tab-wearables')" class="px-3.5 py-1.5 bg-emerald-500 hover:bg-emerald-400 text-slate-950 rounded-lg text-xs font-bold transition flex items-center gap-1.5 shadow-sm">
          Device Dashboards &rarr;
        </button>"""

    new_top_dash_btn = r"""        <button type="button" onclick="switchTab('tab-workouts')" class="px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-bold transition flex items-center gap-1.5 shadow-sm">
          <i data-lucide="dumbbell" class="w-3.5 h-3.5"></i> Shoulder &amp; Back Routine
        </button>
        <button type="button" onclick="switchTab('tab-wearables')" class="px-3.5 py-1.5 bg-emerald-500 hover:bg-emerald-400 text-slate-950 rounded-lg text-xs font-bold transition flex items-center gap-1.5 shadow-sm">
          Device Dashboards &rarr;
        </button>"""

    if "switchTab('tab-workouts')" not in html.split("<!-- DYNAMIC ALIGNMENT CARDS -->")[0] and old_top_dash_btn in html:
        html = html.replace(old_top_dash_btn, new_top_dash_btn, 1)

    # 3. Inject TAB: ADAPTIVE SHOULDER & BACK STRENGTH + FLEXIBILITY ENGINE right after tab-wearables
    workout_tab_html = r"""    <!-- TAB: ADAPTIVE SHOULDER & BACK STRENGTH + FLEXIBILITY ENGINE -->
    <div id="tab-workouts" class="tab-content space-y-6">
      <div class="bg-gradient-to-r from-slate-900 via-emerald-950/30 to-slate-900 border border-emerald-800/50 rounded-2xl p-6 space-y-4 shadow-xl">
        <div class="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4 border-b border-slate-800 pb-4">
          <div>
            <span class="text-[10px] font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
              <i data-lucide="dumbbell" class="w-3.5 h-3.5"></i> Telemetry-Gated Shoulder &amp; Posterior Chain Architect
            </span>
            <h3 class="text-lg font-extrabold text-white mt-0.5">Adaptive Shoulder &amp; Back Strength + Flexibility Engine</h3>
            <p class="text-xs text-slate-400 mt-0.5">Auto-calibrates sets, reps, load, and thoracic/scapular mobility to your live WHOOP Recovery Gate, HRV, and Garmin ACWR.</p>
          </div>
          <div class="flex flex-wrap items-center gap-2">
            <select id="wo-equipment-select" onchange="setWorkoutEquipmentProfile(this.value)" class="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-emerald-500">
              <option value="bands_db">Bands + Dumbbells (Home / Travel)</option>
              <option value="full_gym">Full Gym (Cables, Pull-Up Bar, Dumbbells)</option>
              <option value="bodyweight_band">Minimalist (Resistance Band + Wall/Floor)</option>
            </select>
            <button type="button" onclick="syncWorkoutScheduleToCalendar()" class="px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl text-xs transition flex items-center gap-1.5 shadow">
              <i data-lucide="calendar-plus" class="w-3.5 h-3.5"></i> Push Week to Calendar &amp; Duties
            </button>
            <button type="button" onclick="launchWorkoutVoiceCoach()" class="px-3.5 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold rounded-xl text-xs transition flex items-center gap-1.5 shadow">
              <i data-lucide="headphones" class="w-3.5 h-3.5"></i> Voice-Guided Session
            </button>
          </div>
        </div>

        <!-- Live Telemetry Gate Calibration Strip -->
        <div id="wo-telemetry-banner" class="p-4 rounded-xl bg-slate-950 border border-slate-800 flex flex-col md:flex-row justify-between items-start md:items-center gap-3 text-xs">
          <div class="space-y-1">
            <div class="flex items-center gap-2 flex-wrap">
              <span id="wo-gate-badge" class="px-2.5 py-0.5 rounded bg-rose-500 text-white font-extrabold text-[10px] uppercase">RED GATE</span>
              <span id="wo-gate-title" class="font-bold text-white">Restorative Rotator Cuff Activation + Thoracic Mobility</span>
            </div>
            <p id="wo-gate-detail" class="text-slate-400">WHOOP Recovery: 30% • HRV: 18 ms • Garmin Readiness: 84 • ACWR: 1.03</p>
          </div>
          <div class="flex items-center gap-2 flex-shrink-0">
            <span id="wo-weekly-progress-pill" class="px-3 py-1 rounded-lg bg-emerald-950 border border-emerald-800 text-emerald-300 font-mono font-bold">
              0 / 5 Days Completed
            </span>
          </div>
        </div>
      </div>

      <!-- Today's Prescribed Shoulder & Back Session -->
      <div class="bg-slate-900 border border-sky-800/50 rounded-2xl p-6 space-y-4 shadow-xl">
        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 border-b border-slate-800 pb-3">
          <div>
            <span class="text-[10px] font-bold uppercase tracking-wider text-sky-400">Today's Biometric-Prescribed Session</span>
            <h4 id="wo-today-heading" class="text-base font-bold text-white mt-0.5">Session A: Rotator Cuff Stabilization &amp; Thoracic Extension</h4>
          </div>
          <div class="flex flex-wrap gap-1.5 text-xs">
            <button type="button" onclick="selectWorkoutFocusDay(0)" id="wo-day-pill-0" class="px-2.5 py-1 rounded-lg bg-emerald-500 text-slate-950 font-bold">Mon (A)</button>
            <button type="button" onclick="selectWorkoutFocusDay(1)" id="wo-day-pill-1" class="px-2.5 py-1 rounded-lg bg-slate-950 text-slate-300 border border-slate-800">Tue (Mob)</button>
            <button type="button" onclick="selectWorkoutFocusDay(2)" id="wo-day-pill-2" class="px-2.5 py-1 rounded-lg bg-slate-950 text-slate-300 border border-slate-800">Wed (B)</button>
            <button type="button" onclick="selectWorkoutFocusDay(3)" id="wo-day-pill-3" class="px-2.5 py-1 rounded-lg bg-slate-950 text-slate-300 border border-slate-800">Thu (Mob)</button>
            <button type="button" onclick="selectWorkoutFocusDay(4)" id="wo-day-pill-4" class="px-2.5 py-1 rounded-lg bg-slate-950 text-slate-300 border border-slate-800">Fri (C)</button>
          </div>
        </div>

        <div id="wo-exercises-grid" class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs"></div>

        <!-- Post-Workout Strain & Shoulder/Back Pain-Free Readiness Logger -->
        <div class="pt-3 border-t border-slate-800 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 text-xs">
          <div class="flex flex-wrap items-center gap-3">
            <label class="text-slate-300 font-semibold">Shoulder/Back Comfort (1-10):</label>
            <input type="number" id="wo-comfort-score" min="1" max="10" value="9" class="w-16 bg-slate-950 border border-slate-800 rounded-lg px-2 py-1 text-slate-200 font-mono">
            <input type="text" id="wo-session-note" placeholder="Optional note (e.g., Band external rotation felt strong, zero pinch)..." class="w-64 sm:w-80 bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-slate-200">
          </div>
          <button type="button" onclick="completeSelectedWorkoutDay()" class="px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold rounded-xl transition flex items-center gap-1.5">
            <i data-lucide="check-circle-2" class="w-4 h-4"></i> Complete &amp; Encrypt Session
          </button>
        </div>
      </div>

      <!-- 5-Day Adaptive Microcycle Overview -->
      <div id="wo-weekly-cards" class="grid grid-cols-1 md:grid-cols-5 gap-4 text-xs"></div>
    </div>"""

    target_after_wearables = "    <!-- TAB: ISLAMIC FAITH LEARNING PATHS & LIVE PRAYER TIMES -->"
    assert target_after_wearables in html, "Could not locate tab-faith anchor in docs/index.html"
    if 'id="tab-workouts"' not in html:
        html = html.replace(target_after_wearables, workout_tab_html + "\n\n" + target_after_wearables, 1)

    # 4. Inject Adaptive Shoulder & Back Strength + Flexibility Engine JavaScript
    workout_js = r"""    // ADAPTIVE SHOULDER & BACK STRENGTH + FLEXIBILITY ENGINE
    window.selectedWorkoutDayIdx = 0;

    window.SHOULDER_BACK_WEEKLY_TEMPLATE = [
      {
        dayLabel: 'Monday • Session A',
        title: 'Rotator Cuff Stabilization & Scapular Retraction',
        focus: 'External Rotators, Lower Traps, Rhomboids & Thoracic Extension',
        exercises: [
          {
            name: 'Thoracic Foam Roller Extension + Open-Book Rotation',
            category: 'Flexibility & T-Spine',
            cue: 'Keep ribs down; exhale at end-range thoracic rotation to unlock overhead shoulder clearance.',
            baseSets: 3, baseReps: '8/side (3s hold)', rest: '30s',
            redMod: '3 sets × 8/side slow breath-paced mobility',
            yellowMod: '3 sets × 8/side (3s end-range pause)',
            greenMod: '3 sets × 10/side + Overhead Reach'
          },
          {
            name: 'Side-Lying or Band 90° External Rotation',
            category: 'Rotator Cuff (Infraspinatus/Teres Minor)',
            cue: 'Tuck a rolled towel between elbow and ribs; rotate forearm outward slowly (3s eccentric) without shrugging.',
            baseSets: 4, baseReps: '12–15/arm', rest: '45s',
            redMod: '3 sets × 12/arm (Light band / Isometric 5s holds, RPE 5)',
            yellowMod: '3 sets × 10/arm (-10% load, 3s eccentric, RPE 6.5)',
            greenMod: '4 sets × 12–15/arm (+2.5% load/band tension, RPE 7.5)'
          },
          {
            name: 'Chest-Supported Dumbbell Row / Seated Cable Row',
            category: 'Mid-Back (Rhomboids & Mid-Traps)',
            cue: 'Initiate pull by gliding shoulder blades back and down; pause 1s at ribcage; zero lumbar arch.',
            baseSets: 4, baseReps: '12', rest: '60s',
            redMod: '2 sets × 12 Light Band Scapular Rows + 15m Zone 2 Row (<135 BPM)',
            yellowMod: '3 sets × 10 (-10% weight, 2s isometric squeeze, +30s rest)',
            greenMod: '4 sets × 12–15 (+2.5% progressive overload, RPE 7.5)'
          },
          {
            name: 'Wall Slides with Lift-Off (Serratus Anterior)',
            category: 'Scapular Upward Rotation & Flexibility',
            cue: 'Forearms parallel on wall; slide up into Y while keeping lower ribs tucked; gently lift hands 1 inch off wall at top.',
            baseSets: 3, baseReps: '10', rest: '45s',
            redMod: '3 sets × 8 slow pain-free wall slides',
            yellowMod: '3 sets × 10 controlled tempo',
            greenMod: '3 sets × 12 with 2s top lift-off hold'
          }
        ]
      },
      {
        dayLabel: 'Tuesday • Mobility & Zone 2',
        title: 'Posterior Capsule Flexibility & Aerobic Recovery',
        focus: 'Pec Minor Release, Sleeper/Cross-Body Stretch & Parasympathetic Flush',
        exercises: [
          {
            name: 'Doorway Pec Minor & Anterior Deltoid Stretch (3 Angles)',
            category: 'Anterior Shoulder Flexibility',
            cue: 'Place forearm at 90°, 120°, and 145°; step through gently until mild chest stretch without front-shoulder pinch.',
            baseSets: 3, baseReps: '30s/angle', rest: '20s',
            redMod: '3 sets × 30s/angle + 4-4-4-4 Box Breathing',
            yellowMod: '3 sets × 30s/angle',
            greenMod: '3 sets × 35s/angle'
          },
          {
            name: 'Cross-Body Posterior Shoulder & Lat Prayer Stretch',
            category: 'Posterior Capsule & Lat Flexibility',
            cue: 'Keep shoulder blade pinned down while drawing arm across chest; follow with bench lat prayer stretch.',
            baseSets: 3, baseReps: '30s/side', rest: '20s',
            redMod: '3 sets × 30s/side gentle tension',
            yellowMod: '3 sets × 30s/side',
            greenMod: '3 sets × 35s/side'
          },
          {
            name: 'Banded Face Pulls with External Rotation',
            category: 'Rear Delts & Cuff Endurance',
            cue: 'Pull band toward forehead with thumbs pointing backward; finish in a double-bicep external rotation pose.',
            baseSets: 3, baseReps: '15', rest: '45s',
            redMod: '2 sets × 15 ultra-light band blood-flow flush',
            yellowMod: '3 sets × 12 moderate band',
            greenMod: '3 sets × 15–18 crisp tempo'
          },
          {
            name: 'Zone 2 Ergometer Rowing or Incline Treadmill Walk',
            category: 'Aerobic Base & Autonomic Recovery',
            cue: 'Nasal breathing cadence; maintain heart rate strictly in Zone 2 (<135 BPM) to boost HRV.',
            baseSets: 1, baseReps: '25–35 min', rest: '—',
            redMod: '25 min Zone 2 (<130 BPM) + 20m Therabody on upper traps/lats',
            yellowMod: '30 min Zone 2 (<135 BPM)',
            greenMod: '35 min Zone 2 + 4 × 15s crisp rowing strokes'
          }
        ]
      },
      {
        dayLabel: 'Wednesday • Session B',
        title: 'Vertical Pulling, Lower Trap Y-Raises & Overhead Stability',
        focus: 'Latissimus Dorsi, Lower Trapezius & Pain-Free Overhead Mechanics',
        exercises: [
          {
            name: 'Quadruped Thread-the-Needle & Cat-Cow',
            category: 'Thoracic & Scapular Mobility',
            cue: 'Press supporting palm firmly into floor to protract scapula while threading opposite arm underneath.',
            baseSets: 3, baseReps: '8/side', rest: '30s',
            redMod: '3 sets × 8/side slow restorative flow',
            yellowMod: '3 sets × 8/side',
            greenMod: '3 sets × 10/side'
          },
          {
            name: 'Prone or Incline Bench Y-T-W Raises',
            category: 'Lower & Middle Trapezius',
            cue: 'Thumbs up on Y, palms down on T, elbows tucked on W; lift using shoulder blades rather than upper neck traps.',
            baseSets: 3, baseReps: '8 each (Y/T/W)', rest: '60s',
            redMod: '2 sets × 6 each (bodyweight only, 2s hold)',
            yellowMod: '3 sets × 8 each (light 2.5–5 lb DBs)',
            greenMod: '3 sets × 10 each (5–10 lb DBs, RPE 7.5)'
          },
          {
            name: 'Neutral-Grip Lat Pulldown or Assisted Pull-Up',
            category: 'Vertical Back Strength (Lats & Teres Major)',
            cue: 'Keep chest proud and elbows driving straight down toward hips; stop if shoulder rounds forward at bottom.',
            baseSets: 4, baseReps: '12', rest: '60s',
            redMod: '2 sets × 12 Light Band Lat Pulldowns (control focus)',
            yellowMod: '3 sets × 10 (-10% load, 3s eccentric, +30s rest)',
            greenMod: '4 sets × 12–15 (+2.5% load/volume, RPE 8)'
          },
          {
            name: 'Bottoms-Up Kettlebell / Dumbbell Overhead Carry or Press',
            category: 'Dynamic Cuff Centration & Core',
            cue: 'Pack shoulder down into socket; walk slowly with ribs stacked over pelvis to train reflexive cuff stability.',
            baseSets: 3, baseReps: '30 sec / side', rest: '45s',
            redMod: '3 sets × 20s Farmer Carry (arms at sides, tall posture)',
            yellowMod: '3 sets × 25s/side light 90° waiter carry',
            greenMod: '4 sets × 35s/side bottoms-up carry or landmine press'
          }
        ]
      },
      {
        dayLabel: 'Thursday • Mobility & Posture',
        title: 'Desk-Decompression, Hang Mobility & Core Stability',
        focus: 'Subacromial Space Decompression & Spinal Alignment',
        exercises: [
          {
            name: 'Supported Dead Hang or Lat Bench Traction Stretch',
            category: 'Shoulder Joint & Lat Flexibility',
            cue: 'Keep feet lightly supported on floor/box if needed; breathe deeply into ribcage to decompress shoulder capsule.',
            baseSets: 3, baseReps: '20–30 sec', rest: '40s',
            redMod: '3 sets × 20s foot-supported gentle traction',
            yellowMod: '3 sets × 25s supported hang',
            greenMod: '3 sets × 30–40s active/passive scapular hang'
          },
          {
            name: 'Band Pull-Aparts (Supinated & Pronated Grip)',
            category: 'Rear Delts & Postural Endurance',
            cue: 'Keep ribs down and elbows soft; pull band to sternum while squeezing shoulder blades together.',
            baseSets: 3, baseReps: '15', rest: '45s',
            redMod: '2 sets × 15 light band',
            yellowMod: '3 sets × 15 moderate band',
            greenMod: '4 sets × 15–20 crisp tempo'
          },
          {
            name: 'Bird-Dog with 3-Second Isometric Pause',
            category: 'Contralateral Back & Core Stability',
            cue: 'Reach heel back and thumb up without rotating hips; builds deep spinal erector and lower-trap coordination.',
            baseSets: 3, baseReps: '8/side', rest: '45s',
            redMod: '3 sets × 6/side slow breath control',
            yellowMod: '3 sets × 8/side',
            greenMod: '3 sets × 10/side (3s hold)'
          }
        ]
      },
      {
        dayLabel: 'Friday • Session C',
        title: 'Posterior Chain, Unilateral Row & Rotator Cuff Balance',
        focus: 'Anti-Rotation Back Strength, Posterior Delts & Full-Range Mobility',
        exercises: [
          {
            name: 'Scapular Push-Ups + Shoulder CARs (Controlled Articular Rotations)',
            category: 'Joint Capsule Lubrication',
            cue: 'Move shoulder through largest pain-free circle slowly (6s per circle); follow with protraction/retraction push-ups.',
            baseSets: 3, baseReps: '5 CARs + 10 Push-Ups', rest: '30s',
            redMod: '3 sets × 5 slow CARs/side + wall scapular push-ups',
            yellowMod: '3 sets × 5 CARs + 10 floor/incline scapular push-ups',
            greenMod: '3 sets × 6 CARs + 12 floor scapular push-ups'
          },
          {
            name: 'Single-Arm Dumbbell Row (3-Point Stance)',
            category: 'Unilateral Lat & Rhomboid Strength',
            cue: 'Brace free hand on bench; pull dumbbell toward hip pocket while keeping shoulders square to floor.',
            baseSets: 4, baseReps: '12/arm', rest: '60s',
            redMod: '2 sets × 12/arm light band single-arm row',
            yellowMod: '3 sets × 10/arm (-10% load, +30s rest)',
            greenMod: '4 sets × 12–15/arm (+2.5% overload, RPE 8)'
          },
          {
            name: 'Incline Reverse Dumbbell Flyes or Rear-Delt Cable Fly',
            category: 'Posterior Deltoid & Infraspinatus',
            cue: 'Sweep arms wide with slight elbow bend; focus on rear shoulder and upper back without neck tension.',
            baseSets: 3, baseReps: '15', rest: '45s',
            redMod: '2 sets × 15 ultra-light DBs/band',
            yellowMod: '3 sets × 12 (-10% load)',
            greenMod: '4 sets × 15 (+2.5% load/reps)'
          },
          {
            name: 'Behind-the-Back Stick/Towel Internal & External Rotation Stretch',
            category: 'Full-Range Shoulder Flexibility',
            cue: 'Gently guide top hand upward and bottom hand downward for 25s per side; zero sharp pinching.',
            baseSets: 3, baseReps: '25s/side', rest: '20s',
            redMod: '3 sets × 25s/side gentle mobility + 20m Therabody',
            yellowMod: '3 sets × 25s/side',
            greenMod: '3 sets × 30s/side'
          }
        ]
      }
    ];

    window.setWorkoutEquipmentProfile = async function(val) {
      window.userAppState.workoutEquipment = val;
      renderAdaptiveWorkoutsTab();
      await pushCloudUserData();
    };

    window.selectWorkoutFocusDay = function(idx) {
      window.selectedWorkoutDayIdx = idx;
      renderAdaptiveWorkoutsTab();
    };

    function renderAdaptiveWorkoutsTab() {
      const tel = getWearableTelemetry();
      const gate = evaluateAutoRegulatorGate(tel);
      const completedMap = window.userAppState.workoutCompletions || {};
      const todayIso = getTodayIsoDate();

      const eqSel = document.getElementById('wo-equipment-select');
      if (eqSel && window.userAppState.workoutEquipment) {
        eqSel.value = window.userAppState.workoutEquipment;
      }

      const badge = document.getElementById('wo-gate-badge');
      const gTitle = document.getElementById('wo-gate-title');
      const gDetail = document.getElementById('wo-gate-detail');
      if (badge) {
        badge.innerText = `${gate.zone} GATE`;
        badge.className = `px-2.5 py-0.5 rounded font-extrabold text-[10px] uppercase ${gate.badgeBg}`;
      }
      if (gTitle) gTitle.innerText = gate.headline;
      if (gDetail) {
        gDetail.innerText = `WHOOP Recovery: ${tel.whoop.recovery}% • HRV: ${tel.whoop.hrv} ms • Sleep: ${tel.whoop.sleepPerf}% • Garmin Readiness: ${tel.garmin.readiness} • ACWR: ${tel.garmin.acwr}`;
      }

      const days = window.SHOULDER_BACK_WEEKLY_TEMPLATE;
      let doneCount = 0;
      days.forEach((_, idx) => {
        if (completedMap[`day_${idx}`]) doneCount++;
        const pill = document.getElementById(`wo-day-pill-${idx}`);
        if (pill) {
          const isSel = idx === window.selectedWorkoutDayIdx;
          pill.className = isSel
            ? 'px-2.5 py-1 rounded-lg bg-emerald-500 text-slate-950 font-bold transition'
            : (completedMap[`day_${idx}`]
              ? 'px-2.5 py-1 rounded-lg bg-emerald-950 text-emerald-300 border border-emerald-700 font-semibold transition'
              : 'px-2.5 py-1 rounded-lg bg-slate-950 text-slate-300 border border-slate-800 hover:border-slate-600 transition');
        }
      });

      const progPill = document.getElementById('wo-weekly-progress-pill');
      if (progPill) progPill.innerText = `${doneCount} / ${days.length} Days Completed`;

      const activeDay = days[window.selectedWorkoutDayIdx] || days[0];
      const headingEl = document.getElementById('wo-today-heading');
      if (headingEl) headingEl.innerText = `${activeDay.dayLabel}: ${activeDay.title}`;

      const exGrid = document.getElementById('wo-exercises-grid');
      if (exGrid) {
        exGrid.innerHTML = activeDay.exercises.map((ex, i) => {
          const prescription = gate.zone === 'GREEN'
            ? ex.greenMod
            : (gate.zone === 'YELLOW' ? ex.yellowMod : ex.redMod);
          const rxColor = gate.zone === 'GREEN'
            ? 'text-emerald-300 bg-emerald-950/60 border-emerald-800/70'
            : (gate.zone === 'YELLOW' ? 'text-amber-300 bg-amber-950/60 border-amber-800/70' : 'text-rose-300 bg-rose-950/60 border-rose-800/70');

          return `
            <div class="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-2 flex flex-col justify-between">
              <div class="space-y-1.5">
                <div class="flex justify-between items-center gap-2">
                  <span class="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-sky-950 text-sky-300 border border-sky-800">${ex.category}</span>
                  <span class="text-[10px] font-mono text-slate-400">Rest: ${ex.rest}</span>
                </div>
                <h5 class="font-bold text-white text-sm">${i + 1}. ${ex.name}</h5>
                <p class="text-[11px] text-slate-300 leading-relaxed">${ex.cue}</p>
              </div>
              <div class="p-2.5 rounded-lg border ${rxColor} text-[11px] font-mono">
                <strong>${gate.zone} Gate Rx:</strong> ${prescription}
              </div>
            </div>
          `;
        }).join('');
      }

      const weeklyCards = document.getElementById('wo-weekly-cards');
      if (weeklyCards) {
        weeklyCards.innerHTML = days.map((d, idx) => {
          const isDone = !!completedMap[`day_${idx}`];
          const isSel = idx === window.selectedWorkoutDayIdx;
          return `
            <div onclick="selectWorkoutFocusDay(${idx})" class="cursor-pointer p-4 rounded-2xl border transition space-y-2 ${isSel ? 'bg-slate-900 border-emerald-500/70 shadow-lg' : 'bg-slate-900/70 border-slate-800 hover:border-slate-700'}">
              <div class="flex justify-between items-center">
                <span class="text-[10px] font-mono font-bold text-emerald-400">${d.dayLabel}</span>
                <span class="text-[10px] font-mono px-1.5 py-0.5 rounded ${isDone ? 'bg-emerald-950 text-emerald-300' : 'bg-slate-950 text-slate-500'}">${isDone ? 'Done' : 'Queued'}</span>
              </div>
              <h5 class="font-bold text-white text-xs leading-snug">${d.title}</h5>
              <p class="text-[10px] text-slate-400">${d.focus}</p>
            </div>
          `;
        }).join('');
      }
      if (window.lucide) lucide.createIcons();
    }

    window.completeSelectedWorkoutDay = async function() {
      const days = window.SHOULDER_BACK_WEEKLY_TEMPLATE;
      const activeDay = days[window.selectedWorkoutDayIdx] || days[0];
      const comfort = document.getElementById('wo-comfort-score')?.value || '9';
      const note = (document.getElementById('wo-session-note')?.value || '').trim();
      const gate = evaluateAutoRegulatorGate(getWearableTelemetry());

      window.userAppState.workoutCompletions = window.userAppState.workoutCompletions || {};
      window.userAppState.workoutCompletions[`day_${window.selectedWorkoutDayIdx}`] = {
        date: getTodayIsoDate(),
        gate: gate.zone,
        comfortScore: Number(comfort),
        note
      };

      const logLine = `[${getTodayIsoDate()}] Completed ${activeDay.dayLabel}: ${activeDay.title} (${gate.zone} Gate • Comfort ${comfort}/10)${note ? ' — ' + note : ''}`;
      window.userAppState.muhasabah = window.userAppState.muhasabah
        ? `${window.userAppState.muhasabah}\n${logLine}`
        : logLine;

      if (document.getElementById('wo-session-note')) document.getElementById('wo-session-note').value = '';
      renderAllUI();
      await pushCloudUserData();
      alert(`Logged "${activeDay.title}" (${gate.zone} Gate, Comfort ${comfort}/10) to your encrypted vault!`);
    };

    window.syncWorkoutScheduleToCalendar = async function() {
      const gate = evaluateAutoRegulatorGate(getWearableTelemetry());
      window.userAppState.calendarEvents = window.userAppState.calendarEvents || [];
      window.userAppState.tasks = window.userAppState.tasks || [];

      window.SHOULDER_BACK_WEEKLY_TEMPLATE.forEach(d => {
        const evTitle = `${d.dayLabel}: ${d.title} [${gate.zone} Gate]`;
        if (!window.userAppState.calendarEvents.some(e => e.title === evTitle)) {
          window.userAppState.calendarEvents.unshift({
            id: 'ev_wo_' + Date.now() + '_' + Math.random().toString(36).slice(2, 5),
            title: evTitle,
            time: 'Asr – Maghrib Window (40m)'
          });
        }
      });

      const activeDay = window.SHOULDER_BACK_WEEKLY_TEMPLATE[window.selectedWorkoutDayIdx] || window.SHOULDER_BACK_WEEKLY_TEMPLATE[0];
      window.userAppState.tasks.unshift({
        id: 't_wo_' + Date.now(),
        title: `Shoulder & Back Training (${gate.zone} Gate): ${activeDay.title}`,
        completed: false
      });

      renderAllUI();
      await pushCloudUserData();
      switchTab('tab-calendar');
      alert(`Synced your 5-day Shoulder & Back Strength + Flexibility program (${gate.zone} Gate calibrated) to Calendar & Duties!`);
    };

    window.launchWorkoutVoiceCoach = function() {
      const tel = getWearableTelemetry();
      const gate = evaluateAutoRegulatorGate(tel);
      const activeDay = window.SHOULDER_BACK_WEEKLY_TEMPLATE[window.selectedWorkoutDayIdx] || window.SHOULDER_BACK_WEEKLY_TEMPLATE[0];

      const lines = [
        `${activeDay.dayLabel}: ${activeDay.title}.`,
        `Your live telemetry is in the ${gate.zone} Recovery Gate, with WHOOP recovery at ${tel.whoop.recovery} percent and HRV at ${tel.whoop.hrv} milliseconds.`,
        `${gate.headline}.`,
        ...activeDay.exercises.map((ex, i) => {
          const rx = gate.zone === 'GREEN' ? ex.greenMod : (gate.zone === 'YELLOW' ? ex.yellowMod : ex.redMod);
          return `Exercise ${i + 1}: ${ex.name}. Prescribed volume: ${rx}. Form cue: ${ex.cue}`;
        })
      ];

      window.activeAvItem = { title: `${activeDay.dayLabel} Voice Coach`, author: 'Adaptive Telemetry Auto-Regulator' };
      window.avMode = 'video';
      document.getElementById('av-mode-badge').innerText = 'WORKOUT VOICE COACH';
      const screen = document.getElementById('av-visual-screen');
      const card = document.getElementById('av-synth-card');
      screen.classList.remove('hidden');
      screen.classList.add('flex');
      if (card) card.className = 'bg-slate-900 border border-emerald-700/60 rounded-2xl w-full max-w-4xl overflow-hidden shadow-2xl flex flex-col h-[85vh] md:h-[600px] relative';
      document.getElementById('av-visual-topic').innerText = `${activeDay.title} (${gate.zone} Gate)`;

      window.avSynthQueue = lines;
      window.avCurrentIndex = 0;
      const modal = document.getElementById('av-synth-modal');
      modal.classList.remove('hidden');
      modal.classList.add('flex');
      requestAvWakeLock();
      if (!window.avVoices.length) initVoices();
      if (window.lucide) lucide.createIcons();
      setTimeout(() => { avPlayChunk(); }, 300);
    };"""

    if "window.SHOULDER_BACK_WEEKLY_TEMPLATE =" not in html:
        html = html.replace(
            "    // Interactive 3Q Active-Recall Quiz Handlers",
            workout_js + "\n\n    // Interactive 3Q Active-Recall Quiz Handlers",
            1,
        )

    # 5. Call renderAdaptiveWorkoutsTab() inside renderAllUI()
    if "renderAdaptiveWorkoutsTab();" not in html:
        html = html.replace(
            "      renderWearablesDashboards();",
            "      renderWearablesDashboards();\n      renderAdaptiveWorkoutsTab();",
            1,
        )

    # Validate JS syntax and all onclick handlers before writing
    script_match = re.search(r"<script>\s*(.*?)\s*</script>", html, re.DOTALL)
    assert script_match, "Missing inline <script> block"
    validate_js_syntax(script_match.group(1))

    onclicks = set(re.findall(r'onclick="([a-zA-Z0-9_]+)\(', html))
    missing = [fn for fn in sorted(onclicks) if f"window.{fn}" not in html and f"function {fn}" not in html]
    assert not missing, f"Missing JS handlers: {missing}"

    with open(INDEX_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)

    if os.path.exists(SW_PATH):
        with open(SW_PATH, "r", encoding="utf-8") as f:
            sw = f.read()
        sw = re.sub(r"hive-alignment-ota-v\d+", "hive-alignment-ota-v5", sw)
        with open(SW_PATH, "w", encoding="utf-8", newline="\n") as f:
            f.write(sw)

    print(f"Successfully added Adaptive Shoulder & Back Strength + Flexibility Engine! ({len(onclicks)} button handlers verified)")


if __name__ == "__main__":
    main()

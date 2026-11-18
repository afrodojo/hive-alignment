import os
import re

INDEX_PATH = os.path.join("docs", "index.html")

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

    # 1. Update the Tab Button text to reflect the full body coverage
    old_tab_btn = r"""      <button type="button" onclick="switchTab('tab-workouts')" id="btn-tab-workouts" class="tab-btn px-4 py-2 rounded-lg text-sm font-semibold text-emerald-400 hover:text-emerald-300 transition">Adaptive Workouts (Shoulder &amp; Back)</button>"""
    new_tab_btn = r"""      <button type="button" onclick="switchTab('tab-workouts')" id="btn-tab-workouts" class="tab-btn px-4 py-2 rounded-lg text-sm font-semibold text-emerald-400 hover:text-emerald-300 transition">Adaptive Hypertrophy (Upper/Lower Split)</button>"""
    
    if old_tab_btn in html:
        html = html.replace(old_tab_btn, new_tab_btn, 1)

    # 2. Update the top dash shortcut button
    old_top_dash_btn = r"""        <button type="button" onclick="switchTab('tab-workouts')" class="px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-bold transition flex items-center gap-1.5 shadow-sm">
          <i data-lucide="dumbbell" class="w-3.5 h-3.5"></i> Shoulder &amp; Back Routine
        </button>"""
    new_top_dash_btn = r"""        <button type="button" onclick="switchTab('tab-workouts')" class="px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-bold transition flex items-center gap-1.5 shadow-sm">
          <i data-lucide="dumbbell" class="w-3.5 h-3.5"></i> Full Body Hypertrophy
        </button>"""
    
    if old_top_dash_btn in html:
        html = html.replace(old_top_dash_btn, new_top_dash_btn, 1)

    # 3. Update the Tab Header Titles
    old_tab_header = r"""            <span class="text-[10px] font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
              <i data-lucide="dumbbell" class="w-3.5 h-3.5"></i> Telemetry-Gated Shoulder &amp; Posterior Chain Architect
            </span>
            <h3 class="text-lg font-extrabold text-white mt-0.5">Adaptive Shoulder &amp; Back Strength + Flexibility Engine</h3>
            <p class="text-xs text-slate-400 mt-0.5">Auto-calibrates sets, reps, load, and thoracic/scapular mobility to your live WHOOP Recovery Gate, HRV, and Garmin ACWR.</p>"""
    
    new_tab_header = r"""            <span class="text-[10px] font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
              <i data-lucide="dumbbell" class="w-3.5 h-3.5"></i> Telemetry-Gated 4-Day Hypertrophy Architect
            </span>
            <h3 class="text-lg font-extrabold text-white mt-0.5">Upper / Lower Split (Chest, Back, Arms, Legs, Abs)</h3>
            <p class="text-xs text-slate-400 mt-0.5">Auto-calibrates a 4-Day PHUL-style split to your live WHOOP Recovery Gate, HRV, and Garmin ACWR.</p>"""
            
    if old_tab_header in html:
        html = html.replace(old_tab_header, new_tab_header, 1)

    # 4. Update the Javascript array defining the weekly template
    # We will locate the start of `window.SHOULDER_BACK_WEEKLY_TEMPLATE = [` and replace the array contents.
    
    new_workout_array_js = r"""    window.SHOULDER_BACK_WEEKLY_TEMPLATE = [
      {
        dayLabel: 'Monday • Upper Power',
        title: 'Upper Body (Chest, Back, Arms, Shoulders)',
        focus: 'Compound Strength Focus: Bench Press, Rows, Overhead Press, Arm Hypertrophy',
        exercises: [
          {
            name: 'Barbell or Dumbbell Bench Press',
            category: 'Chest & Triceps',
            cue: 'Grip slightly outside shoulder-width, keep chest up, lower bar to level of nipples, avoid flaring elbows out.',
            baseSets: 4, baseReps: '5–8', rest: '2-3 min',
            redMod: '3 sets × 8–10 (Light Band Press or DB Floor Press, RPE 6)',
            yellowMod: '4 sets × 6–8 (-10% weight, smooth eccentric)',
            greenMod: '4 sets × 5–8 (+2.5% load, RPE 8-9)'
          },
          {
            name: 'Incline Dumbbell Press',
            category: 'Upper Chest',
            cue: 'Set bench 1-2 notches up. Control the weight down dropping elbows to 45 degree angle.',
            baseSets: 3, baseReps: '8–12', rest: '2 min',
            redMod: '2 sets × 10 (Light load)',
            yellowMod: '3 sets × 10 (-10% weight)',
            greenMod: '3 sets × 8–12 (+2.5% load, RPE 8)'
          },
          {
            name: 'Chest-Supported Row or Seated Cable Row',
            category: 'Back (Rhomboids/Lats)',
            cue: 'Initiate pull by gliding shoulder blades back and down; pause 1s at ribcage.',
            baseSets: 4, baseReps: '8–10', rest: '2 min',
            redMod: '2 sets × 12 Light Band Scapular Rows',
            yellowMod: '3 sets × 10 (-10% weight, 2s isometric squeeze)',
            greenMod: '4 sets × 8–10 (+2.5% load, RPE 8)'
          },
          {
            name: 'Pull-Ups or Lat Pulldowns',
            category: 'Vertical Back (Lats)',
            cue: 'Grip outside shoulder-width, pull until chin over bar. Pull elbows down and back.',
            baseSets: 3, baseReps: '6–12', rest: '2 min',
            redMod: '2 sets × 12 Light Band Pulldowns',
            yellowMod: '3 sets × 10 (-10% load)',
            greenMod: '3 sets × 6–12 (Weighted if easy)'
          },
          {
            name: 'Dumbbell Overhead Press & Lateral Raises',
            category: 'Shoulders (Anterior/Lateral Delts)',
            cue: 'Press dumbbells overhead; superset with lateral raises keeping slight bend in elbows.',
            baseSets: 3, baseReps: '8–12 (OHP) + 15 (Raises)', rest: '2 min',
            redMod: '2 sets × 12 light raises only',
            yellowMod: '3 sets × 10 (OHP) + 12 raises',
            greenMod: '3 sets × 8–12 (OHP) + 15 raises'
          },
          {
            name: 'Incline Dumbbell Curl & Overhead Triceps Extension',
            category: 'Biceps & Triceps (Arms)',
            cue: 'Superset. Full stretch at bottom of curls; lock elbows in place for triceps.',
            baseSets: 3, baseReps: '10–12 each', rest: '90s',
            redMod: '2 sets × 12 each (Blood flow focus)',
            yellowMod: '3 sets × 12 each (-10% weight)',
            greenMod: '3 sets × 10–12 each (Push to near failure)'
          }
        ]
      },
      {
        dayLabel: 'Tuesday • Lower Power',
        title: 'Lower Body (Quads, Hams, Glutes, Calves, Abs)',
        focus: 'Compound Leg Strength: Squats, Deadlifts, Core Stability',
        exercises: [
          {
            name: 'Barbell Back Squat or Goblet Squat',
            category: 'Quads & Glutes',
            cue: 'Keep chest up, break at hips and knees simultaneously. Hit parallel or below.',
            baseSets: 4, baseReps: '5–8', rest: '3-4 min',
            redMod: '3 sets × 10 (Bodyweight or Light Goblet Squat)',
            yellowMod: '3 sets × 6–8 (-10% weight)',
            greenMod: '4 sets × 5–8 (+2.5% load, RPE 8)'
          },
          {
            name: 'Romanian Deadlift (RDL)',
            category: 'Hamstrings & Glutes',
            cue: 'Hinge at the hips, keeping the bar close to the legs. Squeeze glutes at the top.',
            baseSets: 3, baseReps: '8–10', rest: '2-3 min',
            redMod: '2 sets × 12 (Very light DB RDLs)',
            yellowMod: '3 sets × 10 (-10% weight)',
            greenMod: '3 sets × 8–10 (+2.5% load)'
          },
          {
            name: 'Leg Press or Bulgarian Split Squat',
            category: 'Quads & Unilateral Strength',
            cue: 'Control the eccentric. For split squats, keep torso upright to target quads.',
            baseSets: 3, baseReps: '8–12', rest: '2 min',
            redMod: '2 sets × 10 (Bodyweight split squats)',
            yellowMod: '3 sets × 10 (-10% weight)',
            greenMod: '3 sets × 8–12 (Push intensity)'
          },
          {
            name: 'Leg Curl (Lying or Seated)',
            category: 'Hamstring Isolation',
            cue: 'Full range of motion, squeeze hamstrings hard at the contracted position.',
            baseSets: 3, baseReps: '10–15', rest: '90s',
            redMod: '2 sets × 15 (Light band leg curls)',
            yellowMod: '3 sets × 12 (-10% load)',
            greenMod: '3 sets × 10–15 (Hold peak contraction)'
          },
          {
            name: 'Standing Calf Raises',
            category: 'Calves',
            cue: 'Elevate toes on weight plate, press up on big toes, full stretch at the bottom.',
            baseSets: 4, baseReps: '10–15', rest: '90s',
            redMod: '3 sets × 15 (Bodyweight only)',
            yellowMod: '4 sets × 15 (Moderate weight)',
            greenMod: '4 sets × 10–15 (Heavy with pause)'
          },
          {
            name: 'Hanging Knee Raises or Ab-Wheel Rollouts',
            category: 'Core (Abs)',
            cue: 'Control the movement, focus on contracting the abdominals, avoid swinging.',
            baseSets: 3, baseReps: '10–15', rest: '60s',
            redMod: '2 sets × 10 (Plank 30s instead)',
            yellowMod: '3 sets × 12',
            greenMod: '3 sets × 15 (Slow eccentric)'
          }
        ]
      },
      {
        dayLabel: 'Wednesday • Active Recovery',
        title: 'Zone 2 Cardio & Full Body Mobility',
        focus: 'Aerobic Base & Autonomic Recovery',
        exercises: [
          {
            name: 'Zone 2 Ergometer Rowing or Incline Treadmill Walk',
            category: 'Aerobic Base & Autonomic Recovery',
            cue: 'Nasal breathing cadence; maintain heart rate strictly in Zone 2 (<135 BPM) to boost HRV.',
            baseSets: 1, baseReps: '30–45 min', rest: '—',
            redMod: '30 min Zone 2 (<130 BPM) + 15m Therabody',
            yellowMod: '35 min Zone 2 (<135 BPM)',
            greenMod: '45 min Zone 2 + Core stretching'
          }
        ]
      },
      {
        dayLabel: 'Thursday • Upper Hypertrophy',
        title: 'Upper Body (Chest, Back, Arms, Shoulders)',
        focus: 'Hypertrophy Focus: Higher Reps, Isolation, and Pump',
        exercises: [
          {
            name: 'Incline Barbell or Dumbbell Press',
            category: 'Upper Chest & Triceps',
            cue: 'Smooth eccentric, explosive concentric. Stop just shy of lockout to keep tension on pecs.',
            baseSets: 4, baseReps: '8–12', rest: '2 min',
            redMod: '3 sets × 12 (Light DB Press)',
            yellowMod: '4 sets × 10 (-10% weight)',
            greenMod: '4 sets × 8–12 (RPE 8-9)'
          },
          {
            name: 'Cable Crossover or Machine Fly',
            category: 'Chest Isolation',
            cue: 'Squeeze pecs together at the top, slight bend in elbows.',
            baseSets: 3, baseReps: '12–15', rest: '90s',
            redMod: '2 sets × 15 (Light band flyes)',
            yellowMod: '3 sets × 15 (-10% weight)',
            greenMod: '3 sets × 12–15 (Hold peak contraction)'
          },
          {
            name: 'Seated Cable Row',
            category: 'Mid-Back (Rhomboids/Traps)',
            cue: 'Pull to lower chest, retract scapula hard.',
            baseSets: 4, baseReps: '8–12', rest: '2 min',
            redMod: '3 sets × 12 (Light band rows)',
            yellowMod: '4 sets × 12 (-10% weight)',
            greenMod: '4 sets × 8–12'
          },
          {
            name: 'One Arm Dumbbell Row',
            category: 'Lats & Unilateral Back',
            cue: 'Pull towards the hip, stretch fully at the bottom.',
            baseSets: 3, baseReps: '10–12 per arm', rest: '90s',
            redMod: '2 sets × 12 (Very light weight)',
            yellowMod: '3 sets × 12 (-10% weight)',
            greenMod: '3 sets × 10–12 (Heavy)'
          },
          {
            name: 'Upright Cable Row or Dumbbell Lateral Raise',
            category: 'Shoulders (Lateral Delts)',
            cue: 'Pull elbows high for upright rows, lead with elbows for lateral raises.',
            baseSets: 3, baseReps: '12–15', rest: '90s',
            redMod: '2 sets × 15 (Light band raises)',
            yellowMod: '3 sets × 15 (-10% weight)',
            greenMod: '3 sets × 12–15'
          },
          {
            name: 'Cable Curl & Skullcrusher (EZ Bar)',
            category: 'Biceps & Triceps (Arms)',
            cue: 'Superset. Constant tension on cable curls; flare elbows slightly for skullcrushers to hit long head.',
            baseSets: 3, baseReps: '12–15 each', rest: '90s',
            redMod: '2 sets × 15 each (Light pump)',
            yellowMod: '3 sets × 15 each (-10% weight)',
            greenMod: '3 sets × 12–15 each (Take near failure)'
          }
        ]
      },
      {
        dayLabel: 'Friday • Lower Hypertrophy',
        title: 'Lower Body (Quads, Hams, Glutes, Calves, Abs)',
        focus: 'Hypertrophy Focus: Volume, Isolation, and Burn',
        exercises: [
          {
            name: 'Front Squat or Leg Press',
            category: 'Quads Focus',
            cue: 'Deep range of motion, focus on pushing through the mid-foot to engage quads.',
            baseSets: 4, baseReps: '8–12', rest: '2-3 min',
            redMod: '3 sets × 12 (Light leg press)',
            yellowMod: '4 sets × 10 (-10% weight)',
            greenMod: '4 sets × 8–12'
          },
          {
            name: 'Barbell Lunge or Walking Lunge',
            category: 'Quads & Glutes',
            cue: 'Long strides for glute focus, short strides for quad focus. Keep torso upright.',
            baseSets: 3, baseReps: '10-12 per leg', rest: '2 min',
            redMod: '2 sets × 10 (Bodyweight lunges)',
            yellowMod: '3 sets × 10 per leg (Light DBs)',
            greenMod: '3 sets × 10-12 per leg'
          },
          {
            name: 'Leg Extension',
            category: 'Quad Isolation',
            cue: 'Pause at the top, control the negative. Burn out the quads.',
            baseSets: 3, baseReps: '12–15', rest: '90s',
            redMod: '2 sets × 15 (Light weight)',
            yellowMod: '3 sets × 15 (-10% load)',
            greenMod: '3 sets × 12–15'
          },
          {
            name: 'Leg Curl',
            category: 'Hamstring Isolation',
            cue: 'Keep hips down on the pad, curl weight smoothly.',
            baseSets: 3, baseReps: '12–15', rest: '90s',
            redMod: '2 sets × 15 (Light weight)',
            yellowMod: '3 sets × 15 (-10% load)',
            greenMod: '3 sets × 12–15'
          },
          {
            name: 'Seated Calf Raises',
            category: 'Soleus (Calves)',
            cue: 'Slow eccentric, deep stretch, pause at top.',
            baseSets: 4, baseReps: '15–20', rest: '90s',
            redMod: '3 sets × 20 (Light)',
            yellowMod: '4 sets × 20 (-10% load)',
            greenMod: '4 sets × 15–20 (Heavy)'
          },
          {
            name: 'Cable Crunches or Weighted Plank',
            category: 'Core (Abs)',
            cue: 'Round the back for cable crunches to engage abs fully.',
            baseSets: 3, baseReps: '15-20 (or 60s hold)', rest: '60s',
            redMod: '2 sets × 45s plank',
            yellowMod: '3 sets × 15 crunches',
            greenMod: '3 sets × 20 crunches (Heavy)'
          }
        ]
      }
    ];"""

    start_idx = html.find("    window.SHOULDER_BACK_WEEKLY_TEMPLATE = [")
    if start_idx != -1:
        end_idx = html.find("    window.setWorkoutEquipmentProfile = async function(val) {")
        if end_idx != -1:
            html = html[:start_idx] + new_workout_array_js + "\n\n" + html[end_idx:]

    # Validate JS syntax and all onclick handlers before writing
    script_match = re.search(r"<script>\s*(.*?)\s*</script>", html, re.DOTALL)
    assert script_match, "Missing inline <script> block"
    validate_js_syntax(script_match.group(1))

    onclicks = set(re.findall(r'onclick="([a-zA-Z0-9_]+)\(', html))
    missing = [fn for fn in sorted(onclicks) if f"window.{fn}" not in html and f"function {fn}" not in html]
    assert not missing, f"Missing JS handlers: {missing}"

    with open(INDEX_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    
    print("Successfully patched index.html with the Full Body Hypertrophy program.")


if __name__ == "__main__":
    main()

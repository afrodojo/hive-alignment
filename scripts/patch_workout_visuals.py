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

    # 1. Inject Exercise Form Infographic & Video Demonstration Modal right after <!-- MODALS -->
    exercise_modal_html = r"""  <!-- EXERCISE FORM INFOGRAPHIC & VIDEO DEMONSTRATION MODAL -->
  <div id="exercise-guide-modal" class="fixed inset-0 bg-slate-950/95 backdrop-blur-md z-[1255] hidden flex items-center justify-center p-4 overflow-y-auto">
    <div class="bg-slate-900 border border-emerald-700/60 rounded-2xl max-w-4xl w-full p-6 space-y-5 shadow-2xl relative my-6">
      <div class="flex justify-between items-start border-b border-slate-800 pb-3 gap-3">
        <div class="min-w-0">
          <span id="ex-guide-category-badge" class="text-[10px] font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
            <i data-lucide="activity" class="w-3.5 h-3.5"></i> Biomechanics Infographic &amp; Form Video
          </span>
          <h3 id="ex-guide-title" class="text-lg font-extrabold text-white mt-0.5 truncate">Exercise Name</h3>
        </div>
        <div class="flex items-center gap-2 flex-shrink-0">
          <a id="ex-guide-yt-search-link" href="https://www.youtube.com/" target="_blank" rel="noopener noreferrer" class="px-3 py-1.5 bg-rose-600 hover:bg-rose-500 text-white rounded-xl text-xs font-bold flex items-center gap-1">
            <i data-lucide="youtube" class="w-3.5 h-3.5"></i> YouTube Demos &nearr;
          </a>
          <button type="button" onclick="closeExerciseGuideModal()" class="text-slate-400 hover:text-white text-xl leading-none px-1">&times;</button>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-5 text-xs">
        <!-- Left 5 Cols: Anatomical Muscle Map & Tempo Infographic -->
        <div class="lg:col-span-5 bg-slate-950 border border-slate-800 rounded-2xl p-4 flex flex-col justify-between space-y-3">
          <div class="flex justify-between items-center">
            <span class="text-[10px] font-bold uppercase tracking-wider text-sky-400">Anatomical Activation Map</span>
            <span id="ex-guide-tempo-badge" class="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800/70">Tempo: 3-1-1-0</span>
          </div>

          <!-- Dynamic SVG Anterior + Posterior Muscle Activation Diagram -->
          <div id="ex-guide-svg-container" class="flex items-center justify-center py-2 bg-slate-900/70 rounded-xl border border-slate-800/80"></div>

          <div class="space-y-1.5 text-[11px]">
            <div class="flex items-center gap-2">
              <span class="w-3 h-3 rounded-sm bg-emerald-500 inline-block flex-shrink-0"></span>
              <span class="text-slate-300"><strong>Primary Drivers:</strong> <span id="ex-guide-primary-muscles" class="text-emerald-300 font-semibold">—</span></span>
            </div>
            <div class="flex items-center gap-2">
              <span class="w-3 h-3 rounded-sm bg-sky-400 inline-block flex-shrink-0"></span>
              <span class="text-slate-300"><strong>Synergists / Stabilizers:</strong> <span id="ex-guide-secondary-muscles" class="text-sky-300 font-semibold">—</span></span>
            </div>
          </div>

          <div id="ex-guide-rx-box" class="p-2.5 rounded-xl bg-emerald-950/50 border border-emerald-800/70 text-[11px] font-mono text-emerald-200">
            Prescribed Sets &amp; Reps
          </div>
        </div>

        <!-- Right 7 Cols: Video Demonstration Player + Step-by-Step Infographic Cues -->
        <div class="lg:col-span-7 space-y-3.5">
          <!-- Embedded Video Demo Player -->
          <div class="space-y-2">
            <div class="relative w-full overflow-hidden rounded-xl border border-slate-800 bg-black" style="padding-top: 52%;">
              <iframe id="ex-guide-video-iframe" src="" title="Exercise Form Demonstration Video" class="absolute inset-0 w-full h-full" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
            </div>
            <!-- Pin Custom YouTube Form Video URL -->
            <div class="flex gap-2">
              <input type="url" id="ex-guide-custom-yt-input" placeholder="Paste any YouTube form tutorial URL to pin to this exercise..." class="flex-grow bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-[11px] text-slate-200 font-mono focus:outline-none focus:border-emerald-500">
              <button type="button" onclick="saveCustomExerciseVideoUrl()" class="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold rounded-xl text-[11px] flex-shrink-0">
                Pin Video
              </button>
            </div>
          </div>

          <!-- 3-Phase Execution & Mistake Prevention Infographic Cards -->
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-2 text-[11px]">
            <div class="p-2.5 bg-slate-950 rounded-xl border border-slate-800 space-y-1">
              <span class="text-[10px] font-bold uppercase text-emerald-400 block">1. Setup &amp; Brace</span>
              <p id="ex-guide-step1" class="text-slate-300 leading-snug">—</p>
            </div>
            <div class="p-2.5 bg-slate-950 rounded-xl border border-slate-800 space-y-1">
              <span class="text-[10px] font-bold uppercase text-sky-400 block">2. Execution &amp; Path</span>
              <p id="ex-guide-step2" class="text-slate-300 leading-snug">—</p>
            </div>
            <div class="p-2.5 bg-slate-950 rounded-xl border border-rose-900/50 space-y-1">
              <span class="text-[10px] font-bold uppercase text-rose-400 block">3. Avoid Mistake</span>
              <p id="ex-guide-avoid" class="text-slate-300 leading-snug">—</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>"""

    if 'id="exercise-guide-modal"' not in html:
        html = html.replace("  <!-- MODALS -->", "  <!-- MODALS -->\n" + exercise_modal_html, 1)

    # 2. Inject Biomechanical Metadata Lookup, Anatomical SVG Infographic Renderer & Exercise Modal JS
    visual_workout_js = r"""    // EXERCISE BIOMECHANICS INFOGRAPHIC & VIDEO DEMONSTRATION ENGINE
    window.activeGuideExercise = null;

    window.EXERCISE_BIOMECHANICS_DB = {
      'bench press': {
        primary: ['chest'], secondary: ['shoulders', 'triceps'],
        tempo: '3-1-1-0 (3s Lower, 1s Chest Pause)',
        step1: 'Retract and depress shoulder blades into the bench; plant feet flat and brace core.',
        step2: 'Lower bar/DBs with elbows tucked at ~45° to mid-chest, then drive up without losing upper-back tightness.',
        avoid: 'Flaring elbows out to 90° or bouncing weight off the sternum.',
        videoQuery: 'barbell dumbbell bench press proper form tutorial'
      },
      'incline': {
        primary: ['chest', 'shoulders'], secondary: ['triceps'],
        tempo: '3-1-1-0 (Controlled Upper-Pec Stretch)',
        step1: 'Set bench to 30° (1–2 notches); keep upper back pinned and ribs down.',
        step2: 'Lower weights toward upper clavicle/chest line with elbows at 45°, press smoothly to near lockout.',
        avoid: 'Setting bench angle too steep (>45°), which shifts load away from upper pecs onto front delts.',
        videoQuery: 'incline dumbbell press proper form upper chest tutorial'
      },
      'fly': {
        primary: ['chest'], secondary: ['shoulders', 'biceps'],
        tempo: '3-1-1-1 (1s Peak Squeeze)',
        step1: 'Set slight elbow bend (~15°) and keep chest proud with scapulae retracted.',
        step2: 'Arc arms wide until a deep stretch is felt across pecs, then sweep together squeezing inner chest.',
        avoid: 'Turning the fly into a press or over-stretching past shoulder comfort.',
        videoQuery: 'cable crossover dumbbell fly proper form tutorial'
      },
      'row': {
        primary: ['back'], secondary: ['biceps', 'shoulders'],
        tempo: '2-1-1-1 (1s Scapular Squeeze)',
        step1: 'Brace torso/chest firmly; let shoulder blades protract slightly at bottom for full lat/rhomboid stretch.',
        step2: 'Drive elbows back toward hip pockets, squeezing shoulder blades together at peak contraction.',
        avoid: 'Jerking torso with momentum or shrugging upper traps toward ears.',
        videoQuery: 'chest supported dumbbell seated cable row proper form'
      },
      'pull-up': {
        primary: ['back'], secondary: ['biceps', 'shoulders', 'abs'],
        tempo: '3-0-1-1 (Full Dead-Hang Control)',
        step1: 'Grip slightly wider than shoulder-width; depress shoulders away from ears before bending elbows.',
        step2: 'Drive elbows down toward ribs until chest/chin clears bar; lower under 3s control.',
        avoid: 'Half-reps or letting shoulders roll forward at the bottom of the hang.',
        videoQuery: 'lat pulldown pull up proper form back hypertrophy'
      },
      'overhead press': {
        primary: ['shoulders'], secondary: ['triceps', 'abs'],
        tempo: '2-0-1-0 (Stacked Rib-to-Pelvis)',
        step1: 'Squeeze glutes and brace abs so lower back stays neutral; hold DBs/bar just in front of shoulders.',
        step2: 'Press vertically in a straight line, finishing with biceps aligned beside ears.',
        avoid: 'Hyperextending the lower back or flaring ribs as weights go overhead.',
        videoQuery: 'dumbbell overhead shoulder press proper form tutorial'
      },
      'lateral raise': {
        primary: ['shoulders'], secondary: ['back'],
        tempo: '2-1-1-1 (1s Top Pause)',
        step1: 'Hinge forward ~10° with soft elbows and weights resting slightly in front of thighs.',
        step2: 'Sweep weights out toward the walls (scapular plane) leading with elbows up to shoulder height.',
        avoid: 'Swinging torso or shrugging traps above shoulder level.',
        videoQuery: 'dumbbell lateral raise proper form side delts'
      },
      'curl': {
        primary: ['biceps'], secondary: ['shoulders'],
        tempo: '3-0-1-1 (3s Eccentric Stretch)',
        step1: 'Pin elbows stationary at your sides (or braced on incline bench) with palms supinated.',
        step2: 'Curl smoothly to full bicep contraction, pause 1s, and lower for a full 3-second stretch.',
        avoid: 'Swinging elbows forward or rocking hips to lift heavier weight.',
        videoQuery: 'incline dumbbell curl cable curl proper form biceps'
      },
      'triceps': {
        primary: ['triceps'], secondary: ['shoulders'],
        tempo: '3-1-1-0 (Deep Long-Head Stretch)',
        step1: 'Lock upper arms stationary overhead or angled slightly back; brace core.',
        step2: 'Bend strictly at the elbow for a deep tricep stretch, then extend smoothly to full contraction.',
        avoid: 'Flaring elbows wide or letting shoulders drift during extension.',
        videoQuery: 'overhead triceps extension skullcrusher proper form'
      },
      'squat': {
        primary: ['quads', 'glutes'], secondary: ['hamstrings', 'abs'],
        tempo: '3-1-1-0 (3s Controlled Descent)',
        step1: 'Stand shoulder-width with toes angled ~15–30° out; take a 360° diaphragmatic breath and brace core.',
        step2: 'Break at hips and knees simultaneously, tracking knees over mid-foot to parallel or below, then drive up.',
        avoid: 'Letting knees cave inward (valgus) or heels lift off the floor.',
        videoQuery: 'barbell back squat goblet squat proper form tutorial'
      },
      'deadlift': {
        primary: ['hamstrings', 'glutes', 'back'], secondary: ['abs'],
        tempo: '3-1-1-0 (Hip-Hinge Tension)',
        step1: 'Soften knees (~15°), lock spine neutral, and pull lats tight as if squeezing oranges in armpits.',
        step2: 'Push hips straight backward while keeping bar/DBs skimming thighs until hamstrings reach full stretch; drive hips forward.',
        avoid: 'Rounding the lower back or squatting the weight instead of hinging at the hips.',
        videoQuery: 'romanian deadlift RDL proper form hamstrings glutes'
      },
      'lunge': {
        primary: ['quads', 'glutes'], secondary: ['hamstrings', 'abs'],
        tempo: '2-1-1-0 (Split-Stance Balance)',
        step1: 'Take a hip-width stride (not on a tightrope) with torso tall and core braced.',
        step2: 'Lower back knee smoothly toward floor until both knees reach ~90°, then drive through front mid-foot.',
        avoid: 'Front knee collapsing inward or slamming rear knee onto floor.',
        videoQuery: 'bulgarian split squat walking lunge proper form'
      },
      'leg extension': {
        primary: ['quads'], secondary: ['abs'],
        tempo: '2-1-1-1 (1s Peak Quad Squeeze)',
        step1: 'Align knee joint directly with the machine pivot axis and grip handles firmly to lock hips down.',
        step2: 'Extend knees smoothly to full contraction, pause 1s at top, and lower under control.',
        avoid: 'Kicking weight up with momentum or lifting glutes off the seat.',
        videoQuery: 'leg extension machine proper form quads hypertrophy'
      },
      'leg curl': {
        primary: ['hamstrings'], secondary: ['calves'],
        tempo: '3-0-1-1 (Hips Pinned to Pad)',
        step1: 'Align knee joint with machine pivot and press hips firmly into the bench pad.',
        step2: 'Curl heels toward glutes smoothly, squeeze hamstrings at top, and control the 3s return.',
        avoid: 'Arching lower back or lifting hips off the pad as fatigue sets in.',
        videoQuery: 'lying seated leg curl proper form hamstrings'
      },
      'calf': {
        primary: ['calves'], secondary: ['hamstrings'],
        tempo: '2-2-1-1 (2s Bottom Stretch Pause)',
        step1: 'Place balls of feet on edge of platform with ankles aligned and knees straight (standing) or 90° (seated).',
        step2: 'Lower heels into a full 2-second stretch at the bottom (eliminating Achilles bounce), then press onto big toes.',
        avoid: 'Bouncing rapidly through partial reps without pausing at the bottom.',
        videoQuery: 'standing seated calf raises proper form hypertrophy'
      },
      'abs': {
        primary: ['abs'], secondary: ['shoulders'],
        tempo: '2-1-2-1 (Spinal Flexion / Anti-Extension)',
        step1: 'Tuck pelvis slightly (posterior pelvic tilt) and exhale fully to engage transverse abdominis.',
        step2: 'Curl ribcage toward pelvis (crunches/raises) or hold rigid plank alignment without lumbar sag.',
        avoid: 'Pulling with hip flexors or letting lower back arch during leg lowers/rollouts.',
        videoQuery: 'hanging knee raises cable crunch proper form abs'
      },
      'rotator': {
        primary: ['shoulders', 'back'], secondary: ['abs'],
        tempo: '3-1-2-1 (Strict Cuff Isolation)',
        step1: 'Tuck towel between elbow and ribs; set shoulder blade back and down before rotating.',
        step2: 'Rotate forearm smoothly through pain-free arc without torso twist, holding 1s at end range.',
        avoid: 'Using heavy weight that recruits deltoids/momentum instead of deep rotator cuff.',
        videoQuery: 'rotator cuff external rotation face pull proper form'
      },
      'zone 2': {
        primary: ['back', 'quads', 'hamstrings'], secondary: ['abs', 'calves'],
        tempo: 'Steady Nasal Cadence (<135 BPM)',
        step1: 'Set damper/incline for smooth conversational effort where nasal breathing stays sustainable.',
        step2: 'Maintain relaxed shoulders and rhythmic stroke/stride for 25–45 minutes to boost parasympathetic HRV.',
        avoid: 'Drifting into Zone 3/4 threshold heart rate on an active recovery day.',
        videoQuery: 'zone 2 rowing machine proper form technique'
      }
    };

    function getExerciseBiomechanics(ex) {
      const hay = `${ex.name || ''} ${ex.category || ''}`.toLowerCase();
      if (hay.includes('rotator') || hay.includes('face pull') || hay.includes('wall slide') || hay.includes('y-t-w') || hay.includes('car') || hay.includes('pull-apart')) {
        return window.EXERCISE_BIOMECHANICS_DB['rotator'];
      }
      if (hay.includes('incline') && (hay.includes('press') || hay.includes('bench'))) return window.EXERCISE_BIOMECHANICS_DB['incline'];
      if (hay.includes('bench') || hay.includes('chest press')) return window.EXERCISE_BIOMECHANICS_DB['bench press'];
      if (hay.includes('fly') || hay.includes('crossover')) return window.EXERCISE_BIOMECHANICS_DB['fly'];
      if (hay.includes('row')) return window.EXERCISE_BIOMECHANICS_DB['row'];
      if (hay.includes('pull-up') || hay.includes('pulldown') || hay.includes('lat') || hay.includes('hang')) return window.EXERCISE_BIOMECHANICS_DB['pull-up'];
      if (hay.includes('overhead') || hay.includes('carry')) return window.EXERCISE_BIOMECHANICS_DB['overhead press'];
      if (hay.includes('lateral')) return window.EXERCISE_BIOMECHANICS_DB['lateral raise'];
      if (hay.includes('leg curl')) return window.EXERCISE_BIOMECHANICS_DB['leg curl'];
      if (hay.includes('curl')) return window.EXERCISE_BIOMECHANICS_DB['curl'];
      if (hay.includes('tricep') || hay.includes('skullcrusher')) return window.EXERCISE_BIOMECHANICS_DB['triceps'];
      if (hay.includes('deadlift') || hay.includes('rdl') || hay.includes('bird-dog')) return window.EXERCISE_BIOMECHANICS_DB['deadlift'];
      if (hay.includes('lunge') || hay.includes('split squat')) return window.EXERCISE_BIOMECHANICS_DB['lunge'];
      if (hay.includes('leg extension')) return window.EXERCISE_BIOMECHANICS_DB['leg extension'];
      if (hay.includes('squat') || hay.includes('leg press')) return window.EXERCISE_BIOMECHANICS_DB['squat'];
      if (hay.includes('calf')) return window.EXERCISE_BIOMECHANICS_DB['calf'];
      if (hay.includes('abs') || hay.includes('crunch') || hay.includes('plank') || hay.includes('knee raise')) return window.EXERCISE_BIOMECHANICS_DB['abs'];
      if (hay.includes('zone 2') || hay.includes('stretch') || hay.includes('thoracic')) return window.EXERCISE_BIOMECHANICS_DB['zone 2'];
      return window.EXERCISE_BIOMECHANICS_DB['row'];
    }

    function buildAnatomicalMuscleSvg(primaryList, secondaryList, compact) {
      const fillFor = (group) => {
        if (primaryList.includes(group)) return '#10b981';   // Emerald-500 Primary
        if (secondaryList.includes(group)) return '#38bdf8'; // Sky-400 Secondary
        return '#1e293b';                                     // Slate-800 Inactive
      };
      const w = compact ? 92 : 230;
      const h = compact ? 64 : 165;
      return `
        <svg width="${w}" height="${h}" viewBox="0 0 230 165" xmlns="http://www.w3.org/2000/svg" aria-label="Muscle Activation Map">
          <!-- FRONT (ANTERIOR) SILHOUETTE -->
          <text x="56" y="12" fill="#94a3b8" font-size="9" font-family="monospace" text-anchor="middle">FRONT</text>
          <circle cx="56" cy="24" r="7" fill="#334155"/>
          <!-- Shoulders (Front Delts) -->
          <ellipse cx="36" cy="39" rx="7" ry="6" fill="${fillFor('shoulders')}"/>
          <ellipse cx="76" cy="39" rx="7" ry="6" fill="${fillFor('shoulders')}"/>
          <!-- Chest (Pectorals) -->
          <path d="M41 35 H55 V49 H42 Z" rx="3" fill="${fillFor('chest')}"/>
          <path d="M57 35 H71 V49 H57 Z" rx="3" fill="${fillFor('chest')}"/>
          <!-- Abs (Rectus Abdominis & Obliques) -->
          <rect x="46" y="51" width="20" height="26" rx="4" fill="${fillFor('abs')}"/>
          <!-- Biceps / Arms -->
          <rect x="27" y="45" width="7" height="22" rx="3.5" fill="${fillFor('biceps')}"/>
          <rect x="78" y="45" width="7" height="22" rx="3.5" fill="${fillFor('biceps')}"/>
          <!-- Quads -->
          <rect x="42" y="81" width="12" height="36" rx="5" fill="${fillFor('quads')}"/>
          <rect x="58" y="81" width="12" height="36" rx="5" fill="${fillFor('quads')}"/>
          <!-- Shins / Tibialis -->
          <rect x="44" y="120" width="9" height="30" rx="4" fill="#1e293b"/>
          <rect x="59" y="120" width="9" height="30" rx="4" fill="#1e293b"/>

          <!-- Divider -->
          <line x1="115" y1="14" x2="115" y2="152" stroke="#1e293b" stroke-dasharray="3,3"/>

          <!-- BACK (POSTERIOR) SILHOUETTE -->
          <text x="174" y="12" fill="#94a3b8" font-size="9" font-family="monospace" text-anchor="middle">BACK</text>
          <circle cx="174" cy="24" r="7" fill="#334155"/>
          <!-- Rear Delts / Shoulders -->
          <ellipse cx="154" cy="39" rx="7" ry="6" fill="${fillFor('shoulders')}"/>
          <ellipse cx="194" cy="39" rx="7" ry="6" fill="${fillFor('shoulders')}"/>
          <!-- Upper/Mid Back & Lats -->
          <path d="M159 34 H189 L184 68 H164 Z" fill="${fillFor('back')}"/>
          <!-- Triceps -->
          <rect x="145" y="45" width="7" height="22" rx="3.5" fill="${fillFor('triceps')}"/>
          <rect x="196" y="45" width="7" height="22" rx="3.5" fill="${fillFor('triceps')}"/>
          <!-- Glutes -->
          <rect x="160" y="70" width="13" height="14" rx="5" fill="${fillFor('glutes')}"/>
          <rect x="175" y="70" width="13" height="14" rx="5" fill="${fillFor('glutes')}"/>
          <!-- Hamstrings -->
          <rect x="160" y="86" width="12" height="31" rx="5" fill="${fillFor('hamstrings')}"/>
          <rect x="176" y="86" width="12" height="31" rx="5" fill="${fillFor('hamstrings')}"/>
          <!-- Calves -->
          <rect x="161" y="120" width="10" height="28" rx="4.5" fill="${fillFor('calves')}"/>
          <rect x="177" y="120" width="10" height="28" rx="4.5" fill="${fillFor('calves')}"/>
        </svg>
      `;
    }

    window.openExerciseGuideModal = function(dayIdx, exIdx) {
      const days = window.SHOULDER_BACK_WEEKLY_TEMPLATE || [];
      const day = days[dayIdx] || days[0];
      const ex = day?.exercises?.[exIdx];
      if (!ex) return;

      window.activeGuideExercise = ex;
      const bio = getExerciseBiomechanics(ex);
      const gate = evaluateAutoRegulatorGate(getWearableTelemetry());
      const rx = gate.zone === 'GREEN' ? ex.greenMod : (gate.zone === 'YELLOW' ? ex.yellowMod : ex.redMod);

      document.getElementById('ex-guide-category-badge').innerText = `${ex.category} • Visual Form Infographic`;
      document.getElementById('ex-guide-title').innerText = ex.name;
      document.getElementById('ex-guide-tempo-badge').innerText = `Tempo: ${bio.tempo}`;
      document.getElementById('ex-guide-svg-container').innerHTML = buildAnatomicalMuscleSvg(bio.primary, bio.secondary, false);
      document.getElementById('ex-guide-primary-muscles').innerText = bio.primary.map(m => m.toUpperCase()).join(', ');
      document.getElementById('ex-guide-secondary-muscles').innerText = bio.secondary.map(m => m.toUpperCase()).join(', ');
      document.getElementById('ex-guide-rx-box').innerHTML = `<strong>${gate.zone} Recovery Gate Rx:</strong> ${rx} (Rest: ${ex.rest})`;

      document.getElementById('ex-guide-step1').innerText = bio.step1;
      document.getElementById('ex-guide-step2').innerText = `${bio.step2} ${ex.cue || ''}`;
      document.getElementById('ex-guide-avoid').innerText = bio.avoid;

      const customMap = window.userAppState.customExerciseVideos || {};
      const savedUrl = customMap[ex.name] || '';
      const urlInput = document.getElementById('ex-guide-custom-yt-input');
      if (urlInput) urlInput.value = savedUrl;

      const ytSearchUrl = `https://www.youtube.com/results?search_query=${encodeURIComponent(bio.videoQuery)}`;
      const ytLink = document.getElementById('ex-guide-yt-search-link');
      if (ytLink) ytLink.href = savedUrl || ytSearchUrl;

      const iframe = document.getElementById('ex-guide-video-iframe');
      const vidId = savedUrl ? window.extractYouTubeVideoId(savedUrl) : null;
      if (iframe) {
        iframe.src = vidId
          ? `https://www.youtube-nocookie.com/embed/${vidId}?rel=0&modestbranding=1`
          : `https://www.youtube-nocookie.com/embed?listType=search&list=${encodeURIComponent(bio.videoQuery)}`;
      }

      document.getElementById('exercise-guide-modal').classList.remove('hidden');
      if (window.lucide) lucide.createIcons();
    };

    window.closeExerciseGuideModal = function() {
      const iframe = document.getElementById('ex-guide-video-iframe');
      if (iframe) iframe.src = '';
      document.getElementById('exercise-guide-modal').classList.add('hidden');
      window.activeGuideExercise = null;
    };

    window.saveCustomExerciseVideoUrl = async function() {
      if (!window.activeGuideExercise) return;
      const urlVal = (document.getElementById('ex-guide-custom-yt-input')?.value || '').trim();
      const vidId = window.extractYouTubeVideoId(urlVal);
      if (!vidId) {
        alert('Please paste a valid YouTube video URL (e.g., https://youtu.be/... or https://www.youtube.com/watch?v=...).');
        return;
      }
      window.userAppState.customExerciseVideos = window.userAppState.customExerciseVideos || {};
      window.userAppState.customExerciseVideos[window.activeGuideExercise.name] = urlVal;

      const iframe = document.getElementById('ex-guide-video-iframe');
      if (iframe) iframe.src = `https://www.youtube-nocookie.com/embed/${vidId}?rel=0&modestbranding=1`;
      const ytLink = document.getElementById('ex-guide-yt-search-link');
      if (ytLink) ytLink.href = urlVal;

      renderAdaptiveWorkoutsTab();
      await pushCloudUserData();
    };"""

    if "window.EXERCISE_BIOMECHANICS_DB =" not in html:
        html = html.replace(
            "    // ADAPTIVE SHOULDER & BACK STRENGTH + FLEXIBILITY ENGINE",
            visual_workout_js + "\n\n    // ADAPTIVE SHOULDER & BACK STRENGTH + FLEXIBILITY ENGINE",
            1,
        )

    # 3. Upgrade exercise card rendering inside renderAdaptiveWorkoutsTab() to display inline Muscle Activation SVG + "Video & Form Guide" button
    old_ex_card_render = r"""          return `
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
          `;"""

    new_ex_card_render = r"""          const bio = getExerciseBiomechanics(ex);
          const miniSvg = buildAnatomicalMuscleSvg(bio.primary, bio.secondary, true);
          return `
            <div class="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-2.5 flex flex-col justify-between">
              <div class="flex justify-between items-start gap-3">
                <div class="space-y-1.5 flex-1 min-w-0">
                  <div class="flex flex-wrap items-center gap-1.5">
                    <span class="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-sky-950 text-sky-300 border border-sky-800">${ex.category}</span>
                    <span class="text-[10px] font-mono text-slate-400">Rest: ${ex.rest}</span>
                  </div>
                  <h5 class="font-bold text-white text-sm">${i + 1}. ${ex.name}</h5>
                  <p class="text-[11px] text-slate-300 leading-relaxed">${ex.cue}</p>
                </div>
                <div onclick="openExerciseGuideModal(${window.selectedWorkoutDayIdx}, ${i})" class="cursor-pointer bg-slate-900/90 hover:border-emerald-500/70 border border-slate-800 rounded-xl p-1.5 flex-shrink-0 transition" title="Click for Muscle Infographic & Video Demo">
                  ${miniSvg}
                </div>
              </div>
              <div class="space-y-2">
                <div class="p-2.5 rounded-lg border ${rxColor} text-[11px] font-mono">
                  <strong>${gate.zone} Gate Rx:</strong> ${prescription}
                </div>
                <div class="flex justify-between items-center gap-2 pt-0.5">
                  <span class="text-[10px] font-mono text-amber-300/90">Tempo: ${bio.tempo.split(' ')[0]}</span>
                  <button type="button" onclick="openExerciseGuideModal(${window.selectedWorkoutDayIdx}, ${i})" class="px-3 py-1 bg-indigo-950 hover:bg-indigo-900 border border-indigo-700/70 text-indigo-200 font-bold rounded-lg text-[11px] transition flex items-center gap-1.5">
                    <i data-lucide="play-circle" class="w-3.5 h-3.5 text-emerald-400"></i> Form Infographic &amp; Video
                  </button>
                </div>
              </div>
            </div>
          `;"""

    assert old_ex_card_render in html, "Could not locate exercise card template in renderAdaptiveWorkoutsTab"
    html = html.replace(old_ex_card_render, new_ex_card_render, 1)

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
        sw = re.sub(r"hive-alignment-ota-v\d+", "hive-alignment-ota-v6", sw)
        with open(SW_PATH, "w", encoding="utf-8", newline="\n") as f:
            f.write(sw)

    print(f"Successfully patched {INDEX_PATH} & {SW_PATH} with Anatomical Muscle Infographics & Exercise Video Demonstrations! ({len(onclicks)} button handlers verified)")


if __name__ == "__main__":
    main()

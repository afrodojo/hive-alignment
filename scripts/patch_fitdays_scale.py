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

    # 1. Update Smart Scale Dashboard Card in HTML with Fitdays metrics (Visceral Fat, Skeletal Muscle, Fat-Free Mass)
    old_scale_card = r"""            <div class="flex justify-between items-center border-b border-slate-800 pb-3">
              <div class="flex items-center gap-2.5">
                <div class="w-9 h-9 rounded-xl bg-purple-950 border border-purple-700/70 flex items-center justify-center text-purple-400 font-extrabold text-xs">BIO</div>
                <div>
                  <h4 class="font-bold text-white text-sm">Smart Scale Biometrics</h4>
                  <span class="text-[10px] text-slate-400 font-mono">Composition &bull; Lean Mass &bull; Hydration</span>
                </div>
              </div>
              <button type="button" onclick="openWearableConnectModal('manual')" class="text-[11px] px-2.5 py-1 bg-purple-950 hover:bg-purple-900 border border-purple-700/60 text-purple-200 rounded-lg font-semibold">
                Log Weigh-In
              </button>
            </div>

            <div class="grid grid-cols-2 gap-3 text-center">
              <div class="p-3.5 bg-slate-950 rounded-xl border border-slate-800">
                <span class="text-[10px] uppercase tracking-wider text-slate-400 block">Body Weight</span>
                <span id="s-dash-weight" class="text-2xl font-extrabold font-mono text-white mt-1 block">194.2 lbs</span>
                <span id="s-dash-weight-delta" class="text-[10px] text-emerald-400 font-semibold">-0.8 lbs (7d)</span>
              </div>
              <div class="p-3.5 bg-slate-950 rounded-xl border border-slate-800">
                <span class="text-[10px] uppercase tracking-wider text-slate-400 block">Body Fat %</span>
                <span id="s-dash-bf" class="text-2xl font-extrabold font-mono text-purple-400 mt-1 block">14.6%</span>
                <span class="text-[10px] text-slate-400">Athletic Range</span>
              </div>
              <div class="p-3 bg-slate-950 rounded-xl border border-slate-800">
                <span class="text-[10px] uppercase tracking-wider text-slate-400 block">Lean Muscle</span>
                <span id="s-dash-muscle" class="text-lg font-bold font-mono text-emerald-400 mt-0.5 block">165.8 lbs</span>
              </div>
              <div class="p-3 bg-slate-950 rounded-xl border border-slate-800">
                <span class="text-[10px] uppercase tracking-wider text-slate-400 block">Hydration %</span>
                <span id="s-dash-hydration" class="text-lg font-bold font-mono text-sky-400 mt-0.5 block">61.4%</span>
              </div>
            </div>

            <div class="p-3.5 bg-slate-950 rounded-xl border border-slate-800 space-y-1.5 text-xs">
              <span class="text-[10px] font-bold uppercase text-purple-400 block">Biometric &amp; Metabolic Targets:</span>
              <p class="text-[11px] text-slate-300">&bull; Daily Hydration Floor: <strong>96–112 oz</strong> electrolyte-balanced water</p>
              <p class="text-[11px] text-slate-300">&bull; Protein Anchor: <strong>185–200g</strong> daily to preserve lean mass during doctoral &amp; Omega prep</p>
            </div>"""

    new_scale_card = r"""            <div class="flex justify-between items-center border-b border-slate-800 pb-3">
              <div class="flex items-center gap-2.5">
                <div class="w-9 h-9 rounded-xl bg-purple-950 border border-purple-700/70 flex items-center justify-center text-purple-400 font-extrabold text-xs">FIT</div>
                <div>
                  <h4 class="font-bold text-white text-sm">Fitdays Smart Scale Biometrics</h4>
                  <span id="s-dash-source-tag" class="text-[10px] text-slate-400 font-mono">Fitdays Sync &bull; Nov 20, 2026</span>
                </div>
              </div>
              <button type="button" onclick="openWearableConnectModal('manual')" class="text-[11px] px-2.5 py-1 bg-purple-950 hover:bg-purple-900 border border-purple-700/60 text-purple-200 rounded-lg font-semibold">
                Log Fitdays
              </button>
            </div>

            <div class="grid grid-cols-2 gap-3 text-center">
              <div class="p-3.5 bg-slate-950 rounded-xl border border-slate-800">
                <span class="text-[10px] uppercase tracking-wider text-slate-400 block">Body Weight</span>
                <span id="s-dash-weight" class="text-2xl font-extrabold font-mono text-white mt-1 block">233.0 lbs</span>
                <span id="s-dash-weight-delta" class="text-[10px] text-emerald-400 font-semibold">-5.5 lbs (Target 100%)</span>
              </div>
              <div class="p-3.5 bg-slate-950 rounded-xl border border-slate-800">
                <span class="text-[10px] uppercase tracking-wider text-slate-400 block">Body Fat %</span>
                <span id="s-dash-bf" class="text-2xl font-extrabold font-mono text-purple-400 mt-1 block">25.5%</span>
                <span id="s-dash-fat-mass" class="text-[10px] text-slate-400">Fat Mass: 59.5 lbs</span>
              </div>
              <div class="p-3 bg-slate-950 rounded-xl border border-slate-800">
                <span class="text-[10px] uppercase tracking-wider text-slate-400 block">Muscle Mass</span>
                <span id="s-dash-muscle" class="text-lg font-bold font-mono text-emerald-400 mt-0.5 block">161.8 lbs</span>
                <span id="s-dash-skel-muscle" class="text-[10px] text-slate-400">Skeletal: 43.1%</span>
              </div>
              <div class="p-3 bg-slate-950 rounded-xl border border-slate-800">
                <span class="text-[10px] uppercase tracking-wider text-slate-400 block">Body Water %</span>
                <span id="s-dash-hydration" class="text-lg font-bold font-mono text-sky-400 mt-0.5 block">54.6%</span>
                <span id="s-dash-water-wt" class="text-[10px] text-slate-400">Water: 127.2 lbs</span>
              </div>
            </div>

            <div class="grid grid-cols-3 gap-2 text-center text-[10px]">
              <div class="p-2 rounded-xl bg-slate-950 border border-slate-800">
                <span class="text-slate-400 block">Fat-Free Wt</span>
                <span id="s-dash-ffm" class="font-mono font-bold text-slate-200">173.5 lbs</span>
              </div>
              <div class="p-2 rounded-xl bg-slate-950 border border-slate-800">
                <span class="text-slate-400 block">Visceral Fat</span>
                <span id="s-dash-visceral" class="font-mono font-bold text-amber-300">10.0</span>
              </div>
              <div class="p-2 rounded-xl bg-slate-950 border border-slate-800">
                <span class="text-slate-400 block">BMI / WHR</span>
                <span id="s-dash-bmi-whr" class="font-mono font-bold text-slate-200">31.6 / 0.89</span>
              </div>
            </div>

            <div class="p-3.5 bg-slate-950 rounded-xl border border-slate-800 space-y-1.5 text-xs">
              <span class="text-[10px] font-bold uppercase text-purple-400 block">Fitdays Recomposition &amp; Hydration Targets:</span>
              <p class="text-[11px] text-slate-300">&bull; Hydration Target: <strong>115–125 oz</strong>/day to raise Body Water from 54.6% toward 58%+</p>
              <p class="text-[11px] text-slate-300">&bull; Protein Anchor: <strong>175–200g</strong>/day (1.0–1.15g/lb FFM) to protect 161.8 lb muscle mass</p>
            </div>"""

    assert old_scale_card in html, "Could not locate Smart Scale card in docs/index.html"
    html = html.replace(old_scale_card, new_scale_card, 1)

    # 2. Expand Quick Sync modal inputs to include Hydration %, BMR, Visceral Fat, and Skeletal Muscle %
    old_manual_scale_inputs = r"""        <div class="grid grid-cols-3 gap-2.5">
          <div>
            <label class="text-slate-400 block mb-1">Weight (lbs)</label>
            <input type="number" step="0.1" id="inp-s-weight" value="194.2" class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2 text-slate-200 font-mono">
          </div>
          <div>
            <label class="text-slate-400 block mb-1">Body Fat %</label>
            <input type="number" step="0.1" id="inp-s-bf" value="14.6" class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2 text-slate-200 font-mono">
          </div>
          <div>
            <label class="text-slate-400 block mb-1">Lean Mass (lbs)</label>
            <input type="number" step="0.1" id="inp-s-muscle" value="165.8" class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2 text-slate-200 font-mono">
          </div>
        </div>"""

    new_manual_scale_inputs = r"""        <div class="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
          <div>
            <label class="text-slate-400 block mb-1">Fitdays Weight (lbs)</label>
            <input type="number" step="0.1" id="inp-s-weight" value="233.0" class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2 text-slate-200 font-mono">
          </div>
          <div>
            <label class="text-slate-400 block mb-1">Body Fat %</label>
            <input type="number" step="0.1" id="inp-s-bf" value="25.5" class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2 text-slate-200 font-mono">
          </div>
          <div>
            <label class="text-slate-400 block mb-1">Muscle Mass (lbs)</label>
            <input type="number" step="0.1" id="inp-s-muscle" value="161.8" class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2 text-slate-200 font-mono">
          </div>
          <div>
            <label class="text-slate-400 block mb-1">Body Water %</label>
            <input type="number" step="0.1" id="inp-s-hydration" value="54.6" class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2 text-slate-200 font-mono">
          </div>
          <div>
            <label class="text-slate-400 block mb-1">Visceral Fat</label>
            <input type="number" step="0.5" id="inp-s-visceral" value="10.0" class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2 text-slate-200 font-mono">
          </div>
          <div>
            <label class="text-slate-400 block mb-1">Fitdays BMR (kcal)</label>
            <input type="number" id="inp-s-bmr" value="2072" class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2 text-slate-200 font-mono">
          </div>
        </div>"""

    if old_manual_scale_inputs in html:
        html = html.replace(old_manual_scale_inputs, new_manual_scale_inputs, 1)

    # 3. Update CSV Import description to explicitly mention Fitdays CSV exports
    old_csv_desc = r"""Upload exported <strong>WHOOP</strong> (<code class="text-emerald-300">physiological_cycles.csv</code>, <code class="text-emerald-300">sleeps.csv</code>, <code class="text-emerald-300">workouts.csv</code>, <code class="text-emerald-300">journal_entries.csv</code>), <strong>Garmin Connect</strong> (<code class="text-sky-300">.csv</code> / <code class="text-sky-300">.fit</code>), or <code class="text-purple-300">.json</code> files."""
    new_csv_desc = r"""Upload exported <strong>Fitdays Smart Scale</strong> (<code class="text-purple-300">Fitdays*.csv</code>), <strong>WHOOP</strong> (<code class="text-emerald-300">physiological_cycles.csv</code>, <code class="text-emerald-300">sleeps.csv</code>, <code class="text-emerald-300">workouts.csv</code>, <code class="text-emerald-300">journal_entries.csv</code>), <strong>Garmin Connect</strong> (<code class="text-sky-300">.csv</code> / <code class="text-sky-300">.fit</code>), or <code class="text-purple-300">.json</code> files."""
    if old_csv_desc in html:
        html = html.replace(old_csv_desc, new_csv_desc, 1)

    # 4. Update DEFAULT_WEARABLE_TELEMETRY.scale with today's Nov 20, 2026 Fitdays baseline
    old_scale_def = r"""      scale: {
        weight: 194.2,
        weightDelta: '-0.8 lbs (7d)',
        bodyFat: 14.6,
        muscleMass: 165.8,
        hydration: 61.4,
        bmr: 1940
      }"""

    new_scale_def = r"""      scale: {
        source: 'Fitdays • Nov 20, 2026',
        weight: 233.0,
        weightDelta: '-5.5 lbs (Target 100%)',
        bodyFat: 25.5,
        fatMass: 59.5,
        fatFreeMass: 173.5,
        muscleMass: 161.8,
        skeletalMusclePct: 43.1,
        hydration: 54.6,
        waterWeight: 127.2,
        visceralFat: 10.0,
        bmi: 31.6,
        whr: 0.89,
        boneMass: 11.7,
        proteinMass: 34.6,
        bmr: 2072
      }"""

    assert old_scale_def in html, "Could not locate DEFAULT_WEARABLE_TELEMETRY.scale"
    html = html.replace(old_scale_def, new_scale_def, 1)

    # 5. Update renderWearablesDashboards() scale rendering
    old_scale_render = r"""      setTxt('s-dash-weight', `${tel.scale.weight} lbs`);
      setTxt('s-dash-weight-delta', tel.scale.weightDelta);
      setTxt('s-dash-bf', `${tel.scale.bodyFat}%`);
      setTxt('s-dash-muscle', `${tel.scale.muscleMass} lbs`);
      setTxt('s-dash-hydration', `${tel.scale.hydration}%`);
      setTxt('s-dash-bmr', `Est. BMR: ${Number(tel.scale.bmr || 1940).toLocaleString()} kcal`);"""

    new_scale_render = r"""      setTxt('s-dash-source-tag', tel.scale.source || 'Fitdays Smart Scale');
      setTxt('s-dash-weight', `${tel.scale.weight} lbs`);
      setTxt('s-dash-weight-delta', tel.scale.weightDelta);
      setTxt('s-dash-bf', `${tel.scale.bodyFat}%`);
      setTxt('s-dash-fat-mass', `Fat Mass: ${tel.scale.fatMass ?? (Number(tel.scale.weight || 233) * (Number(tel.scale.bodyFat || 25.5) / 100)).toFixed(1)} lbs`);
      setTxt('s-dash-muscle', `${tel.scale.muscleMass} lbs`);
      setTxt('s-dash-skel-muscle', `Skeletal: ${tel.scale.skeletalMusclePct ?? 43.1}%`);
      setTxt('s-dash-hydration', `${tel.scale.hydration}%`);
      setTxt('s-dash-water-wt', `Water: ${tel.scale.waterWeight ?? 127.2} lbs`);
      setTxt('s-dash-ffm', `${tel.scale.fatFreeMass ?? 173.5} lbs`);
      setTxt('s-dash-visceral', `${tel.scale.visceralFat ?? 10.0}`);
      setTxt('s-dash-bmi-whr', `${tel.scale.bmi ?? 31.6} / ${tel.scale.whr ?? 0.89}`);
      setTxt('s-dash-bmr', `Fitdays BMR: ${Number(tel.scale.bmr || 2072).toLocaleString()} kcal`);"""

    assert old_scale_render in html, "Could not locate scale render block in renderWearablesDashboards"
    html = html.replace(old_scale_render, new_scale_render, 1)

    # 6. Update syncWearableModalInputsFromState & handleSaveManualWearableTelemetry & CSV parser for Fitdays columns
    old_modal_scale_sync = r"""      setVal('inp-s-weight', tel.scale.weight);
      setVal('inp-s-bf', tel.scale.bodyFat);
      setVal('inp-s-muscle', tel.scale.muscleMass);"""

    new_modal_scale_sync = r"""      setVal('inp-s-weight', tel.scale.weight);
      setVal('inp-s-bf', tel.scale.bodyFat);
      setVal('inp-s-muscle', tel.scale.muscleMass);
      setVal('inp-s-hydration', tel.scale.hydration ?? 54.6);
      setVal('inp-s-visceral', tel.scale.visceralFat ?? 10.0);
      setVal('inp-s-bmr', tel.scale.bmr ?? 2072);"""

    if old_modal_scale_sync in html:
        html = html.replace(old_modal_scale_sync, new_modal_scale_sync, 1)

    old_manual_scale_save = r"""      tel.scale.weight = Number(document.getElementById('inp-s-weight').value || 194.2);
      tel.scale.bodyFat = Number(document.getElementById('inp-s-bf').value || 14.6);
      tel.scale.muscleMass = Number(document.getElementById('inp-s-muscle').value || 165.8);"""

    new_manual_scale_save = r"""      tel.scale.weight = Number(document.getElementById('inp-s-weight').value || 233.0);
      tel.scale.bodyFat = Number(document.getElementById('inp-s-bf').value || 25.5);
      tel.scale.muscleMass = Number(document.getElementById('inp-s-muscle').value || 161.8);
      tel.scale.hydration = Number(document.getElementById('inp-s-hydration')?.value || 54.6);
      tel.scale.visceralFat = Number(document.getElementById('inp-s-visceral')?.value || 10.0);
      tel.scale.bmr = Number(document.getElementById('inp-s-bmr')?.value || 2072);
      tel.scale.fatMass = Number((tel.scale.weight * (tel.scale.bodyFat / 100)).toFixed(1));
      tel.scale.fatFreeMass = Number((tel.scale.weight - tel.scale.fatMass).toFixed(1));
      tel.scale.source = `Fitdays • ${new Date().toLocaleDateString()}`;"""

    if old_manual_scale_save in html:
        html = html.replace(old_manual_scale_save, new_manual_scale_save, 1)

    old_csv_weight_parse = r"""          const steps = findFirstValid(['steps']);
          const weight = findFirstValid(['weight']);"""

    new_csv_weight_parse = r"""          const steps = findFirstValid(['steps']);
          const weight = findFirstValid(['weight']);
          const bfPct = findFirstValid(['body fat', 'fat rate']);
          const fatMassVal = findFirstValid(['fat mass']);
          const ffmVal = findFirstValid(['fat-free', 'fat free']);
          const muscleMassVal = findFirstValid(['muscle mass']);
          const skelMuscleVal = findFirstValid(['skeletal muscle']);
          const waterPctVal = findFirstValid(['body water', 'water rate', 'hydration']);
          const visceralVal = findFirstValid(['visceral fat']);
          const bmiVal = findFirstValid(['bmi']);
          const bmrVal = findFirstValid(['bmr', 'basal metabolic']);"""

    if old_csv_weight_parse in html:
        html = html.replace(old_csv_weight_parse, new_csv_weight_parse, 1)

    old_csv_weight_apply = r"""          if (!isNaN(steps)) tel.garmin.steps = Math.round(steps);
          if (!isNaN(weight)) tel.scale.weight = Number(weight).toFixed(1);"""

    new_csv_weight_apply = r"""          if (!isNaN(steps)) tel.garmin.steps = Math.round(steps);
          if (!isNaN(weight)) {
            tel.scale.weight = Number(weight).toFixed(1);
            tel.scale.source = `Fitdays CSV (${file.name})`;
          }
          if (!isNaN(bfPct)) tel.scale.bodyFat = Number(bfPct).toFixed(1);
          if (!isNaN(fatMassVal)) tel.scale.fatMass = Number(fatMassVal).toFixed(1);
          if (!isNaN(ffmVal)) tel.scale.fatFreeMass = Number(ffmVal).toFixed(1);
          if (!isNaN(muscleMassVal)) tel.scale.muscleMass = Number(muscleMassVal).toFixed(1);
          if (!isNaN(skelMuscleVal)) tel.scale.skeletalMusclePct = Number(skelMuscleVal).toFixed(1);
          if (!isNaN(waterPctVal)) tel.scale.hydration = Number(waterPctVal).toFixed(1);
          if (!isNaN(visceralVal)) tel.scale.visceralFat = Number(visceralVal).toFixed(1);
          if (!isNaN(bmiVal)) tel.scale.bmi = Number(bmiVal).toFixed(1);
          if (!isNaN(bmrVal)) tel.scale.bmr = Math.round(bmrVal);"""

    if old_csv_weight_apply in html:
        html = html.replace(old_csv_weight_apply, new_csv_weight_apply, 1)

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
        sw = re.sub(r"hive-alignment-ota-v\d+", "hive-alignment-ota-v8", sw)
        with open(SW_PATH, "w", encoding="utf-8", newline="\n") as f:
            f.write(sw)

    print(f"Successfully patched {INDEX_PATH} & {SW_PATH} with Fitdays Smart Scale Biometrics! ({len(onclicks)} button handlers verified)")


if __name__ == "__main__":
    main()

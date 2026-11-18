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
        raise FileNotFoundError(f"Could not find {INDEX_PATH}. Run this script from your repository root.")

    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Add On-Device Browser AI Status Badge + OpenAlex Citation Explorer Button in Knowledge Toolbar
    old_matrix_toolbar = """            <button type="button" id="btn-toggle-matrix-view" onclick="toggleKnowledgeMatrixView()" class="px-3.5 py-2 bg-slate-950 hover:bg-slate-800 border border-indigo-600/70 text-indigo-300 font-bold rounded-xl text-xs transition flex items-center gap-1.5">
              <i data-lucide="table" class="w-3.5 h-3.5"></i> <span id="matrix-view-label">Literature Matrix View</span>
            </button>"""

    new_matrix_toolbar = """            <button type="button" id="btn-toggle-matrix-view" onclick="toggleKnowledgeMatrixView()" class="px-3.5 py-2 bg-slate-950 hover:bg-slate-800 border border-indigo-600/70 text-indigo-300 font-bold rounded-xl text-xs transition flex items-center gap-1.5">
              <i data-lucide="table" class="w-3.5 h-3.5"></i> <span id="matrix-view-label">Literature Matrix View</span>
            </button>
            <button type="button" onclick="openOpenAlexExplorerModal()" class="px-3.5 py-2 bg-indigo-950 hover:bg-indigo-900 border border-indigo-600/70 text-indigo-200 font-bold rounded-xl text-xs transition flex items-center gap-1.5">
              <i data-lucide="network" class="w-3.5 h-3.5 text-sky-400"></i> OpenAlex Citation Graph
            </button>
            <button type="button" id="btn-local-ai-status" onclick="warmUpLocalBrowserAi()" class="px-3 py-2 bg-slate-950 hover:bg-slate-800 border border-emerald-700/60 text-emerald-300 font-bold rounded-xl text-xs transition flex items-center gap-1.5" title="Zero-Knowledge On-Device Browser AI (Gemini Nano / Phi)">
              <i data-lucide="cpu" class="w-3.5 h-3.5 text-emerald-400"></i> <span id="local-ai-badge-text">On-Device AI: Checking</span>
            </button>"""

    if "openOpenAlexExplorerModal()" not in html and old_matrix_toolbar in html:
        html = html.replace(old_matrix_toolbar, new_matrix_toolbar, 1)

    # 2. Add HRV-to-Mastery Biometric-Cognitive Analytics Card at the bottom of tab-wearables
    old_wearables_end = """          <div class="pt-3 border-t border-slate-800 flex justify-between items-center text-[11px]">
            <span id="s-dash-bmr" class="text-slate-400 font-mono">Est. BMR: 1,940 kcal</span>
            <button type="button" onclick="openWearableConnectModal('manual')" class="text-purple-400 hover:text-purple-300 font-semibold">Update Biometrics &rarr;</button>
          </div>
        </div>
      </div>
    </div>"""

    new_wearables_end = """          <div class="pt-3 border-t border-slate-800 flex justify-between items-center text-[11px]">
            <span id="s-dash-bmr" class="text-slate-400 font-mono">Est. BMR: 1,940 kcal</span>
            <button type="button" onclick="openWearableConnectModal('manual')" class="text-purple-400 hover:text-purple-300 font-semibold">Update Biometrics &rarr;</button>
          </div>
        </div>
      </div>

      <!-- HRV-TO-MASTERY BIOMETRIC-COGNITIVE CORRELATION ANALYTICS -->
      <div class="bg-slate-900 border border-indigo-800/50 rounded-2xl p-6 space-y-4 shadow-xl">
        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 border-b border-slate-800 pb-3">
          <div>
            <span class="text-[10px] font-bold uppercase tracking-wider text-indigo-400 flex items-center gap-1.5">
              <i data-lucide="brain-circuit" class="w-3.5 h-3.5"></i> Biometric-Cognitive Telemetry Synthesis
            </span>
            <h4 class="text-base font-bold text-white mt-0.5">HRV &amp; Recovery Gate vs. Active-Recall Mastery</h4>
          </div>
          <span id="cog-bio-sync-tag" class="text-[11px] font-mono px-3 py-1 rounded-lg bg-slate-950 border border-slate-800 text-emerald-300">
            Cognitive Load Calibrated
          </span>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 text-xs">
          <div class="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-1">
            <span class="text-[10px] uppercase text-slate-400 block">Autonomic Cognitive Bandwidth</span>
            <span id="cog-bio-bandwidth" class="text-xl font-extrabold font-mono text-amber-400 block">Consolidation Mode</span>
            <span id="cog-bio-hrv-ref" class="text-[11px] text-slate-400 block">WHOOP HRV: 18 ms • Garmin: 84</span>
          </div>
          <div class="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-1">
            <span class="text-[10px] uppercase text-slate-400 block">Active-Recall Mastery Rate</span>
            <span id="cog-bio-mastery-pct" class="text-xl font-extrabold font-mono text-emerald-400 block">0% Mastered</span>
            <span id="cog-bio-mastery-sub" class="text-[11px] text-slate-400 block">0 / 0 Vault &amp; Omega Cards</span>
          </div>
          <div class="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-1">
            <span class="text-[10px] uppercase text-slate-400 block">Spaced-Repetition Depth</span>
            <span id="cog-bio-spaced-lvl" class="text-xl font-extrabold font-mono text-sky-400 block">Avg Lvl 0.0</span>
            <span id="cog-bio-due-count" class="text-[11px] text-slate-400 block">0 Cards Due Today</span>
          </div>
          <div class="p-4 bg-slate-950 rounded-xl border border-indigo-900/50 space-y-1">
            <span class="text-[10px] uppercase text-indigo-400 font-bold block">Recommended Study Modality</span>
            <p id="cog-bio-modality-advice" class="text-[11px] text-slate-200 leading-snug">
              Pair 20-min Audio/Video review with 3Q active-recall drills during peak post-Fajr focus.
            </p>
          </div>
        </div>
      </div>
    </div>"""

    if 'id="cog-bio-bandwidth"' not in html and old_wearables_end in html:
        html = html.replace(old_wearables_end, new_wearables_end, 1)

    # 3. Add Native Qari Recitation Streamer Bar inside Faith & Salat Path tab
    old_salat_grid = """        <div id="salat-times-grid" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5 text-xs"></div>
      </div>"""

    new_salat_grid = """        <div id="salat-times-grid" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5 text-xs"></div>

        <!-- Authentic Qari Quran Recitation Player (AlQuran Cloud CDN) -->
        <div class="p-3.5 bg-slate-950 rounded-xl border border-emerald-800/50 flex flex-col lg:flex-row items-start lg:items-center justify-between gap-3 text-xs">
          <div class="flex items-center gap-2.5">
            <div class="w-9 h-9 rounded-xl bg-emerald-950 border border-emerald-700 flex items-center justify-center text-emerald-400 flex-shrink-0">
              <i data-lucide="volume-2" class="w-4 h-4"></i>
            </div>
            <div>
              <span class="text-[10px] font-bold uppercase text-emerald-400 block">Authentic Qari Recitation Stream (AlQuran CDN)</span>
              <p id="qari-now-playing" class="text-slate-200 font-semibold">Select a Surah &amp; Qari (Alafasy, Al-Husary, Al-Minshawi) for Fajr/Isha listening</p>
            </div>
          </div>
          <div class="flex flex-wrap items-center gap-2 w-full lg:w-auto">
            <select id="qari-surah-select" onchange="playSelectedQariSurah()" class="bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1.5 text-slate-200">
              <option value="1">1. Al-Fatihah</option>
              <option value="18">18. Al-Kahf</option>
              <option value="36">36. Ya-Sin</option>
              <option value="55">55. Ar-Rahman</option>
              <option value="67" selected>67. Al-Mulk (Nightly Isha)</option>
              <option value="87">87. Al-A'la</option>
              <option value="94">94. Ash-Sharh</option>
              <option value="103">103. Al-Asr</option>
              <option value="112">112. Al-Ikhlas</option>
            </select>
            <select id="qari-reciter-select" onchange="playSelectedQariSurah()" class="bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1.5 text-slate-200">
              <option value="ar.alafasy">Mishary Rashid Alafasy</option>
              <option value="ar.husary">Mahmoud Khalil Al-Husary (Tajweed)</option>
              <option value="ar.minshawi">Mohamed Siddiq al-Minshawi</option>
            </select>
            <audio id="qari-html5-audio" controls preload="none" class="h-8 max-w-[230px]"></audio>
          </div>
        </div>
      </div>"""

    if 'id="qari-html5-audio"' not in html and old_salat_grid in html:
        html = html.replace(old_salat_grid, new_salat_grid, 1)

    # 4. Add "3-Min Rapid-Fire Drill" button in Seeker Study (Omega) toolbar
    old_omega_4phase = """            <button type="button" onclick="buildFullOmegaLinePlan()" class="px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl text-xs transition flex items-center gap-1.5 shadow-lg">
              <i data-lucide="map" class="w-3.5 h-3.5"></i> 4-Phase Plan
            </button>"""

    new_omega_4phase = """            <button type="button" onclick="openOmegaTimedDrill()" class="px-3.5 py-2 bg-amber-400 hover:bg-amber-300 text-slate-950 font-extrabold rounded-xl text-xs transition flex items-center gap-1.5 shadow-lg">
              <i data-lucide="timer" class="w-3.5 h-3.5"></i> 3-Min Line Drill
            </button>
            <button type="button" onclick="buildFullOmegaLinePlan()" class="px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl text-xs transition flex items-center gap-1.5 shadow-lg">
              <i data-lucide="map" class="w-3.5 h-3.5"></i> 4-Phase Plan
            </button>"""

    if "openOmegaTimedDrill()" not in html and old_omega_4phase in html:
        html = html.replace(old_omega_4phase, new_omega_4phase, 1)

    # 5. Add Psycuro Move 2 Blank-Page Generation Scratchpad inside Recall Quiz Modal
    old_quiz_container = """      <div id="quiz-questions-container" class="space-y-4 text-xs"></div>"""

    new_quiz_container = """      <!-- Psycuro Move 2: Blank-Page Generation Effect Scratchpad -->
      <div id="generation-scratchpad-box" class="p-3.5 bg-indigo-950/30 border border-indigo-800/60 rounded-xl space-y-2 text-xs">
        <div class="flex justify-between items-center">
          <span class="text-[10px] font-bold uppercase tracking-wider text-indigo-300 flex items-center gap-1.5">
            <i data-lucide="edit-3" class="w-3.5 h-3.5"></i> Move 2: Blank-Page Generation Recall (Before Cues)
          </span>
          <span id="gen-timer-label" class="text-[11px] font-mono text-amber-300">60s Free Recall</span>
        </div>
        <textarea id="generation-scratchpad-input" rows="3" placeholder="Close your mental notes and write everything you remember about this topic from a blank page BEFORE revealing the 3 cues..." class="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 font-mono focus:outline-none focus:border-indigo-500"></textarea>
        <div class="flex justify-end gap-2">
          <button type="button" onclick="unlockQuizQuestionsFromGeneration()" class="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-lg text-[11px]">
            Lock Generation &amp; Reveal 3Q Cues
          </button>
        </div>
      </div>

      <div id="quiz-questions-container" class="hidden space-y-4 text-xs"></div>"""

    if 'id="generation-scratchpad-box"' not in html and old_quiz_container in html:
        html = html.replace(old_quiz_container, new_quiz_container, 1)

    # 6. Inject OpenAlex Citation-Graph Explorer Modal & Timed Omega Line-Drill Simulator Modal
    new_modals_html = """  <!-- OPENALEX CITATION-GRAPH & RELATED WORKS EXPLORER MODAL -->
  <div id="openalex-explorer-modal" class="fixed inset-0 bg-slate-950/95 backdrop-blur-md z-[1240] hidden flex items-center justify-center p-4 overflow-y-auto">
    <div class="bg-slate-900 border border-indigo-700/60 rounded-2xl max-w-3xl w-full p-6 space-y-4 shadow-2xl relative my-8">
      <div class="flex justify-between items-start border-b border-slate-800 pb-3">
        <div>
          <span class="text-[10px] font-bold uppercase tracking-wider text-indigo-400 flex items-center gap-1.5">
            <i data-lucide="network" class="w-3.5 h-3.5"></i> OpenAlex 500M+ Scholarly Citation Graph
          </span>
          <h3 class="text-base font-bold text-white mt-0.5">Expand Doctoral Literature Matrix (Cited-By &amp; Open-Access Papers)</h3>
        </div>
        <button type="button" onclick="closeOpenAlexExplorerModal()" class="text-slate-400 hover:text-white text-xl leading-none">&times;</button>
      </div>

      <form onsubmit="searchOpenAlexWorks(event)" class="flex flex-col sm:flex-row gap-2 text-xs">
        <input type="text" id="openalex-query-input" required placeholder="Search author, seminal paper, or doctoral construct (e.g., Deslauriers feeling of learning, HRV executive function)..." class="flex-grow bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-slate-200 focus:outline-none focus:border-indigo-500">
        <button type="submit" id="openalex-search-btn" class="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl flex-shrink-0">
          Search Citation Graph
        </button>
      </form>
      <p id="openalex-status-text" class="text-xs text-sky-300 hidden"></p>
      <div id="openalex-results-list" class="max-h-96 overflow-y-auto space-y-2.5 text-xs pr-1"></div>
    </div>
  </div>

  <!-- TIMED OMEGA RAPID-FIRE LINE DRILL SIMULATOR MODAL -->
  <div id="omega-timed-drill-modal" class="fixed inset-0 bg-slate-950/95 backdrop-blur-md z-[1245] hidden flex items-center justify-center p-4 overflow-y-auto">
    <div class="bg-slate-900 border border-amber-600/60 rounded-2xl max-w-xl w-full p-6 space-y-4 shadow-2xl relative my-8">
      <div class="flex justify-between items-center border-b border-slate-800 pb-3">
        <div>
          <span class="text-[10px] font-bold uppercase tracking-wider text-amber-400 flex items-center gap-1.5">
            <i data-lucide="timer" class="w-3.5 h-3.5"></i> Omega Psi Phi High-Tempo Recall Drill
          </span>
          <h3 class="text-base font-bold text-white mt-0.5">3-Minute Rapid-Fire Line &amp; Heritage Simulator</h3>
        </div>
        <div class="flex items-center gap-3">
          <span id="omega-drill-timer" class="px-3 py-1 rounded-lg bg-amber-950 border border-amber-600 text-amber-300 font-mono font-extrabold text-sm">03:00</span>
          <button type="button" onclick="closeOmegaTimedDrill()" class="text-slate-400 hover:text-white text-xl leading-none">&times;</button>
        </div>
      </div>

      <div id="omega-drill-body" class="space-y-4 text-xs">
        <div class="flex justify-between text-[11px] font-mono text-slate-400">
          <span id="omega-drill-counter">Card 1 of 10</span>
          <span id="omega-drill-score" class="text-emerald-400 font-bold">Score: 0</span>
        </div>
        <div class="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-3">
          <span id="omega-drill-source-tag" class="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800">Heritage</span>
          <p id="omega-drill-question" class="text-sm font-bold text-white leading-relaxed">Loading drill deck...</p>
          <input type="text" id="omega-drill-user-input" placeholder="Type quick recall answer before flipping..." class="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-amber-500">
          <div id="omega-drill-answer-box" class="hidden p-3 rounded-lg bg-emerald-950/50 border border-emerald-700/60 text-emerald-200 text-xs"></div>
        </div>
        <div class="flex flex-wrap justify-between items-center gap-2 pt-2 border-t border-slate-800">
          <button type="button" onclick="revealOmegaDrillAnswer()" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl">
            Flip / Check Answer
          </button>
          <div class="flex gap-2">
            <button type="button" onclick="gradeOmegaDrillCard(false)" class="px-3.5 py-2 bg-rose-950 hover:bg-rose-900 border border-rose-700 text-rose-200 font-bold rounded-xl">
              Review Again
            </button>
            <button type="button" onclick="gradeOmegaDrillCard(true)" class="px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold rounded-xl">
              Nailed It (+1) &rarr;
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>"""

    if 'id="openalex-explorer-modal"' not in html:
        html = html.replace("  <!-- MODALS -->", "  <!-- MODALS -->\n" + new_modals_html, 1)

    # 7. Add "Cited-By" quick button to Literature Matrix rows
    old_matrix_row_btns = """              <div class="inline-flex gap-1">
                <button type="button" onclick="openRecallQuiz('${item.id}')" class="px-2 py-1 bg-emerald-600 text-slate-950 font-bold rounded text-[10px]">3Q</button>"""

    new_matrix_row_btns = """              <div class="inline-flex gap-1">
                <button type="button" onclick="openOpenAlexExplorerModal('${item.title.replace(/'/g, "\\'")}')" class="px-2 py-1 bg-sky-950 text-sky-300 border border-sky-800 font-bold rounded text-[10px]" title="Find Cited-By & Related Works in OpenAlex">Cite+</button>
                <button type="button" onclick="openRecallQuiz('${item.id}')" class="px-2 py-1 bg-emerald-600 text-slate-950 font-bold rounded text-[10px]">3Q</button>"""

    if "openOpenAlexExplorerModal('${item.title" not in html and old_matrix_row_btns in html:
        html = html.replace(old_matrix_row_btns, new_matrix_row_btns, 1)

    # 8. Enhance fetchQuranSurahIntoForm to also pull Classical Tafsir (ar.muyassar / en.jalalayn) and load Qari audio
    old_quran_fetch = """        const res = await fetch(`https://api.alquran.cloud/v1/surah/${surahNum}/editions/quran-uthmani,en.sahih`);
        if (!res.ok) throw new Error(`AlQuran API returned HTTP ${res.status}`);
        const json = await res.json();
        const arData = json?.data?.[0];
        const enData = json?.data?.[1];
        if (!arData || !enData) throw new Error('Could not parse Surah payload.');"""

    new_quran_fetch = """        const res = await fetch(`https://api.alquran.cloud/v1/surah/${surahNum}/editions/quran-uthmani,en.sahih,ar.muyassar`);
        if (!res.ok) throw new Error(`AlQuran API returned HTTP ${res.status}`);
        const json = await res.json();
        const arData = json?.data?.[0];
        const enData = json?.data?.[1];
        const tafsirData = json?.data?.[2];
        if (!arData || !enData) throw new Error('Could not parse Surah payload.');"""

    if "ar.muyassar" not in html and old_quran_fetch in html:
        html = html.replace(old_quran_fetch, new_quran_fetch, 1)

    old_quran_loop = """          if (enAyah) {
            compiledLines.push(`[${surahNum}:${enAyah.numberInSurah}] ${enAyah.text}`);
            if (arAyah) compiledLines.push(`Arabic: ${arAyah.text}`);
          }"""

    new_quran_loop = """          const tafsirAyah = tafsirData?.ayahs?.[i];
          if (enAyah) {
            compiledLines.push(`[${surahNum}:${enAyah.numberInSurah}] ${enAyah.text}`);
            if (arAyah) compiledLines.push(`Arabic: ${arAyah.text}`);
            if (tafsirAyah) compiledLines.push(`Tafsir Al-Muyassar: ${tafsirAyah.text}`);
          }"""

    if "Tafsir Al-Muyassar:" not in html and old_quran_loop in html:
        html = html.replace(old_quran_loop, new_quran_loop, 1)

    # 9. Inject JavaScript Engines for:
    #    - On-Device Browser AI (Summarizer & LanguageModel APIs with deterministic fallback)
    #    - Authentic Qari Recitation Streamer
    #    - OpenAlex Citation-Graph Explorer
    #    - Psycuro Move 2 Blank-Page Generation Scratchpad
    #    - 3-Minute Timed Omega Rapid-Fire Line-Drill Simulator
    #    - HRV-to-Mastery Biometric-Cognitive Analytics Renderer
    advanced_js = """    // 1. ZERO-KNOWLEDGE ON-DEVICE BROWSER AI (GEMINI NANO / PHI SUMMARIZER & PROMPT API)
    window.localAiCapability = 'checking';

    window.checkLocalBrowserAiStatus = async function() {
      const badgeEl = document.getElementById('local-ai-badge-text');
      try {
        if ('Summarizer' in self) {
          const avail = await self.Summarizer.availability({ type: 'key-points', format: 'plain-text', length: 'short' });
          window.localAiCapability = avail;
          if (badgeEl) {
            badgeEl.innerText = avail === 'available'
              ? 'On-Device AI: Ready (Local)'
              : (avail === 'downloadable' ? 'On-Device AI: Click to Enable' : 'Local Parser: Active');
          }
          return avail;
        }
        if ('LanguageModel' in self) {
          const lmAvail = await self.LanguageModel.availability();
          window.localAiCapability = lmAvail;
          if (badgeEl) badgeEl.innerText = lmAvail === 'available' ? 'On-Device AI: Ready (Local)' : 'Local Parser: Active';
          return lmAvail;
        }
      } catch (e) {}
      window.localAiCapability = 'unavailable';
      if (badgeEl) badgeEl.innerText = 'Local Parser: Active';
      return 'unavailable';
    };

    window.warmUpLocalBrowserAi = async function() {
      const badgeEl = document.getElementById('local-ai-badge-text');
      if (!('Summarizer' in self) && !('LanguageModel' in self)) {
        alert('Built-in Browser AI (Chrome 138+ Gemini Nano / Edge 148+ Phi) is not enabled in this browser. Your zero-knowledge deterministic distillation engine is active.');
        return;
      }
      try {
        if (badgeEl) badgeEl.innerText = 'On-Device AI: Warming...';
        if ('Summarizer' in self) {
          const opts = {
            type: 'key-points',
            format: 'plain-text',
            length: 'short',
            monitor(m) {
              m.addEventListener('downloadprogress', (e) => {
                if (badgeEl && e.total) {
                  badgeEl.innerText = `AI Model: ${Math.round((e.loaded / e.total) * 100)}%`;
                }
              });
            }
          };
          const s = await self.Summarizer.create(opts);
          if (s && typeof s.destroy === 'function') s.destroy();
        }
        await window.checkLocalBrowserAiStatus();
      } catch (err) {
        await window.checkLocalBrowserAiStatus();
      }
    };

    window.enhanceItemWithLocalAiAsync = async function(itemId) {
      if (!('Summarizer' in self)) return;
      try {
        const opts = { type: 'key-points', format: 'plain-text', length: 'short' };
        const avail = await self.Summarizer.availability(opts);
        if (avail !== 'available') return;

        const vault = window.userAppState.knowledgeVault || [];
        const target = vault.find(v => v.id === itemId);
        if (!target || !target.content || target.content.length < 180) return;

        const summarizer = await self.Summarizer.create(opts);
        const summary = await summarizer.summarize(target.content.slice(0, 5000), {
          context: `Distill key academic or spiritual insights for ${target.title}`
        });
        if (typeof summarizer.destroy === 'function') summarizer.destroy();

        const bullets = summary.split(/\n+/).map(l => l.replace(/^[-*•\d.)\s]+/, '').trim()).filter(l => l.length > 15);
        if (bullets.length >= 2) {
          target.takeaway = bullets[0];
          target.microSteps = [
            `1. Local AI Synthesis: ${bullets[0]}`,
            `2. Core Mechanism: ${bullets[1]}`,
            `3. Active Recall: ${bullets[2] || 'Test retention via 3Q quiz from blank-page memory.'}`
          ];
          renderAllUI();
          await pushCloudUserData();
        }
      } catch (e) {}
    };

    // 2. AUTHENTIC QARI QURAN RECITATION PLAYER (ALQURAN CLOUD CDN)
    window.playSelectedQariSurah = function() {
      const surahSel = document.getElementById('qari-surah-select');
      const reciterSel = document.getElementById('qari-reciter-select');
      const audioEl = document.getElementById('qari-html5-audio');
      const nowEl = document.getElementById('qari-now-playing');
      if (!surahSel || !reciterSel || !audioEl) return;

      const surahNum = surahSel.value;
      const surahLabel = surahSel.options[surahSel.selectedIndex].text;
      const qariId = reciterSel.value;
      const qariName = reciterSel.options[reciterSel.selectedIndex].text;

      audioEl.src = `https://cdn.islamic.network/quran/audio-surah/128/${qariId}/${surahNum}.mp3`;
      if (nowEl) nowEl.innerText = `Streaming ${surahLabel} • Reciter: ${qariName}`;
      audioEl.play().catch(() => {});
    };

    // 3. OPENALEX 500M+ SCHOLARLY CITATION GRAPH EXPLORER
    window.openAlexCachedResults = [];

    window.openOpenAlexExplorerModal = function(presetQuery) {
      const qInput = document.getElementById('openalex-query-input');
      const stEl = document.getElementById('openalex-status-text');
      const listEl = document.getElementById('openalex-results-list');
      if (stEl) stEl.classList.add('hidden');
      if (listEl) listEl.innerHTML = '';
      if (qInput && presetQuery) qInput.value = presetQuery;
      document.getElementById('openalex-explorer-modal').classList.remove('hidden');
      if (window.lucide) lucide.createIcons();
      if (qInput && qInput.value.trim()) {
        window.searchOpenAlexWorks();
      }
    };

    window.closeOpenAlexExplorerModal = function() {
      document.getElementById('openalex-explorer-modal').classList.add('hidden');
    };

    function reconstructOpenAlexAbstract(invIdx) {
      if (!invIdx || typeof invIdx !== 'object') return '';
      const words = [];
      Object.entries(invIdx).forEach(([word, positions]) => {
        if (Array.isArray(positions)) {
          positions.forEach(pos => { words[pos] = word; });
        }
      });
      return words.filter(Boolean).join(' ');
    }

    window.searchOpenAlexWorks = async function(e) {
      if (e) e.preventDefault();
      const query = (document.getElementById('openalex-query-input')?.value || '').trim();
      const btn = document.getElementById('openalex-search-btn');
      const stEl = document.getElementById('openalex-status-text');
      const listEl = document.getElementById('openalex-results-list');
      if (!query) return;

      btn.disabled = true;
      btn.innerText = 'Searching...';
      if (stEl) {
        stEl.classList.remove('hidden');
        stEl.innerText = `Querying OpenAlex scholarly graph for "${query}"...`;
      }

      try {
        const url = `https://api.openalex.org/works?search=${encodeURIComponent(query)}&per-page=8&sort=cited_by_count:desc`;
        const res = await fetch(url);
        if (!res.ok) throw new Error(`OpenAlex returned HTTP ${res.status}`);
        const json = await res.json();
        const works = json?.results || [];
        window.openAlexCachedResults = works;

        if (stEl) {
          stEl.innerText = `Found ${works.length} high-impact works (sorted by citation count). Click "+ Literature Matrix" to ingest.`;
        }

        if (listEl) {
          listEl.innerHTML = works.map((w, idx) => {
            const title = w.display_name || w.title || 'Untitled Work';
            const year = w.publication_year || 'n.d.';
            const authors = (w.authorships || []).slice(0, 3).map(a => a.author?.display_name).filter(Boolean).join(', ') || 'Scholarly Author';
            const citedBy = w.cited_by_count || 0;
            const venue = w.primary_location?.source?.display_name || 'OpenAlex Index';
            const oaUrl = w.open_access?.oa_url || w.doi || w.id || '';
            const abstract = reconstructOpenAlexAbstract(w.abstract_inverted_index);

            return `
              <div class="p-3.5 bg-slate-950 rounded-xl border border-slate-800 space-y-2">
                <div class="flex justify-between items-start gap-2">
                  <div class="space-y-0.5">
                    <h4 class="font-bold text-white text-xs">${title}</h4>
                    <p class="text-[11px] font-mono text-amber-300">${authors} (${year}) • ${venue}</p>
                  </div>
                  <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800 flex-shrink-0">
                    Cited by ${citedBy.toLocaleString()}
                  </span>
                </div>
                ${abstract ? `<p class="text-[11px] text-slate-400 line-clamp-3">${abstract}</p>` : ''}
                <div class="flex flex-wrap justify-between items-center gap-2 pt-1">
                  ${oaUrl ? `<a href="${oaUrl}" target="_blank" rel="noopener noreferrer" class="text-[11px] text-sky-400 hover:underline">Open Source / DOI &nearr;</a>` : '<span></span>'}
                  <button type="button" onclick="ingestOpenAlexWork(${idx})" class="px-3 py-1 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-lg text-[11px]">
                    + Literature Matrix &amp; 3Q Quiz
                  </button>
                </div>
              </div>
            `;
          }).join('') || '<p class="text-slate-400">No matching scholarly works found.</p>';
        }
      } catch (err) {
        if (stEl) stEl.innerText = `OpenAlex search notice: ${err.message}`;
      } finally {
        btn.disabled = false;
        btn.innerText = 'Search Citation Graph';
      }
    };

    window.ingestOpenAlexWork = async function(idx) {
      const w = window.openAlexCachedResults[idx];
      if (!w) return;
      const title = w.display_name || w.title || 'Scholarly Paper';
      const year = w.publication_year || '2026';
      const authors = (w.authorships || []).slice(0, 3).map(a => a.author?.display_name).filter(Boolean).join(', ') || 'Scholarly Author';
      const venue = w.primary_location?.source?.display_name || 'OpenAlex Citation Graph';
      const abstract = reconstructOpenAlexAbstract(w.abstract_inverted_index) || `Seminal work "${title}" by ${authors} (${year}), cited ${w.cited_by_count || 0} times.`;
      const distilled = distillTextToMicroSession(title, abstract);
      const today = getTodayIsoDate();

      const newId = 'kv_oa_' + Date.now();
      window.userAppState.knowledgeVault = window.userAppState.knowledgeVault || [];
      window.userAppState.knowledgeVault.unshift({
        id: newId,
        title,
        domain: 'Doctoral Studies',
        resourceFormat: 'Academic Paper (Peer-Reviewed)',
        author: `${authors} (${year})`,
        sectionRef: `${venue} • Cited ${w.cited_by_count || 0}x`,
        researchGap: 'Evaluate theoretical construct alignment for Chapter 2 synthesis.',
        duration: '20-Min Deep Sprint',
        type: 'Doctoral Studies • OpenAlex Citation',
        takeaway: distilled.takeaway,
        content: abstract.slice(0, 6000),
        microSteps: distilled.microSteps,
        quiz: distilled.quiz,
        masteryLevel: 0,
        nextReviewDate: today,
        quizScore: null,
        date: today
      });

      window.activePolymathDomain = 'Doctoral Studies';
      renderAllUI();
      await pushCloudUserData();
      window.enhanceItemWithLocalAiAsync(newId);
      closeOpenAlexExplorerModal();
    };

    // 4. TIMED 3-MINUTE OMEGA RAPID-FIRE LINE-DRILL SIMULATOR
    window.omegaDrillDeck = [];
    window.omegaDrillIndex = 0;
    window.omegaDrillScore = 0;
    window.omegaDrillSecondsLeft = 180;
    window.omegaDrillInterval = null;

    window.openOmegaTimedDrill = function() {
      const omegaItems = window.userAppState.omegaNotebooks || [];
      if (!omegaItems.length) {
        alert('Import your Proton Drive folder or pull official Omega sites first to populate the drill deck.');
        return;
      }

      const cards = [];
      omegaItems.forEach(item => {
        const qList = (item.quiz && item.quiz.length) ? item.quiz : generateRecallQuiz(item.title, item.content);
        qList.forEach(qObj => {
          cards.push({
            source: item.source || 'Omega Vault',
            title: item.title,
            q: qObj.q.replace(/^\d+\.\s*/, ''),
            a: qObj.a
          });
        });
      });

      // Fisher-Yates shuffle
      for (let i = cards.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [cards[i], cards[j]] = [cards[j], cards[i]];
      }

      window.omegaDrillDeck = cards.slice(0, 15);
      window.omegaDrillIndex = 0;
      window.omegaDrillScore = 0;
      window.omegaDrillSecondsLeft = 180;

      if (window.omegaDrillInterval) clearInterval(window.omegaDrillInterval);
      window.omegaDrillInterval = setInterval(() => {
        window.omegaDrillSecondsLeft--;
        const mins = String(Math.floor(Math.max(0, window.omegaDrillSecondsLeft) / 60)).padStart(2, '0');
        const secs = String(Math.max(0, window.omegaDrillSecondsLeft) % 60).padStart(2, '0');
        const tEl = document.getElementById('omega-drill-timer');
        if (tEl) tEl.innerText = `${mins}:${secs}`;
        if (window.omegaDrillSecondsLeft <= 0) {
          clearInterval(window.omegaDrillInterval);
          finishOmegaTimedDrill();
        }
      }, 1000);

      renderOmegaDrillCard();
      document.getElementById('omega-timed-drill-modal').classList.remove('hidden');
      if (window.lucide) lucide.createIcons();
    };

    function renderOmegaDrillCard() {
      if (window.omegaDrillIndex >= window.omegaDrillDeck.length) {
        finishOmegaTimedDrill();
        return;
      }
      const card = window.omegaDrillDeck[window.omegaDrillIndex];
      document.getElementById('omega-drill-counter').innerText = `Card ${window.omegaDrillIndex + 1} of ${window.omegaDrillDeck.length}`;
      document.getElementById('omega-drill-score').innerText = `Score: ${window.omegaDrillScore}`;
      document.getElementById('omega-drill-source-tag').innerText = `${card.source} • ${card.title}`;
      document.getElementById('omega-drill-question').innerText = card.q;
      document.getElementById('omega-drill-user-input').value = '';
      const ansBox = document.getElementById('omega-drill-answer-box');
      ansBox.classList.add('hidden');
      ansBox.innerText = `Key: ${card.a}`;
    }

    window.revealOmegaDrillAnswer = function() {
      document.getElementById('omega-drill-answer-box')?.classList.remove('hidden');
    };

    window.gradeOmegaDrillCard = function(passed) {
      if (passed) window.omegaDrillScore++;
      window.omegaDrillIndex++;
      renderOmegaDrillCard();
    };

    function finishOmegaTimedDrill() {
      if (window.omegaDrillInterval) clearInterval(window.omegaDrillInterval);
      const total = window.omegaDrillDeck.length || 1;
      const pct = Math.round((window.omegaDrillScore / total) * 100);
      document.getElementById('omega-drill-question').innerText = `Drill Complete! You scored ${window.omegaDrillScore} / ${total} (${pct}%) under timed conditions.`;
      const ansBox = document.getElementById('omega-drill-answer-box');
      ansBox.classList.remove('hidden');
      ansBox.innerText = 'Manhood • Scholarship • Perseverance • Uplift — Keep sharpening daily!';
    }

    window.closeOmegaTimedDrill = function() {
      if (window.omegaDrillInterval) clearInterval(window.omegaDrillInterval);
      document.getElementById('omega-timed-drill-modal').classList.add('hidden');
    };

    // 5. PSYCURO MOVE 2 GENERATION SCRATCHPAD UNLOCK
    window.unlockQuizQuestionsFromGeneration = function() {
      const qBox = document.getElementById('quiz-questions-container');
      if (qBox) qBox.classList.remove('hidden');
    };

    // 6. HRV-TO-MASTERY BIOMETRIC-COGNITIVE ANALYTICS RENDERER
    function renderBiometricCognitiveAnalytics() {
      const tel = getWearableTelemetry();
      const gate = evaluateAutoRegulatorGate(tel);
      const vault = window.userAppState.knowledgeVault || [];
      const omega = window.userAppState.omegaNotebooks || [];
      const allCards = [...vault, ...omega];
      const mastered = allCards.filter(i => !!i.quizScore).length;
      const pct = allCards.length ? Math.round((mastered / allCards.length) * 100) : 0;
      const avgLvl = vault.length
        ? (vault.reduce((acc, i) => acc + (i.masteryLevel || 0), 0) / vault.length).toFixed(1)
        : '0.0';
      const today = getTodayIsoDate();
      const due = vault.filter(i => !i.nextReviewDate || i.nextReviewDate <= today).length;

      const setTxt = (id, v) => { const el = document.getElementById(id); if (el) el.innerText = v; };
      setTxt('cog-bio-hrv-ref', `WHOOP HRV: ${tel.whoop.hrv} ms • Garmin Readiness: ${tel.garmin.readiness}`);
      setTxt('cog-bio-mastery-pct', `${pct}% Mastered`);
      setTxt('cog-bio-mastery-sub', `${mastered} / ${allCards.length} Vault & Omega Cards`);
      setTxt('cog-bio-spaced-lvl', `Avg Lvl ${avgLvl}`);
      setTxt('cog-bio-due-count', `${due} Cards Due Today`);

      if (gate.zone === 'GREEN') {
        setTxt('cog-bio-bandwidth', 'Peak Synthesis Cleared');
        setTxt('cog-bio-modality-advice', 'Green Gate (>66%): Ideal window for 90-min Doctoral Literature Matrix synthesis, complex PDF extraction, and Lvl 3+ recall.');
      } else if (gate.zone === 'YELLOW') {
        setTxt('cog-bio-bandwidth', 'Steady Consolidation');
        setTxt('cog-bio-modality-advice', 'Yellow Gate (34%–65%): Execute 20-min focused micro-sprints and clear Due Today 3Q quizzes before heavy writing.');
      } else {
        setTxt('cog-bio-bandwidth', 'Audio / Video Review Mode');
        setTxt('cog-bio-modality-advice', 'Red Gate (<33%): Protect nervous system recovery—use Car/Workout Audiobooks, Qari recitation, and light 3Q review.');
      }
    }"""

    if "window.checkLocalBrowserAiStatus =" not in html:
        html = html.replace(
            "    // Interactive 3Q Active-Recall Quiz Handlers",
            advanced_js + "\n\n    // Interactive 3Q Active-Recall Quiz Handlers",
            1,
        )

    # 10. Wire Blank-Page Generation Scratchpad reset inside openRecallQuiz
    old_open_quiz_tail = """      document.getElementById('quiz-modal-title').innerText = item.title;
      document.getElementById('quiz-score-banner').classList.add('hidden');"""

    new_open_quiz_tail = """      document.getElementById('quiz-modal-title').innerText = item.title;
      document.getElementById('quiz-score-banner').classList.add('hidden');
      const scratchInput = document.getElementById('generation-scratchpad-input');
      const qContEl = document.getElementById('quiz-questions-container');
      if (scratchInput) scratchInput.value = '';
      if (qContEl) qContEl.classList.add('hidden');"""

    if "getElementById('generation-scratchpad-input')" not in html and old_open_quiz_tail in html:
        html = html.replace(old_open_quiz_tail, new_open_quiz_tail, 1)

    # 11. Call renderBiometricCognitiveAnalytics() inside renderAllUI() and checkLocalBrowserAiStatus() on DOMContentLoaded
    if "renderBiometricCognitiveAnalytics();" not in html:
        html = html.replace(
            "      renderWearablesDashboards();",
            "      renderWearablesDashboards();\n      renderBiometricCognitiveAnalytics();",
            1,
        )
    if "checkLocalBrowserAiStatus();" not in html:
        html = html.replace(
            "      initPwaOtaEngine();",
            "      initPwaOtaEngine();\n      checkLocalBrowserAiStatus();",
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

    # Bump Service Worker cache version to ota-v4 so installed PWAs hot-reload immediately
    if os.path.exists(SW_PATH):
        with open(SW_PATH, "r", encoding="utf-8") as f:
            sw = f.read()
        sw = sw.replace("hive-alignment-ota-v3", "hive-alignment-ota-v4")
        with open(SW_PATH, "w", encoding="utf-8", newline="\n") as f:
            f.write(sw)

    print(f"Successfully patched {INDEX_PATH} & {SW_PATH}! JS syntax validated & {len(onclicks)} button handlers verified.")


if __name__ == "__main__":
    main()

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

    # 1. Update the Tab Headers to include 'Focus & Coping'
    old_tab_nav = r"""      <button type="button" onclick="switchTab('tab-workflows')" id="btn-tab-workflows" class="tab-btn px-4 py-2 rounded-lg text-sm font-semibold text-slate-400 hover:text-white transition">Agent Workflows</button>
      <button type="button" onclick="switchTab('tab-spiritual')" id="btn-tab-spiritual" class="tab-btn px-4 py-2 rounded-lg text-sm font-semibold text-slate-400 hover:text-white transition">Journal &amp; Accounting</button>"""

    new_tab_nav = r"""      <button type="button" onclick="switchTab('tab-workflows')" id="btn-tab-workflows" class="tab-btn px-4 py-2 rounded-lg text-sm font-semibold text-slate-400 hover:text-white transition">Agent Workflows</button>
      <button type="button" onclick="switchTab('tab-spiritual')" id="btn-tab-spiritual" class="tab-btn px-4 py-2 rounded-lg text-sm font-semibold text-sky-400 hover:text-sky-300 transition">Journal &amp; Focus Coping</button>"""

    if "Journal &amp; Focus Coping" not in html and old_tab_nav in html:
        html = html.replace(old_tab_nav, new_tab_nav, 1)

    # 2. Inject "Zeigarnik Open-Loop Parking Lot" globally under Active Battles Bar
    old_battles_bar = r"""        <button type="button" onclick="openOnboardingModal()" class="px-3 py-1.5 bg-slate-950 hover:bg-slate-800 border border-slate-800 text-slate-300 rounded-lg text-xs font-semibold">
          Change Battles
        </button>
      </div>
    </div>"""

    new_battles_bar = r"""        <button type="button" onclick="openOnboardingModal()" class="px-3 py-1.5 bg-slate-950 hover:bg-slate-800 border border-slate-800 text-slate-300 rounded-lg text-xs font-semibold">
          Change Battles
        </button>
      </div>
    </div>

    <!-- Zeigarnik Open-Loop Parking Lot (Global Focus Guard) -->
    <div class="p-3 bg-slate-900 border border-indigo-900/50 rounded-2xl flex flex-col sm:flex-row items-center gap-3 shadow-md">
      <span class="text-[10px] font-bold uppercase tracking-wider text-indigo-400 flex items-center gap-1.5 flex-shrink-0">
        <i data-lucide="brain-cog" class="w-3.5 h-3.5"></i> Open-Loop Dump
      </span>
      <form onsubmit="handleZeigarnikDump(event)" class="w-full flex gap-2">
        <input type="text" id="zeigarnik-input" placeholder="Urgent thought? Email to send? Dump it here to protect your focus block..." class="flex-grow bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500">
        <button type="submit" class="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl text-xs flex-shrink-0 transition">Park It</button>
      </form>
    </div>"""

    if "id=\"zeigarnik-input\"" not in html and old_battles_bar in html:
        html = html.replace(old_battles_bar, new_battles_bar, 1)

    # 3. Enhance tab-spiritual (Journal & Accounting) to include the Cyclic Sighing Pacer, CBT Reframe, and Focus Timer
    old_tab_spiritual = r"""    <!-- TAB: JOURNAL & ACCOUNTING -->
    <div id="tab-spiritual" class="tab-content space-y-6">
      <div class="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-3">
        <h3 class="text-base font-bold text-white">Encrypted Daily Self-Accountability Log (Muhasabah)</h3>
        <textarea id="muhasabah-notes" rows="4" placeholder="Write your private reflection here. Encrypted before leaving your browser..." class="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:border-emerald-500"></textarea>
        <div class="flex justify-between items-center">
          <span id="muhasabah-status" class="text-[11px] text-slate-500">Zero-knowledge encryption active (never shared in Accountability Pings)</span>
          <button type="button" onclick="saveMuhasabah()" class="px-4 py-1.5 bg-emerald-600 text-slate-950 font-bold rounded-lg text-xs">Encrypt &amp; Save</button>
        </div>
      </div>
    </div>"""

    new_tab_spiritual = r"""    <!-- TAB: JOURNAL, FOCUS SHIELD & AUTONOMIC COPING SUITE -->
    <div id="tab-spiritual" class="tab-content space-y-6">
      
      <!-- 5-Minute Cyclic Sighing & 40 Hz Focus Audio Suite -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Autonomic Coping Pacer -->
        <div class="bg-slate-900 border border-sky-800/50 rounded-2xl p-6 flex flex-col justify-between space-y-4 shadow-xl relative overflow-hidden">
          <div class="flex justify-between items-center z-10 relative">
            <span class="text-[10px] font-bold uppercase tracking-wider text-sky-400 flex items-center gap-1.5">
              <i data-lucide="wind" class="w-3.5 h-3.5"></i> Vagal Tone Rest &amp; Digest
            </span>
            <span id="breath-timer-badge" class="px-2 py-0.5 rounded bg-sky-950 border border-sky-800 text-[10px] text-sky-300 font-mono">5:00</span>
          </div>
          <div class="z-10 relative space-y-1">
            <h3 class="text-lg font-bold text-white">Cyclic Sighing Pacer</h3>
            <p class="text-xs text-slate-400">Stanford Protocol: Two nasal inhales followed by a prolonged, slow exhale. Lowers physiological anxiety.</p>
          </div>
          
          <!-- Animated Pacer Ring -->
          <div class="flex items-center justify-center py-4 z-10 relative">
            <div id="breath-pacer-ring" class="w-24 h-24 rounded-full border-4 border-slate-700 flex items-center justify-center transition-all duration-1000 ease-in-out">
              <span id="breath-pacer-text" class="text-xs font-bold text-slate-300 tracking-widest uppercase">Ready</span>
            </div>
          </div>

          <div class="flex gap-2 z-10 relative pt-2">
            <button type="button" onclick="startCyclicSighing()" class="flex-1 py-2 bg-sky-600 hover:bg-sky-500 text-white font-bold rounded-xl text-xs transition">Start 5-Min Reset</button>
            <button type="button" onclick="stopBreathPacer()" class="px-3 py-2 bg-slate-950 hover:bg-slate-800 border border-slate-700 text-slate-300 rounded-xl text-xs transition"><i data-lucide="square" class="w-3.5 h-3.5"></i></button>
          </div>
        </div>

        <!-- Offline Audio Focus Timer -->
        <div class="bg-slate-900 border border-indigo-800/50 rounded-2xl p-6 flex flex-col justify-between space-y-4 shadow-xl">
          <div class="flex justify-between items-center">
            <span class="text-[10px] font-bold uppercase tracking-wider text-indigo-400 flex items-center gap-1.5">
              <i data-lucide="headphones" class="w-3.5 h-3.5"></i> WebAudio API Generator
            </span>
            <span id="focus-timer-badge" class="px-2 py-0.5 rounded bg-indigo-950 border border-indigo-800 text-[10px] text-indigo-300 font-mono">50:00</span>
          </div>
          <div class="space-y-1">
            <h3 class="text-lg font-bold text-white">Ultradian Focus Lockdown</h3>
            <p class="text-xs text-slate-400">Generates offline Brown Noise locally. 50-minute deep block followed by a 10-minute screen-free reset.</p>
          </div>
          
          <div class="flex items-center gap-3 pt-2">
            <select id="focus-audio-type" class="flex-grow bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200">
              <option value="brown">Deep Brown Noise</option>
              <option value="pink">Pink Noise (Softer)</option>
              <option value="gamma">40 Hz Gamma Isochronic</option>
            </select>
          </div>

          <div class="flex gap-2 pt-2">
            <button type="button" onclick="startFocusLockdown()" class="flex-1 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl text-xs transition flex items-center justify-center gap-1.5">
              <i data-lucide="lock" class="w-3.5 h-3.5"></i> Engage 50-Min Focus
            </button>
            <button type="button" onclick="stopFocusLockdown()" class="px-3 py-2 bg-slate-950 hover:bg-slate-800 border border-slate-700 text-slate-300 rounded-xl text-xs transition"><i data-lucide="square" class="w-3.5 h-3.5"></i></button>
          </div>
        </div>
      </div>

      <!-- CBT Sabr Reframing & Daily Muhasabah -->
      <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-5 shadow-xl">
        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 border-b border-slate-800 pb-3">
          <div>
            <h3 class="text-base font-bold text-white">Encrypted Daily Self-Accountability (Muhasabah)</h3>
            <p class="text-[11px] text-slate-400">Zero-knowledge AES-GCM-256 encryption. Never exposed in accountability pings.</p>
          </div>
          <button type="button" onclick="loadCbtTemplate()" class="px-3 py-1.5 bg-slate-950 hover:bg-slate-800 border border-emerald-700/60 text-emerald-300 rounded-lg text-xs font-semibold transition flex items-center gap-1.5">
            <i data-lucide="shield-alert" class="w-3.5 h-3.5"></i> Load CBT Sabr Audit
          </button>
        </div>
        <textarea id="muhasabah-notes" rows="6" placeholder="Write your private reflection here, or click 'Load CBT Sabr Audit' to deconstruct a high-friction interaction..." class="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 font-mono focus:outline-none focus:border-emerald-500"></textarea>
        <div class="flex justify-between items-center">
          <span id="muhasabah-status" class="text-[11px] text-slate-500 font-mono">Encryption active</span>
          <button type="button" onclick="saveMuhasabah()" class="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold rounded-xl text-xs transition shadow-md">Encrypt &amp; Save Log</button>
        </div>
      </div>
    </div>"""

    if "id=\"tab-spiritual\"" in html and "Cyclic Sighing Pacer" not in html:
        html = html.replace(old_tab_spiritual, new_tab_spiritual, 1)

    # 4. Enhance renderAdaptiveWorkoutsTab (or renderAllUI task rendering) to cap Daily Tasks to 3 and show Email Batch rules
    # We will inject the Email Batch & Zeigarnik tasks renderer inside renderAllUI
    old_task_render = r"""      const tCont = document.getElementById('tasks-list-container');
      if (tCont) {
        tCont.innerHTML = (window.userAppState.tasks || []).map(t => `
          <div class="p-3 bg-slate-950 rounded-xl border border-slate-800 flex justify-between items-center">
            <span class="${t.completed ? 'line-through text-slate-500' : 'text-slate-200'}">${t.title}</span>
            <input type="checkbox" ${t.completed ? 'checked' : ''} onchange="toggleTask('${t.id}')">
          </div>
        `).join('') || '<p class="text-slate-500">No duties added yet.</p>';
      }"""

    new_task_render = r"""      const tCont = document.getElementById('tasks-list-container');
      if (tCont) {
        const tel = getWearableTelemetry();
        const gate = evaluateAutoRegulatorGate(tel);
        let taskCap = 3;
        if (gate.zone === 'YELLOW') taskCap = 2;
        if (gate.zone === 'RED') taskCap = 1;
        
        const allTasks = window.userAppState.tasks || [];
        const activeTasks = allTasks.slice(0, taskCap);
        const backlog = allTasks.slice(taskCap);

        const emailBatches = `
          <div class="mb-4 p-3.5 bg-slate-950 rounded-xl border border-sky-800/50 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
            <div>
              <span class="text-[10px] font-bold uppercase text-sky-400 flex items-center gap-1"><i data-lucide="mail" class="w-3 h-3"></i> 2-Window Email / Slack Batching</span>
              <p class="text-[11px] text-slate-400 mt-0.5">Protect attention residue. Check inbox only at <strong class="text-slate-200">11:30 AM</strong> (Pre-Dhuhr) and <strong class="text-slate-200">4:30 PM</strong> (Post-Asr).</p>
            </div>
            <span class="px-2 py-1 rounded bg-sky-950 text-sky-300 border border-sky-800 text-[10px] font-mono">Active</span>
          </div>`;

        let htmlStr = emailBatches;
        htmlStr += `<div class="flex justify-between items-end mb-2"><span class="text-[10px] font-bold uppercase text-emerald-400">Rule of 3 Focus (Gate Calibrated: ${gate.zone})</span><span class="text-[10px] font-mono text-slate-500">Cap: ${taskCap} Active</span></div>`;
        htmlStr += activeTasks.map(t => `
          <div class="mb-2 p-3 bg-slate-950 rounded-xl border ${t.completed ? 'border-slate-800 opacity-60' : 'border-emerald-800/60'} flex justify-between items-center shadow-sm">
            <span class="text-xs ${t.completed ? 'line-through text-slate-500' : 'text-slate-200 font-semibold'}">${t.title}</span>
            <input type="checkbox" ${t.completed ? 'checked' : ''} onchange="toggleTask('${t.id}')" class="w-4 h-4 rounded border-slate-700 bg-slate-900 text-emerald-500">
          </div>
        `).join('') || '<p class="text-xs text-slate-500 mb-2">No active duties.</p>';

        if (backlog.length > 0) {
          htmlStr += `<div class="mt-4 mb-2"><span class="text-[10px] font-bold uppercase text-slate-500">Backlog &amp; Zeigarnik Parking Lot (${backlog.length} Deferred)</span></div>`;
          htmlStr += backlog.map(t => `
            <div class="mb-1.5 p-2 bg-slate-950/50 rounded-lg border border-slate-800/50 flex justify-between items-center opacity-70">
              <span class="text-[11px] truncate ${t.completed ? 'line-through text-slate-600' : 'text-slate-400'}">${t.title}</span>
              <div class="flex items-center gap-2 flex-shrink-0">
                <button type="button" onclick="promoteTaskToActive('${t.id}')" class="text-[10px] text-indigo-400 hover:underline">Promote</button>
                <input type="checkbox" ${t.completed ? 'checked' : ''} onchange="toggleTask('${t.id}')" class="w-3 h-3 rounded bg-slate-900">
              </div>
            </div>
          `).join('');
        }
        tCont.innerHTML = htmlStr;
      }"""

    if "promoteTaskToActive(" not in html and old_task_render in html:
        html = html.replace(old_task_render, new_task_render, 1)

    # 5. Inject Focus Suite JS Engine (Zeigarnik Dump, Pacer, Audio Focus Timer, Task Promote)
    focus_js = r"""    // FOCUS SHIELD & AUTONOMIC COPING ENGINE
    window.handleZeigarnikDump = async function(e) {
      if (e) e.preventDefault();
      const inp = document.getElementById('zeigarnik-input');
      const val = inp.value.trim();
      if (!val) return;
      window.userAppState.tasks = window.userAppState.tasks || [];
      // Push to the end so it goes into the backlog
      window.userAppState.tasks.push({ id: 't_zg_' + Date.now(), title: val, completed: false });
      inp.value = '';
      renderAllUI();
      await pushCloudUserData();
    };

    window.promoteTaskToActive = async function(id) {
      window.userAppState.tasks = window.userAppState.tasks || [];
      const idx = window.userAppState.tasks.findIndex(t => t.id === id);
      if (idx > -1) {
        const [t] = window.userAppState.tasks.splice(idx, 1);
        window.userAppState.tasks.unshift(t);
        renderAllUI();
        await pushCloudUserData();
      }
    };

    window.loadCbtTemplate = function() {
      const template = `[CBT Sabr & Cognitive Reframe Audit]\n1. Trigger (What external event caused friction?):\n> \n\n2. Dichotomy Check (What part is actually within my control?):\n> \n\n3. Prophetic Reframe (My composed, Ihsan-driven response):\n> `;
      const el = document.getElementById('muhasabah-notes');
      if (el) {
        el.value = el.value ? el.value + '\n\n' + template : template;
        el.focus();
      }
    };

    // WebAudio Focus Engine (Brown Noise / Gamma)
    window.focusAudioCtx = null;
    window.focusNoiseNode = null;
    window.focusGainNode = null;
    window.focusOscNode = null;
    window.focusTimerInterval = null;
    window.focusSecondsLeft = 50 * 60;

    function createBrownNoise(audioCtx) {
      const bufferSize = audioCtx.sampleRate * 2;
      const buffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
      const output = buffer.getChannelData(0);
      let lastOut = 0;
      for (let i = 0; i < bufferSize; i++) {
        const white = Math.random() * 2 - 1;
        output[i] = (lastOut + (0.02 * white)) / 1.02;
        lastOut = output[i];
        output[i] *= 3.5;
      }
      const node = audioCtx.createBufferSource();
      node.buffer = buffer;
      node.loop = true;
      return node;
    }

    function createPinkNoise(audioCtx) {
      const bufferSize = audioCtx.sampleRate * 2;
      const buffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
      const output = buffer.getChannelData(0);
      let b0=0, b1=0, b2=0, b3=0, b4=0, b5=0, b6=0;
      for (let i = 0; i < bufferSize; i++) {
        const white = Math.random() * 2 - 1;
        b0 = 0.99886 * b0 + white * 0.0555179;
        b1 = 0.99332 * b1 + white * 0.0750759;
        b2 = 0.96900 * b2 + white * 0.1538520;
        b3 = 0.86650 * b3 + white * 0.3104856;
        b4 = 0.55000 * b4 + white * 0.5329522;
        b5 = -0.7616 * b5 - white * 0.0168980;
        output[i] = b0 + b1 + b2 + b3 + b4 + b5 + b6 + white * 0.5362;
        output[i] *= 0.11;
        b6 = white * 0.115926;
      }
      const node = audioCtx.createBufferSource();
      node.buffer = buffer;
      node.loop = true;
      return node;
    }

    window.startFocusLockdown = async function() {
      if (window.focusTimerInterval) clearInterval(window.focusTimerInterval);
      window.stopFocusLockdown(true); // silent stop to reset
      
      const type = document.getElementById('focus-audio-type')?.value || 'brown';
      window.focusAudioCtx = new (window.AudioContext || window.webkitAudioContext)();
      window.focusGainNode = window.focusAudioCtx.createGain();
      window.focusGainNode.gain.value = 0.15;
      window.focusGainNode.connect(window.focusAudioCtx.destination);

      if (type === 'brown' || type === 'pink') {
        window.focusNoiseNode = type === 'brown' ? createBrownNoise(window.focusAudioCtx) : createPinkNoise(window.focusAudioCtx);
        window.focusNoiseNode.connect(window.focusGainNode);
        window.focusNoiseNode.start();
      } else if (type === 'gamma') {
        // 40Hz Isochronic tone (200Hz base modulated at 40Hz)
        window.focusOscNode = window.focusAudioCtx.createOscillator();
        window.focusOscNode.type = 'sine';
        window.focusOscNode.frequency.value = 200;
        const modNode = window.focusAudioCtx.createOscillator();
        modNode.type = 'square';
        modNode.frequency.value = 40;
        const modGain = window.focusAudioCtx.createGain();
        modGain.gain.value = 1;
        modNode.connect(modGain.gain);
        window.focusOscNode.connect(modGain);
        modGain.connect(window.focusGainNode);
        window.focusOscNode.start();
        modNode.start();
        window.focusNoiseNode = { stop: () => { window.focusOscNode.stop(); modNode.stop(); } };
      }

      window.focusSecondsLeft = 50 * 60; // 50 Mins
      if (typeof window.requestAvWakeLock === 'function') window.requestAvWakeLock();

      window.focusTimerInterval = setInterval(() => {
        window.focusSecondsLeft--;
        const m = String(Math.floor(Math.max(0, window.focusSecondsLeft) / 60)).padStart(2, '0');
        const s = String(Math.max(0, window.focusSecondsLeft) % 60).padStart(2, '0');
        const badge = document.getElementById('focus-timer-badge');
        if (badge) badge.innerText = `${m}:${s}`;
        if (window.focusSecondsLeft <= 0) {
          window.stopFocusLockdown();
          if (badge) badge.innerText = "DONE - Screen-Free Rest";
          if (typeof window.firePwaLocalNotification === 'function') {
            window.firePwaLocalNotification('Focus Sprint Complete', '50 minutes achieved. Step away from the screen for 10 minutes.');
          }
        }
      }, 1000);
    };

    window.stopFocusLockdown = function(silent) {
      if (window.focusTimerInterval) clearInterval(window.focusTimerInterval);
      if (window.focusNoiseNode) {
        try { window.focusNoiseNode.stop(); } catch(e){}
        window.focusNoiseNode = null;
      }
      if (window.focusAudioCtx) {
        window.focusAudioCtx.close();
        window.focusAudioCtx = null;
      }
      if (typeof window.releaseAvWakeLock === 'function') window.releaseAvWakeLock();
      if (!silent) {
        const badge = document.getElementById('focus-timer-badge');
        if (badge) badge.innerText = "50:00";
      }
    };

    // Cyclic Sighing Pacer
    window.pacerInterval = null;
    window.pacerPhase = 0; // 0=Inhale1, 1=Inhale2, 2=Exhale
    window.pacerTicks = 0;
    window.pacerTotalSeconds = 5 * 60;

    window.startCyclicSighing = function() {
      if (window.pacerInterval) clearInterval(window.pacerInterval);
      window.pacerPhase = 0;
      window.pacerTicks = 0;
      window.pacerTotalSeconds = 5 * 60;
      const ring = document.getElementById('breath-pacer-ring');
      const text = document.getElementById('breath-pacer-text');
      const badge = document.getElementById('breath-timer-badge');
      if (typeof window.requestAvWakeLock === 'function') window.requestAvWakeLock();

      window.pacerInterval = setInterval(() => {
        window.pacerTotalSeconds--;
        if (window.pacerTotalSeconds <= 0) {
          window.stopBreathPacer();
          if (text) text.innerText = 'DONE';
          return;
        }
        if (badge) {
          const m = String(Math.floor(window.pacerTotalSeconds / 60)).padStart(2, '0');
          const s = String(window.pacerTotalSeconds % 60).padStart(2, '0');
          badge.innerText = `${m}:${s}`;
        }
      }, 1000);

      const runPhase = () => {
        if (window.pacerTotalSeconds <= 0) return;
        if (window.pacerPhase === 0) {
          if (ring) { ring.style.transform = 'scale(1.4)'; ring.style.borderColor = '#38bdf8'; }
          if (text) { text.innerText = 'INHALE'; text.style.color = '#38bdf8'; }
          window.pacerPhase = 1;
          window.pacerTicks = setTimeout(runPhase, 2000);
        } else if (window.pacerPhase === 1) {
          if (ring) { ring.style.transform = 'scale(1.6)'; ring.style.borderColor = '#10b981'; }
          if (text) { text.innerText = 'TOP-UP'; text.style.color = '#10b981'; }
          window.pacerPhase = 2;
          window.pacerTicks = setTimeout(runPhase, 1000);
        } else if (window.pacerPhase === 2) {
          if (ring) { ring.style.transform = 'scale(1.0)'; ring.style.borderColor = '#818cf8'; }
          if (text) { text.innerText = 'SLOW EXHALE'; text.style.color = '#818cf8'; }
          window.pacerPhase = 0;
          window.pacerTicks = setTimeout(runPhase, 5000);
        }
      };
      runPhase();
    };

    window.stopBreathPacer = function() {
      if (window.pacerInterval) clearInterval(window.pacerInterval);
      if (window.pacerTicks) clearTimeout(window.pacerTicks);
      const ring = document.getElementById('breath-pacer-ring');
      const text = document.getElementById('breath-pacer-text');
      const badge = document.getElementById('breath-timer-badge');
      if (ring) { ring.style.transform = 'scale(1.0)'; ring.style.borderColor = '#334155'; }
      if (text) { text.innerText = 'READY'; text.style.color = '#cbd5e1'; }
      if (badge) badge.innerText = '5:00';
      if (typeof window.releaseAvWakeLock === 'function') window.releaseAvWakeLock();
    };"""

    if "function handleZeigarnikDump" not in html:
        html = html.replace(
            "    // Interactive 3Q Active-Recall Quiz Handlers",
            focus_js + "\n\n    // Interactive 3Q Active-Recall Quiz Handlers",
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
        sw = re.sub(r"hive-alignment-ota-v\d+", "hive-alignment-ota-v7", sw)
        with open(SW_PATH, "w", encoding="utf-8", newline="\n") as f:
            f.write(sw)

    print(f"Successfully added Focus & Coping Suite (Zeigarnik, Pacer, Timer, Emails). ({len(onclicks)} button handlers verified)")


if __name__ == "__main__":
    main()

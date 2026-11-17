import os
import re

INDEX_PATH = os.path.join("docs", "index.html")

def main():
    if not os.path.exists(INDEX_PATH):
        raise FileNotFoundError(f"Could not find {INDEX_PATH}.")

    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Inject Audiobook / Visual Video Synth Modal
    av_modal_html = """  <!-- AUDIOBOOK & VISUAL SYNTH VIDEO PLAYER MODAL -->
  <div id="av-synth-modal" class="fixed inset-0 bg-slate-950/95 backdrop-blur-md z-[1230] hidden flex-col items-center justify-center p-4">
    <div class="bg-slate-900 border border-indigo-700/60 rounded-2xl w-full max-w-4xl overflow-hidden shadow-2xl flex flex-col h-[85vh] md:h-[600px] relative">
      <!-- Header -->
      <div class="flex justify-between items-center p-4 border-b border-slate-800 bg-slate-950">
        <div class="flex items-center gap-2 text-indigo-400">
          <i data-lucide="play-circle" class="w-5 h-5"></i>
          <span class="font-bold text-sm tracking-wide">Cognitive A/V Player</span>
          <span id="av-mode-badge" class="ml-2 text-[10px] bg-indigo-900/50 text-indigo-300 px-2 py-0.5 rounded font-mono">AUDIOBOOK</span>
        </div>
        <button type="button" onclick="closeAvPlayer()" class="text-slate-400 hover:text-white"><i data-lucide="x"></i></button>
      </div>
      
      <!-- Visual Video Screen -->
      <div id="av-visual-screen" class="flex-grow bg-black relative flex items-center justify-center p-8 text-center transition-colors duration-1000 overflow-hidden">
        <div class="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent z-0"></div>
        <h2 id="av-visual-text" class="text-3xl md:text-5xl font-extrabold text-white drop-shadow-2xl leading-tight transition-opacity duration-300 z-10 px-4">Initializing Synth...</h2>
        <div class="absolute bottom-4 left-6 right-6 flex justify-between items-center text-xs font-mono text-slate-400 z-10">
          <span id="av-visual-progress">0%</span>
          <span id="av-visual-topic" class="truncate max-w-[60%]">Topic Name</span>
        </div>
      </div>

      <!-- Controls -->
      <div class="p-4 bg-slate-950 border-t border-slate-800 flex flex-col gap-4">
        <div class="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden cursor-pointer" id="av-progress-bar-container">
          <div id="av-progress-bar" class="bg-indigo-500 h-full w-0 transition-all duration-300"></div>
        </div>
        <div class="flex justify-between items-center">
          <div class="flex items-center gap-5">
            <button type="button" onclick="avTogglePlay()" id="av-btn-play" class="text-white hover:text-indigo-400 transition"><i data-lucide="play" class="w-6 h-6 fill-current"></i></button>
            <button type="button" onclick="avStop()" class="text-slate-400 hover:text-white transition"><i data-lucide="square" class="w-5 h-5 fill-current"></i></button>
          </div>
          <div class="flex items-center gap-3">
            <select id="av-voice-select" onchange="avChangeVoice()" class="bg-slate-900 border border-slate-700 rounded-lg px-2 py-1.5 text-xs text-slate-300 max-w-[130px] truncate focus:outline-none"></select>
            <button type="button" onclick="avCycleSpeed()" id="av-btn-speed" class="text-xs font-bold text-slate-200 bg-slate-800 px-3 py-1.5 rounded-lg hover:bg-slate-700 transition w-14 text-center">1.0x</button>
          </div>
        </div>
      </div>
    </div>
  </div>"""

    if 'id="av-synth-modal"' not in html:
        html = html.replace("  <!-- MODALS -->", av_modal_html + "\n\n  <!-- MODALS -->", 1)

    # 2. Inject JS Engine
    av_js = """    // COGNITIVE AUDIOBOOK & VISUAL VIDEO SYNTHESIS ENGINE
    window.avSynthQueue = [];
    window.avCurrentIndex = 0;
    window.avIsPlaying = false;
    window.avMode = 'audio';
    window.avRate = 1.0;
    window.avVoices = [];
    window.avUtterance = null;

    function initVoices() {
      window.avVoices = speechSynthesis.getVoices().filter(v => v.lang.startsWith('en'));
      const sel = document.getElementById('av-voice-select');
      if (sel && window.avVoices.length) {
        sel.innerHTML = window.avVoices.map((v, i) => `<option value="${i}">${v.name.replace('Google', 'Synth').replace('Microsoft', 'Synth')}</option>`).join('');
      }
    }
    if (speechSynthesis.onvoiceschanged !== undefined) {
      speechSynthesis.onvoiceschanged = initVoices;
    }

    window.launchAvPlayer = function(itemId, mode) {
      const vault = window.userAppState.knowledgeVault || [];
      const omega = window.userAppState.omegaNotebooks || [];
      const item = vault.find(v => v.id === itemId) || omega.find(o => o.id === itemId);
      if (!item) return;

      window.avMode = mode;
      document.getElementById('av-mode-badge').innerText = mode === 'video' ? 'VISUAL SYNTH' : 'AUDIOBOOK';
      const screen = document.getElementById('av-visual-screen');
      if (mode === 'video') {
        screen.classList.remove('hidden');
        screen.classList.add('flex');
      } else {
        screen.classList.add('hidden');
        screen.classList.remove('flex');
        // keep min-height small for audio mode
        document.querySelector('#av-synth-modal > div').style.height = 'auto';
      }

      document.getElementById('av-visual-topic').innerText = item.title;

      const q = [];
      q.push(item.title);
      q.push("Core Takeaway: " + (item.takeaway || ''));
      
      const contentSentences = (item.content || '').replace(/--- Page \\d+ ---/g, '').split(/(?<=[.!?])\\s+/).filter(s => s.trim().length > 10);
      contentSentences.forEach(s => q.push(s.trim()));
      
      if (item.microSteps && item.microSteps.length) {
        q.push("Distilled Micro-Steps.");
        item.microSteps.forEach(s => q.push(s.replace(/^\\d+\\.\\s*/, '')));
      }

      if (item.quiz && item.quiz.length) {
        q.push("Active Recall Quiz.");
        item.quiz.forEach((qz, idx) => {
          q.push(`Question ${idx + 1}. ` + qz.q.replace(/^\\d+\\.\\s*/, ''));
          q.push(`Answer. ` + qz.a);
        });
      }

      window.avSynthQueue = q;
      window.avCurrentIndex = 0;
      const modal = document.getElementById('av-synth-modal');
      modal.classList.remove('hidden');
      modal.classList.add('flex');
      
      if (!window.avVoices.length) initVoices();
      
      setTimeout(() => { avPlayChunk(); }, 500);
    };

    window.avPlayChunk = function() {
      if (window.avCurrentIndex >= window.avSynthQueue.length) {
        avStop();
        document.getElementById('av-visual-text').innerText = "Session Complete.";
        return;
      }
      
      const text = window.avSynthQueue[window.avCurrentIndex];
      window.avUtterance = new SpeechSynthesisUtterance(text);
      window.avUtterance.rate = window.avRate;
      
      const vIdx = document.getElementById('av-voice-select')?.value;
      if (vIdx && window.avVoices[vIdx]) window.avUtterance.voice = window.avVoices[vIdx];

      document.getElementById('av-visual-text').innerText = text;
      const pct = Math.round((window.avCurrentIndex / window.avSynthQueue.length) * 100);
      document.getElementById('av-progress-bar').style.width = pct + '%';
      document.getElementById('av-visual-progress').innerText = `${pct}%`;

      if (window.avMode === 'video') {
         const colors = ['#1e1b4b', '#312e81', '#064e3b', '#4a044e', '#450a0a', '#0f172a', '#3f3f46'];
         document.getElementById('av-visual-screen').style.backgroundColor = colors[window.avCurrentIndex % colors.length];
      }

      window.avUtterance.onend = () => {
        window.avCurrentIndex++;
        if (window.avIsPlaying) setTimeout(() => { avPlayChunk(); }, 250);
      };
      
      window.avUtterance.onerror = (e) => {
        console.warn("Speech synth interupted", e);
      };

      window.avIsPlaying = true;
      document.getElementById('av-btn-play').innerHTML = '<i data-lucide="pause" class="w-6 h-6 fill-current"></i>';
      if (window.lucide) lucide.createIcons();
      
      speechSynthesis.cancel();
      speechSynthesis.speak(window.avUtterance);
    };

    window.avTogglePlay = function() {
      if (window.avIsPlaying) {
        speechSynthesis.pause();
        window.avIsPlaying = false;
        document.getElementById('av-btn-play').innerHTML = '<i data-lucide="play" class="w-6 h-6 fill-current"></i>';
      } else {
        if (speechSynthesis.paused) {
          speechSynthesis.resume();
          window.avIsPlaying = true;
          document.getElementById('av-btn-play').innerHTML = '<i data-lucide="pause" class="w-6 h-6 fill-current"></i>';
        } else {
          avPlayChunk();
        }
      }
      if (window.lucide) lucide.createIcons();
    };

    window.avStop = function() {
      speechSynthesis.cancel();
      window.avIsPlaying = false;
      window.avCurrentIndex = 0;
      document.getElementById('av-btn-play').innerHTML = '<i data-lucide="play" class="w-6 h-6 fill-current"></i>';
      document.getElementById('av-progress-bar').style.width = '0%';
      if (window.lucide) lucide.createIcons();
    };

    window.closeAvPlayer = function() {
      avStop();
      const modal = document.getElementById('av-synth-modal');
      modal.classList.add('hidden');
      modal.classList.remove('flex');
      document.querySelector('#av-synth-modal > div').style.height = '';
    };

    window.avChangeVoice = function() {
      if (window.avIsPlaying) {
        speechSynthesis.cancel();
        avPlayChunk();
      }
    };

    window.avCycleSpeed = function() {
      const speeds = [1.0, 1.25, 1.5, 1.75, 2.0];
      const cur = speeds.indexOf(window.avRate);
      window.avRate = speeds[(cur + 1) % speeds.length];
      document.getElementById('av-btn-speed').innerText = window.avRate.toFixed(2) + 'x';
      if (window.avIsPlaying) {
        speechSynthesis.cancel();
        avPlayChunk();
      }
    };"""

    if "function launchAvPlayer(" not in html:
        html = html.replace(
            "    // Interactive 3Q Active-Recall Quiz Handlers",
            av_js + "\n\n    // Interactive 3Q Active-Recall Quiz Handlers",
            1,
        )

    # 3. Add Audio & Visual Buttons to Polymath & Omega Cards
    polymath_quiz_html = '<i data-lucide="help-circle" class="w-3 h-3"></i> Quiz (3Q)\n                  </button>'
    polymath_buttons = """<i data-lucide="help-circle" class="w-3 h-3"></i> Quiz (3Q)
                  </button>
                  <button type="button" onclick="launchAvPlayer('${item.id}', 'audio')" class="px-2.5 py-1 bg-indigo-950 hover:bg-indigo-900 text-indigo-300 border border-indigo-800 rounded-lg text-[11px] font-bold flex items-center gap-1 shadow-sm"><i data-lucide="headphones" class="w-3 h-3"></i> Audio</button>
                  <button type="button" onclick="launchAvPlayer('${item.id}', 'video')" class="px-2.5 py-1 bg-purple-950 hover:bg-purple-900 text-purple-300 border border-purple-800 rounded-lg text-[11px] font-bold flex items-center gap-1 shadow-sm"><i data-lucide="monitor-play" class="w-3 h-3"></i> Video</button>"""
    
    if "launchAvPlayer('${item.id}', 'audio')" not in html and polymath_quiz_html in html:
        html = html.replace(polymath_quiz_html, polymath_buttons, 1)

    omega_quiz_html = '<i data-lucide="help-circle" class="w-3 h-3"></i> Drill Quiz (3Q)\n                </button>'
    omega_buttons = """<i data-lucide="help-circle" class="w-3 h-3"></i> Drill Quiz (3Q)
                </button>
                <button type="button" onclick="launchAvPlayer('${item.id}', 'audio')" class="px-2.5 py-1 bg-indigo-950 hover:bg-indigo-900 text-indigo-300 border border-indigo-800 rounded-lg text-[11px] font-bold flex items-center gap-1 shadow-sm"><i data-lucide="headphones" class="w-3 h-3"></i> Audio</button>
                <button type="button" onclick="launchAvPlayer('${item.id}', 'video')" class="px-2.5 py-1 bg-purple-950 hover:bg-purple-900 text-purple-300 border border-purple-800 rounded-lg text-[11px] font-bold flex items-center gap-1 shadow-sm"><i data-lucide="monitor-play" class="w-3 h-3"></i> Video</button>"""
    
    if "launchAvPlayer('${item.id}', 'audio')" not in html and omega_quiz_html in html:
        html = html.replace(omega_quiz_html, omega_buttons, 1)

    with open(INDEX_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)

    print("Patched index.html with Web Speech API Audio & Visual Synthesis Engines!")

if __name__ == "__main__":
    main()

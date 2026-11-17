import os
import re

INDEX_PATH = os.path.join("docs", "index.html")


def main():
    if not os.path.exists(INDEX_PATH):
        raise FileNotFoundError(f"Could not find {INDEX_PATH}. Run this script from the repository root.")

    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Add "+ YouTube Video" button to Knowledge & Micro-Learning toolbar
    old_web_url_btn = """            <button type="button" onclick="openIngestModal('url')" class="px-3 py-1.5 bg-indigo-950 hover:bg-indigo-900 border border-indigo-800 text-indigo-300 font-semibold rounded-xl text-xs transition flex items-center gap-1.5">
              <i data-lucide="globe" class="w-3.5 h-3.5"></i> Web URL
            </button>"""

    new_web_url_btn = """            <button type="button" onclick="openYouTubeModal('knowledge')" class="px-3.5 py-1.5 bg-rose-600 hover:bg-rose-500 text-white font-bold rounded-xl text-xs transition flex items-center gap-1.5 shadow-sm">
              <i data-lucide="youtube" class="w-3.5 h-3.5"></i> + YouTube Video
            </button>
            <button type="button" onclick="openIngestModal('url')" class="px-3 py-1.5 bg-indigo-950 hover:bg-indigo-900 border border-indigo-800 text-indigo-300 font-semibold rounded-xl text-xs transition flex items-center gap-1.5">
              <i data-lucide="globe" class="w-3.5 h-3.5"></i> Web URL
            </button>"""

    if 'onclick="openYouTubeModal(' not in html and old_web_url_btn in html:
        html = html.replace(old_web_url_btn, new_web_url_btn, 1)

    # 2. Add "+ YouTube Lecture" button in Seeker Study (Omega) toolbar as well
    old_omega_paste_btn = """            <button type="button" onclick="openOmegaNoteModal()" class="px-3.5 py-2 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded-xl text-xs transition flex items-center gap-1.5 shadow-lg">
              <i data-lucide="plus" class="w-3.5 h-3.5"></i> Paste Note
            </button>"""

    new_omega_paste_btn = """            <button type="button" onclick="openYouTubeModal('omega')" class="px-3.5 py-2 bg-rose-600 hover:bg-rose-500 text-white font-bold rounded-xl text-xs transition flex items-center gap-1.5 shadow-lg">
              <i data-lucide="youtube" class="w-3.5 h-3.5"></i> + YouTube Lecture
            </button>
            <button type="button" onclick="openOmegaNoteModal()" class="px-3.5 py-2 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded-xl text-xs transition flex items-center gap-1.5 shadow-lg">
              <i data-lucide="plus" class="w-3.5 h-3.5"></i> Paste Note
            </button>"""

    if "openYouTubeModal('omega')" not in html and old_omega_paste_btn in html:
        html = html.replace(old_omega_paste_btn, new_omega_paste_btn, 1)

    # 3. Add Watch Video button to the Top Tailored Micro-Learning Card when active item is a video
    old_top_quiz_btn = """            <button type="button" onclick="openActiveRecallQuiz()" class="px-2.5 py-1 bg-emerald-600 hover:bg-emerald-500 text-slate-950 rounded-lg text-xs font-bold transition flex items-center gap-1">
              <i data-lucide="help-circle" class="w-3 h-3"></i> Quiz (3Q)
            </button>"""

    new_top_quiz_btn = """            <button type="button" id="active-micro-watch-btn" onclick="openActiveVideoTheater()" class="hidden px-2.5 py-1 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-xs font-bold transition items-center gap-1">
              <i data-lucide="play-circle" class="w-3 h-3"></i> Watch
            </button>
            <button type="button" onclick="openActiveRecallQuiz()" class="px-2.5 py-1 bg-emerald-600 hover:bg-emerald-500 text-slate-950 rounded-lg text-xs font-bold transition flex items-center gap-1">
              <i data-lucide="help-circle" class="w-3 h-3"></i> Quiz (3Q)
            </button>"""

    if 'id="active-micro-watch-btn"' not in html and old_top_quiz_btn in html:
        html = html.replace(old_top_quiz_btn, new_top_quiz_btn, 1)

    # 4. Add YouTube Video Ingestion Modal & Visual Learning Theater Modal before <!-- MODALS -->
    youtube_modals_html = """  <!-- Add YouTube Video Reference & Visual Learning Modal -->
  <div id="youtube-ingest-modal" class="fixed inset-0 bg-slate-950/95 backdrop-blur-md z-[1180] hidden flex items-center justify-center p-4 overflow-y-auto">
    <div class="bg-slate-900 border border-rose-700/60 rounded-2xl max-w-xl w-full p-6 space-y-4 shadow-2xl relative my-8">
      <div class="flex justify-between items-start border-b border-slate-800 pb-3">
        <div>
          <span class="text-[10px] font-bold uppercase tracking-wider text-rose-400 flex items-center gap-1.5">
            <i data-lucide="youtube" class="w-3.5 h-3.5"></i> Visual Learning &amp; Video Reference Engine
          </span>
          <h3 class="text-base font-bold text-white mt-0.5">Add YouTube Lecture, Tutorial, or Study Video</h3>
        </div>
        <button type="button" onclick="closeYouTubeModal()" class="text-slate-400 hover:text-white text-xl leading-none">&times;</button>
      </div>

      <div class="space-y-2 text-xs">
        <label class="text-slate-400 block font-medium">YouTube Video URL (Watch, Short, Share, or Embed Link)</label>
        <div class="flex gap-2">
          <input type="url" id="yt-url-input" oninput="previewYouTubeMetadata()" placeholder="https://www.youtube.com/watch?v=... or https://youtu.be/..." class="flex-grow bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-slate-200 font-mono focus:outline-none focus:border-rose-500">
          <button type="button" id="yt-fetch-meta-btn" onclick="previewYouTubeMetadata(true)" class="px-3.5 py-2 bg-rose-600 hover:bg-rose-500 text-white font-bold rounded-xl flex-shrink-0">
            Fetch Info
          </button>
        </div>
        <p id="yt-fetch-status" class="text-[11px] text-rose-300 hidden"></p>
      </div>

      <!-- Live Video Thumbnail & Embed Preview -->
      <div id="yt-preview-card" class="hidden p-3 bg-slate-950 rounded-xl border border-slate-800 flex items-center gap-3">
        <img id="yt-preview-thumb" src="" alt="Video Thumbnail" class="w-28 h-16 object-cover rounded-lg border border-slate-700 flex-shrink-0">
        <div class="min-w-0 flex-1">
          <span id="yt-preview-channel" class="text-[10px] font-mono text-rose-400 uppercase block truncate">YouTube Channel</span>
          <p id="yt-preview-title" class="text-xs font-bold text-white truncate">Video Title Preview</p>
          <span id="yt-preview-id-tag" class="text-[10px] font-mono text-slate-500 block mt-0.5">ID: --</span>
        </div>
      </div>

      <form onsubmit="handleSaveYouTubeVideo(event)" class="space-y-3 text-xs">
        <input type="hidden" id="yt-target-vault" value="knowledge">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label class="text-slate-400 block mb-1 font-medium">Video Title</label>
            <input type="text" id="yt-title-input" required placeholder="Auto-filled from YouTube or type title..." class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200">
          </div>
          <div>
            <label class="text-slate-400 block mb-1 font-medium">Pillar / Category</label>
            <select id="yt-domain-input" class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200">
              <option value="Doctoral Studies">Doctoral Studies (Jan 2027)</option>
              <option value="Faith">Faith &amp; Quran / Hadith</option>
              <option value="Health">Health &amp; Physiology</option>
              <option value="Family">Family &amp; Leadership</option>
              <option value="Omega">Omega &amp; Heritage</option>
              <option value="Polymath" selected>Polymath / Visual Reference</option>
            </select>
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label class="text-slate-400 block mb-1 font-medium">Speaker / Channel (Optional)</label>
            <input type="text" id="yt-channel-input" placeholder="e.g., Huberman Lab, Yaqeen Institute, Dr. Just..." class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2 text-slate-200">
          </div>
          <div>
            <label class="text-slate-400 block mb-1 font-medium">Key Timestamp Anchor (Optional)</label>
            <input type="text" id="yt-timestamp-input" placeholder="e.g., 04:20 Core Framework, 18:10 Case Study" class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2 text-slate-200 font-mono">
          </div>
        </div>

        <div>
          <label class="text-slate-400 block mb-1 font-medium">Visual Takeaways, Transcript Notes, or Key Concepts</label>
          <textarea id="yt-notes-input" rows="4" required placeholder="Paste video summary, key timestamps, or concepts you want distilled into micro-steps and a 3-question active-recall quiz..." class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200 font-mono"></textarea>
        </div>

        <div class="flex justify-end gap-2 pt-2 border-t border-slate-800">
          <button type="button" onclick="closeYouTubeModal()" class="px-4 py-2 bg-slate-800 text-slate-300 rounded-xl font-semibold">Cancel</button>
          <button type="submit" class="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white font-bold rounded-xl flex items-center gap-1.5">
            <i data-lucide="play" class="w-3.5 h-3.5"></i> Save Video &amp; Build 3Q Quiz
          </button>
        </div>
      </form>
    </div>
  </div>

  <!-- Visual Learning Theater & Timestamped Note Modal -->
  <div id="video-theater-modal" class="fixed inset-0 bg-slate-950/95 backdrop-blur-md z-[1220] hidden flex items-center justify-center p-4 overflow-y-auto">
    <div class="bg-slate-900 border border-rose-700/60 rounded-2xl max-w-4xl w-full p-6 space-y-4 shadow-2xl relative my-6">
      <div class="flex justify-between items-start border-b border-slate-800 pb-3 gap-3">
        <div class="min-w-0">
          <span id="theater-domain-badge" class="text-[10px] font-bold uppercase tracking-wider text-rose-400 flex items-center gap-1.5">
            <i data-lucide="youtube" class="w-3.5 h-3.5"></i> Visual Learning Theater
          </span>
          <h3 id="theater-video-title" class="text-base font-bold text-white mt-0.5 truncate">Video Reference</h3>
        </div>
        <div class="flex items-center gap-2 flex-shrink-0">
          <a id="theater-external-link" href="#" target="_blank" rel="noopener noreferrer" class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-semibold flex items-center gap-1">
            YouTube &nearr;
          </a>
          <button type="button" onclick="closeVideoTheaterModal()" class="text-slate-400 hover:text-white text-xl leading-none px-1">&times;</button>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-5 gap-4">
        <div class="lg:col-span-3 space-y-2">
          <div class="relative w-full overflow-hidden rounded-xl border border-slate-800 bg-black" style="padding-top: 56.25%;">
            <iframe id="theater-youtube-iframe" src="" title="YouTube Visual Learning Player" class="absolute inset-0 w-full h-full" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
          </div>
          <p id="theater-channel-meta" class="text-[11px] text-slate-400 font-mono"></p>
        </div>

        <div class="lg:col-span-2 flex flex-col justify-between bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-3 text-xs">
          <div class="space-y-2.5 overflow-y-auto max-h-72">
            <div>
              <span class="text-[10px] font-bold uppercase text-emerald-400 block mb-1">Distilled Visual Micro-Steps:</span>
              <div id="theater-micro-steps" class="space-y-1 text-[11px] text-slate-300"></div>
            </div>
            <div class="pt-2 border-t border-slate-800">
              <label class="text-[10px] font-bold uppercase text-sky-400 block mb-1">Live Study Notes &amp; Timestamps:</label>
              <textarea id="theater-notes-editor" rows="5" class="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-[11px] text-slate-200 font-mono focus:outline-none focus:border-sky-500" placeholder="Jot down timestamps (e.g., 12:45 - Key equation) while watching..."></textarea>
            </div>
          </div>

          <div class="flex flex-wrap justify-between items-center gap-2 pt-2 border-t border-slate-800">
            <button type="button" onclick="saveTheaterNotes()" class="px-3 py-1.5 bg-sky-600 hover:bg-sky-500 text-slate-950 font-bold rounded-lg text-[11px]">
              Save Notes
            </button>
            <button type="button" onclick="launchQuizFromTheater()" class="px-3 py-1.5 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold rounded-lg text-[11px] flex items-center gap-1">
              <i data-lucide="help-circle" class="w-3.5 h-3.5"></i> Run 3Q Quiz
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>"""

    if 'id="youtube-ingest-modal"' not in html:
        html = html.replace("  <!-- MODALS -->", youtube_modals_html + "\n\n  <!-- MODALS -->", 1)

    # 5. Add 'Videos' filter pill and video player rendering inside renderPolymathVaultUI
    old_domains_line = "const domains = ['All', 'Due Today', 'Doctoral Studies', 'Faith', 'Health', 'Family', 'Omega', 'Polymath'];"
    new_domains_line = "const domains = ['All', 'Due Today', 'Videos', 'Doctoral Studies', 'Faith', 'Health', 'Family', 'Omega', 'Polymath'];"
    if "'Videos'" not in html and old_domains_line in html:
        html = html.replace(old_domains_line, new_domains_line, 1)

    old_count_logic = """          if (dom === 'All') count = vault.length;
          else if (dom === 'Due Today') count = dueCount;
          else count = vault.filter(i => getDomain(i) === dom).length;"""
    new_count_logic = """          if (dom === 'All') count = vault.length;
          else if (dom === 'Due Today') count = dueCount;
          else if (dom === 'Videos') count = vault.filter(i => !!i.videoId).length;
          else count = vault.filter(i => getDomain(i) === dom).length;"""
    if "dom === 'Videos'" not in html and old_count_logic in html:
        html = html.replace(old_count_logic, new_count_logic, 1)

    old_filter_logic = """      if (window.activePolymathDomain === 'Due Today') filtered = vault.filter(isDue);
      else if (window.activePolymathDomain !== 'All') filtered = vault.filter(i => getDomain(i) === window.activePolymathDomain);"""
    new_filter_logic = """      if (window.activePolymathDomain === 'Due Today') filtered = vault.filter(isDue);
      else if (window.activePolymathDomain === 'Videos') filtered = vault.filter(i => !!i.videoId);
      else if (window.activePolymathDomain !== 'All') filtered = vault.filter(i => getDomain(i) === window.activePolymathDomain);"""
    if "activePolymathDomain === 'Videos'" not in html and old_filter_logic in html:
        html = html.replace(old_filter_logic, new_filter_logic, 1)

    # Enhance Vault Card Rendering to show YouTube Thumbnail/Embed & Watch Button
    old_kv_card_title = """                <h4 class="font-bold text-white text-sm">${item.title}</h4>
                ${item.quizScore ? `<p class="text-[10px] font-mono text-emerald-400">Retention Status: ${item.quizScore}</p>` : ''}"""

    new_kv_card_title = """                <h4 class="font-bold text-white text-sm">${item.title}</h4>
                ${item.videoId ? `
                  <div onclick="openVideoTheater('${item.id}')" class="relative group cursor-pointer rounded-xl overflow-hidden border border-rose-800/50 bg-black aspect-video">
                    <img src="https://i.ytimg.com/vi/${item.videoId}/hqdefault.jpg" alt="${item.title}" class="w-full h-full object-cover opacity-85 group-hover:opacity-100 transition">
                    <div class="absolute inset-0 bg-slate-950/35 group-hover:bg-slate-950/15 transition flex items-center justify-center">
                      <div class="w-11 h-11 rounded-full bg-rose-600 group-hover:bg-rose-500 text-white flex items-center justify-center shadow-lg">
                        <i data-lucide="play" class="w-5 h-5 fill-current ml-0.5"></i>
                      </div>
                    </div>
                    ${item.channelName ? `<span class="absolute bottom-1.5 left-2 px-2 py-0.5 rounded bg-slate-950/85 text-[10px] font-mono text-rose-300 border border-slate-800">${item.channelName}</span>` : ''}
                  </div>
                ` : ''}
                ${item.quizScore ? `<p class="text-[10px] font-mono text-emerald-400">Retention Status: ${item.quizScore}</p>` : ''}"""

    if "openVideoTheater('${item.id}')" not in html and old_kv_card_title in html:
        html = html.replace(old_kv_card_title, new_kv_card_title, 1)

    old_kv_card_footer = """              <div class="flex justify-between items-center gap-2 pt-2 border-t border-slate-800/60">
                <button type="button" onclick="openRecallQuiz('${item.id}')" class="px-2.5 py-1 bg-emerald-600 hover:bg-emerald-500 text-slate-950 rounded-lg text-[11px] font-bold flex items-center gap-1">
                  <i data-lucide="help-circle" class="w-3 h-3"></i> Quiz (3Q)
                </button>"""

    new_kv_card_footer = """              <div class="flex flex-wrap justify-between items-center gap-1.5 pt-2 border-t border-slate-800/60">
                <div class="flex items-center gap-1.5">
                  ${item.videoId ? `<button type="button" onclick="openVideoTheater('${item.id}')" class="px-2.5 py-1 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-[11px] font-bold flex items-center gap-1"><i data-lucide="play" class="w-3 h-3"></i> Watch</button>` : ''}
                  <button type="button" onclick="openRecallQuiz('${item.id}')" class="px-2.5 py-1 bg-emerald-600 hover:bg-emerald-500 text-slate-950 rounded-lg text-[11px] font-bold flex items-center gap-1">
                    <i data-lucide="help-circle" class="w-3 h-3"></i> Quiz (3Q)
                  </button>
                </div>"""

    if "onclick=\"openVideoTheater('${item.id}')\" class=\"px-2.5 py-1 bg-rose-600" not in html and old_kv_card_footer in html:
        html = html.replace(old_kv_card_footer, new_kv_card_footer, 1)

    # Also render YouTube thumbnail/watch button on Omega cards if videoId is attached
    old_omega_card_title = """                <h4 class="font-bold text-white text-sm">${item.title}</h4>
                <div class="p-2.5 bg-slate-950 rounded-xl border border-slate-800/90 space-y-1 text-[11px] text-slate-300">
                  <span class="text-[10px] font-bold uppercase text-amber-400 block">Distilled Omega Micro-Session:</span>"""

    new_omega_card_title = """                <h4 class="font-bold text-white text-sm">${item.title}</h4>
                ${item.videoId ? `
                  <div onclick="openVideoTheater('${item.id}')" class="relative group cursor-pointer rounded-xl overflow-hidden border border-rose-800/50 bg-black aspect-video">
                    <img src="https://i.ytimg.com/vi/${item.videoId}/hqdefault.jpg" alt="${item.title}" class="w-full h-full object-cover opacity-85 group-hover:opacity-100 transition">
                    <div class="absolute inset-0 bg-slate-950/30 flex items-center justify-center">
                      <div class="w-10 h-10 rounded-full bg-rose-600 text-white flex items-center justify-center shadow-lg">
                        <i data-lucide="play" class="w-4 h-4 fill-current ml-0.5"></i>
                      </div>
                    </div>
                  </div>
                ` : ''}
                <div class="p-2.5 bg-slate-950 rounded-xl border border-slate-800/90 space-y-1 text-[11px] text-slate-300">
                  <span class="text-[10px] font-bold uppercase text-amber-400 block">Distilled Omega Micro-Session:</span>"""

    if "Distilled Omega Micro-Session:" in html and "https://i.ytimg.com/vi/${item.videoId}/hqdefault.jpg" not in html.split("Distilled Omega Micro-Session:")[0][-600:]:
        html = html.replace(old_omega_card_title, new_omega_card_title, 1)

    # Toggle Top Micro-Learning Watch button in renderAllUI
    old_top_micro_render = """        microTitleEl.innerText = activeStudy.title;
        microDomEl.innerText = activeStudy.quizScore ? `${activeStudy.type} (${activeStudy.quizScore})` : activeStudy.type;
        microStepsEl.innerHTML = steps.map(s => `<p>${s}</p>`).join('');"""

    new_top_micro_render = """        microTitleEl.innerText = activeStudy.title;
        microDomEl.innerText = activeStudy.quizScore ? `${activeStudy.type} (${activeStudy.quizScore})` : activeStudy.type;
        microStepsEl.innerHTML = steps.map(s => `<p>${s}</p>`).join('');
        const watchBtn = document.getElementById('active-micro-watch-btn');
        if (watchBtn) {
          watchBtn.classList.toggle('hidden', !activeStudy.videoId);
          watchBtn.classList.toggle('flex', !!activeStudy.videoId);
        }"""

    if "getElementById('active-micro-watch-btn')" not in html and old_top_micro_render in html:
        html = html.replace(old_top_micro_render, new_top_micro_render, 1)

    # 6. Inject YouTube Video Extraction, oEmbed Metadata Fetch, and Theater Player JavaScript
    youtube_js = """    // YOUTUBE VISUAL LEARNING & VIDEO REFERENCE ENGINE
    window.activeTheaterItemId = null;

    window.extractYouTubeVideoId = function(rawUrl) {
      if (!rawUrl) return null;
      const trimmed = rawUrl.trim();
      if (/^[a-zA-Z0-9_-]{11}$/.test(trimmed)) return trimmed;
      const patterns = [
        /(?:youtube\\.com\\/watch\\?(?:.*&)?v=)([a-zA-Z0-9_-]{11})/,
        /(?:youtu\\.be\\/)([a-zA-Z0-9_-]{11})/,
        /(?:youtube\\.com\\/embed\\/)([a-zA-Z0-9_-]{11})/,
        /(?:youtube\\.com\\/shorts\\/)([a-zA-Z0-9_-]{11})/,
        /(?:youtube\\.com\\/live\\/)([a-zA-Z0-9_-]{11})/
      ];
      for (const re of patterns) {
        const m = trimmed.match(re);
        if (m && m[1]) return m[1];
      }
      return null;
    };

    window.openYouTubeModal = function(targetVault) {
      document.getElementById('yt-target-vault').value = targetVault || 'knowledge';
      if (targetVault === 'omega') {
        document.getElementById('yt-domain-input').value = 'Omega';
      }
      document.getElementById('yt-fetch-status').classList.add('hidden');
      document.getElementById('yt-preview-card').classList.add('hidden');
      document.getElementById('youtube-ingest-modal').classList.remove('hidden');
      if (window.lucide) lucide.createIcons();
    };

    window.closeYouTubeModal = function() {
      document.getElementById('youtube-ingest-modal').classList.add('hidden');
    };

    window.previewYouTubeMetadata = async function(forceNotify) {
      const urlVal = document.getElementById('yt-url-input').value.trim();
      const videoId = window.extractYouTubeVideoId(urlVal);
      const statusEl = document.getElementById('yt-fetch-status');
      const cardEl = document.getElementById('yt-preview-card');

      if (!videoId) {
        if (forceNotify && statusEl) {
          statusEl.classList.remove('hidden');
          statusEl.innerText = 'Paste a valid YouTube link (e.g., https://www.youtube.com/watch?v=... or https://youtu.be/...).';
        }
        return;
      }

      document.getElementById('yt-preview-thumb').src = `https://i.ytimg.com/vi/${videoId}/hqdefault.jpg`;
      document.getElementById('yt-preview-id-tag').innerText = `Video ID: ${videoId} • Ready for Theater Embed`;
      cardEl.classList.remove('hidden');

      try {
        const oembedUrl = `https://www.youtube.com/oembed?url=${encodeURIComponent('https://www.youtube.com/watch?v=' + videoId)}&format=json`;
        const res = await fetch(oembedUrl);
        if (res.ok) {
          const meta = await res.json();
          if (meta.title) {
            document.getElementById('yt-preview-title').innerText = meta.title;
            const titleInput = document.getElementById('yt-title-input');
            if (!titleInput.value.trim()) titleInput.value = meta.title;
          }
          if (meta.author_name) {
            document.getElementById('yt-preview-channel').innerText = meta.author_name;
            const chInput = document.getElementById('yt-channel-input');
            if (!chInput.value.trim()) chInput.value = meta.author_name;
          }
          if (statusEl && forceNotify) {
            statusEl.classList.remove('hidden');
            statusEl.innerText = `Verified YouTube video "${meta.title}" by ${meta.author_name}!`;
          }
        }
      } catch (e) {}
    };

    window.handleSaveYouTubeVideo = async function(e) {
      if (e) e.preventDefault();
      const rawUrl = document.getElementById('yt-url-input').value.trim();
      const videoId = window.extractYouTubeVideoId(rawUrl);
      if (!videoId) {
        alert('Please enter a valid YouTube URL.');
        return;
      }

      const title = document.getElementById('yt-title-input').value.trim();
      const domain = document.getElementById('yt-domain-input').value;
      const channelName = document.getElementById('yt-channel-input').value.trim() || 'YouTube Reference';
      const timestampAnchor = document.getElementById('yt-timestamp-input').value.trim();
      const notes = document.getElementById('yt-notes-input').value.trim();
      const targetVault = document.getElementById('yt-target-vault').value;

      const combinedNotes = timestampAnchor ? `Key Timestamps: ${timestampAnchor}. ${notes}` : notes;
      const distilled = distillTextToMicroSession(title, combinedNotes);
      const videoUrl = `https://www.youtube.com/watch?v=${videoId}`;

      const record = {
        id: (targetVault === 'omega' ? 'om_yt_' : 'kv_yt_') + Date.now(),
        title,
        domain,
        source: targetVault === 'omega' ? 'Video Lecture (YouTube)' : domain,
        duration: 'YouTube Visual Sprint',
        type: `${domain} • YouTube Video`,
        videoId,
        videoUrl,
        channelName,
        timestampAnchor,
        takeaway: distilled.takeaway,
        content: combinedNotes,
        microSteps: distilled.microSteps,
        quiz: distilled.quiz,
        masteryLevel: 0,
        nextReviewDate: getTodayIsoDate(),
        quizScore: null,
        date: getTodayIsoDate()
      };

      if (targetVault === 'omega') {
        window.userAppState.omegaNotebooks = window.userAppState.omegaNotebooks || [];
        window.userAppState.omegaNotebooks.unshift(record);
      } else {
        window.userAppState.knowledgeVault = window.userAppState.knowledgeVault || [];
        window.userAppState.knowledgeVault.unshift(record);
        window.activePolymathDomain = 'All';
      }

      document.getElementById('yt-url-input').value = '';
      document.getElementById('yt-title-input').value = '';
      document.getElementById('yt-channel-input').value = '';
      document.getElementById('yt-timestamp-input').value = '';
      document.getElementById('yt-notes-input').value = '';

      renderAllUI();
      await pushCloudUserData();
      closeYouTubeModal();
      window.openVideoTheater(record.id);
    };

    window.openActiveVideoTheater = function() {
      const vault = window.userAppState.knowledgeVault || [];
      const firstVid = vault.find(v => !!v.videoId);
      if (firstVid) window.openVideoTheater(firstVid.id);
    };

    window.openVideoTheater = function(itemId) {
      const vault = window.userAppState.knowledgeVault || [];
      const omega = window.userAppState.omegaNotebooks || [];
      const item = vault.find(v => v.id === itemId) || omega.find(o => o.id === itemId);
      if (!item || !item.videoId) return;

      window.activeTheaterItemId = item.id;
      document.getElementById('theater-domain-badge').innerText = `${item.domain || item.source || 'Visual Learning'} • YouTube Theater`;
      document.getElementById('theater-video-title').innerText = item.title;
      document.getElementById('theater-external-link').href = item.videoUrl || `https://www.youtube.com/watch?v=${item.videoId}`;
      document.getElementById('theater-channel-meta').innerText = `${item.channelName || 'YouTube'}${item.timestampAnchor ? ' • Timestamps: ' + item.timestampAnchor : ''}`;

      const steps = item.microSteps || distillTextToMicroSession(item.title, item.content).microSteps;
      document.getElementById('theater-micro-steps').innerHTML = steps.map(s => `<p>${s}</p>`).join('');
      document.getElementById('theater-notes-editor').value = item.content || '';

      document.getElementById('theater-youtube-iframe').src = `https://www.youtube-nocookie.com/embed/${item.videoId}?rel=0&modestbranding=1`;
      document.getElementById('video-theater-modal').classList.remove('hidden');
      if (window.lucide) lucide.createIcons();
    };

    window.closeVideoTheaterModal = function() {
      document.getElementById('theater-youtube-iframe').src = '';
      document.getElementById('video-theater-modal').classList.add('hidden');
      window.activeTheaterItemId = null;
    };

    window.saveTheaterNotes = async function() {
      if (!window.activeTheaterItemId) return;
      const updatedNotes = document.getElementById('theater-notes-editor').value.trim();
      const applyUpdate = (item) => {
        if (item.id === window.activeTheaterItemId) {
          item.content = updatedNotes;
          const distilled = distillTextToMicroSession(item.title, updatedNotes);
          item.takeaway = distilled.takeaway;
          item.microSteps = distilled.microSteps;
          item.quiz = distilled.quiz;
        }
        return item;
      };
      window.userAppState.knowledgeVault = (window.userAppState.knowledgeVault || []).map(applyUpdate);
      window.userAppState.omegaNotebooks = (window.userAppState.omegaNotebooks || []).map(applyUpdate);
      renderAllUI();
      await pushCloudUserData();
      alert('Visual study notes & 3Q recall questions updated and encrypted!');
    };

    window.launchQuizFromTheater = function() {
      const id = window.activeTheaterItemId;
      window.closeVideoTheaterModal();
      if (id) window.openRecallQuiz(id);
    };"""

    if "function openVideoTheater(" not in html:
        html = html.replace(
            "    // Interactive 3Q Active-Recall Quiz Handlers",
            youtube_js + "\n\n    // Interactive 3Q Active-Recall Quiz Handlers",
            1,
        )

    # Also upgrade promoteOmegaToDailySprint to carry videoId/videoUrl/channelName forward
    old_promote_obj = """        type: `Omega: ${item.source}`,
        takeaway: item.takeaway,"""
    new_promote_obj = """        type: `Omega: ${item.source}`,
        videoId: item.videoId || null,
        videoUrl: item.videoUrl || null,
        channelName: item.channelName || null,
        takeaway: item.takeaway,"""
    if "videoId: item.videoId" not in html and old_promote_obj in html:
        html = html.replace(old_promote_obj, new_promote_obj, 1)

    with open(INDEX_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)

    onclicks = set(re.findall(r'onclick="([a-zA-Z0-9_]+)\(', html))
    missing = [fn for fn in sorted(onclicks) if f"window.{fn}" not in html and f"function {fn}" not in html]
    assert not missing, f"Missing JS handlers: {missing}"
    print(f"Successfully patched {INDEX_PATH} with YouTube Visual Learning & Theater Player! ({len(onclicks)} handlers verified)")


if __name__ == "__main__":
    main()

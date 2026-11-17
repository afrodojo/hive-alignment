import os
import re

INDEX_PATH = os.path.join("docs", "index.html")


def main():
    if not os.path.exists(INDEX_PATH):
        raise FileNotFoundError(f"Could not find {INDEX_PATH}. Run this script from the repository root.")

    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Add "+ Book / Paper / Scholar" button in Knowledge & Micro-Learning toolbar
    target_cms_btn = """            <button type="button" onclick="openCustomMicroSessionModal()" class="px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold rounded-xl text-xs transition flex items-center gap-1.5 shadow-md">
              <i data-lucide="plus-circle" class="w-3.5 h-3.5"></i> + Custom Micro-Session
            </button>"""

    replacement_cms_btn = """            <button type="button" onclick="openLibraryResourceModal('Doctoral Book / Textbook')" class="px-4 py-2 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded-xl text-xs transition flex items-center gap-1.5 shadow-md">
              <i data-lucide="book-open" class="w-3.5 h-3.5"></i> + Book / Paper / Scholar
            </button>
            <button type="button" onclick="openCustomMicroSessionModal()" class="px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold rounded-xl text-xs transition flex items-center gap-1.5 shadow-md">
              <i data-lucide="plus-circle" class="w-3.5 h-3.5"></i> + Custom Micro-Session
            </button>"""

    if "openLibraryResourceModal(" not in html and target_cms_btn in html:
        html = html.replace(target_cms_btn, replacement_cms_btn, 1)

    # 2. Enhance Faith & Salat Path tab header with Quran Surah Fetcher, Islamic Scholars Book button & Canon Loader
    target_faith_btn = """            <button type="button" onclick="loadAllIslamicModulesToVault()" class="px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold rounded-xl text-xs transition flex items-center gap-1.5 shadow-md">
              <i data-lucide="book-open-check" class="w-3.5 h-3.5"></i> Load All 5 Faith Paths to Vault
            </button>"""

    replacement_faith_btn = """            <button type="button" onclick="openLibraryResourceModal('Quran (Surah / Tafsir / Hifz)')" class="px-3.5 py-2 bg-sky-600 hover:bg-sky-500 text-slate-950 font-bold rounded-xl text-xs transition flex items-center gap-1.5 shadow-md">
              <i data-lucide="book" class="w-3.5 h-3.5"></i> + Quran Surah / Tafsir
            </button>
            <button type="button" onclick="openLibraryResourceModal('Book on Islamic Scholars')" class="px-3.5 py-2 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded-xl text-xs transition flex items-center gap-1.5 shadow-md">
              <i data-lucide="library" class="w-3.5 h-3.5"></i> + Islamic Scholars Book
            </button>
            <button type="button" onclick="loadIslamicScholarsCanonPack()" class="px-3.5 py-2 bg-purple-950 hover:bg-purple-900 border border-purple-700/70 text-purple-200 font-bold rounded-xl text-xs transition flex items-center gap-1.5">
              <i data-lucide="scroll-text" class="w-3.5 h-3.5 text-amber-400"></i> Load Scholars Canon
            </button>
            <button type="button" onclick="loadAllIslamicModulesToVault()" class="px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold rounded-xl text-xs transition flex items-center gap-1.5 shadow-md">
              <i data-lucide="book-open-check" class="w-3.5 h-3.5"></i> Load All 5 Faith Paths
            </button>"""

    if "loadIslamicScholarsCanonPack()" not in html and target_faith_btn in html:
        html = html.replace(target_faith_btn, replacement_faith_btn, 1)

    # 3. Also add Audio & Video buttons directly on the 5 Islamic Faith Curriculum Cards
    target_islam_card_btns = """            <div class="flex flex-wrap justify-between items-center gap-2 pt-2 border-t border-slate-800/60">
              <button type="button" onclick="launchIslamicModuleQuiz('${mod.id}')" class="px-2.5 py-1.5 bg-emerald-500 hover:bg-emerald-400 text-slate-950 rounded-lg text-[11px] font-bold flex items-center gap-1">
                <i data-lucide="help-circle" class="w-3 h-3"></i> Quiz (3Q)
              </button>
              <button type="button" onclick="activateIslamicModuleSprint('${mod.id}')" class="px-2.5 py-1.5 bg-sky-950 hover:bg-sky-900 border border-sky-800 text-sky-300 rounded-lg text-[11px] font-semibold">
                Set Active Sprint
              </button>
            </div>"""

    replacement_islam_card_btns = """            <div class="flex flex-wrap justify-between items-center gap-1.5 pt-2 border-t border-slate-800/60">
              <div class="flex items-center gap-1.5">
                <button type="button" onclick="launchIslamicModuleQuiz('${mod.id}')" class="px-2.5 py-1 bg-emerald-500 hover:bg-emerald-400 text-slate-950 rounded-lg text-[11px] font-bold flex items-center gap-1">
                  <i data-lucide="help-circle" class="w-3 h-3"></i> Quiz
                </button>
                <button type="button" onclick="launchIslamicModuleAv('${mod.id}', 'audio')" class="px-2 py-1 bg-indigo-950 hover:bg-indigo-900 text-indigo-300 border border-indigo-800 rounded-lg text-[11px] font-bold flex items-center gap-1">
                  <i data-lucide="headphones" class="w-3 h-3"></i> Audio
                </button>
                <button type="button" onclick="launchIslamicModuleAv('${mod.id}', 'video')" class="px-2 py-1 bg-purple-950 hover:bg-purple-900 text-purple-300 border border-purple-800 rounded-lg text-[11px] font-bold flex items-center gap-1">
                  <i data-lucide="monitor-play" class="w-3 h-3"></i> Video
                </button>
              </div>
              <button type="button" onclick="activateIslamicModuleSprint('${mod.id}')" class="px-2.5 py-1 bg-sky-950 hover:bg-sky-900 border border-sky-800 text-sky-300 rounded-lg text-[11px] font-semibold">
                Sprint
              </button>
            </div>"""

    if "launchIslamicModuleAv(" not in html and target_islam_card_btns in html:
        html = html.replace(target_islam_card_btns, replacement_islam_card_btns, 1)

    # 4. Inject Doctoral Books, Papers, Quran & Islamic Scholars Library Modal before <!-- MODALS -->
    library_modal_html = """  <!-- DOCTORAL BOOKS, ACADEMIC PAPERS, QURAN & ISLAMIC SCHOLARS LIBRARY MODAL -->
  <div id="library-resource-modal" class="fixed inset-0 bg-slate-950/95 backdrop-blur-md z-[1190] hidden flex items-center justify-center p-4 overflow-y-auto">
    <div class="bg-slate-900 border border-amber-700/60 rounded-2xl max-w-2xl w-full p-6 space-y-4 shadow-2xl relative my-8">
      <div class="flex justify-between items-start border-b border-slate-800 pb-3">
        <div>
          <span class="text-[10px] font-bold uppercase tracking-wider text-amber-400 flex items-center gap-1.5">
            <i data-lucide="book-open" class="w-3.5 h-3.5"></i> Doctoral &amp; Sacred Knowledge Library
          </span>
          <h3 class="text-base font-bold text-white mt-0.5">Add Book, Academic Paper, Quran Passage, or Book on Islamic Scholars</h3>
        </div>
        <button type="button" onclick="closeLibraryResourceModal()" class="text-slate-400 hover:text-white text-xl leading-none">&times;</button>
      </div>

      <!-- Quick Starter Packs & Live Quran Fetcher Bar -->
      <div class="p-3.5 bg-slate-950 rounded-xl border border-slate-800 space-y-3 text-xs">
        <div class="flex flex-wrap items-center justify-between gap-2">
          <span class="font-bold text-emerald-400 uppercase text-[10px]">One-Click Curated Canon Packs:</span>
          <div class="flex flex-wrap gap-2">
            <button type="button" onclick="loadDoctoralCanonPack()" class="px-3 py-1.5 bg-indigo-950 hover:bg-indigo-900 border border-indigo-700 text-indigo-200 font-bold rounded-lg text-[11px] transition">
              + Doctoral Books &amp; Methodology Pack
            </button>
            <button type="button" onclick="loadIslamicScholarsCanonPack()" class="px-3 py-1.5 bg-amber-950 hover:bg-amber-900 border border-amber-700 text-amber-200 font-bold rounded-lg text-[11px] transition">
              + Islamic Scholars Canon Pack
            </button>
          </div>
        </div>

        <!-- Live Quran Surah & Translation Auto-Pull -->
        <div class="pt-2 border-t border-slate-800/80 space-y-1.5">
          <label class="text-[10px] font-bold uppercase text-sky-400 block">Pull Any Quran Surah (Arabic + Sahih International English):</label>
          <div class="flex flex-col sm:flex-row gap-2">
            <select id="lib-quran-surah-select" class="flex-grow bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-slate-200">
              <option value="1">1. Al-Fatihah (The Opener — 7 Ayahs)</option>
              <option value="2">2. Al-Baqarah (Selected / Ayat al-Kursi 2:255)</option>
              <option value="18">18. Al-Kahf (The Cave — Friday Anchor)</option>
              <option value="36">36. Ya-Sin (Heart of the Quran)</option>
              <option value="49">49. Al-Hujurat (Social Ethics &amp; Brotherhood)</option>
              <option value="55">55. Ar-Rahman (The Most Merciful)</option>
              <option value="67" selected>67. Al-Mulk (Nightly Isha Protection — 30 Ayahs)</option>
              <option value="87">87. Al-A'la (The Most High)</option>
              <option value="94">94. Ash-Sharh (Relief After Hardship)</option>
              <option value="103">103. Al-Asr (Time &amp; Salvation)</option>
              <option value="112">112. Al-Ikhlas (Pure Monotheism)</option>
            </select>
            <input type="text" id="lib-quran-ayah-range" placeholder="Ayahs (e.g. 1-10 or 255, optional)" class="sm:w-48 bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 font-mono">
            <button type="button" id="lib-quran-fetch-btn" onclick="fetchQuranSurahIntoForm()" class="px-4 py-2 bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold rounded-xl flex-shrink-0">
              Pull Quran Text
            </button>
          </div>
          <p id="lib-status-msg" class="text-[11px] text-emerald-300 hidden"></p>
        </div>
      </div>

      <form onsubmit="handleSaveLibraryResource(event)" class="space-y-3 text-xs">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label class="text-slate-400 block mb-1 font-medium">Resource Format</label>
            <select id="lib-format-select" class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200">
              <option value="Doctoral Book / Textbook">Doctoral Book / Textbook</option>
              <option value="Academic Paper (Peer-Reviewed)">Academic Paper (Peer-Reviewed)</option>
              <option value="Quran (Surah / Tafsir / Hifz)">Quran (Surah / Tafsir / Hifz)</option>
              <option value="Book on Islamic Scholars">Book on Islamic Scholars</option>
              <option value="Classical Islamic Text (Turath)">Classical Islamic Text (Turath)</option>
            </select>
          </div>
          <div>
            <label class="text-slate-400 block mb-1 font-medium">Life Pillar</label>
            <select id="lib-domain-select" class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200">
              <option value="Doctoral Studies">Doctoral Studies (Jan 2027)</option>
              <option value="Faith">Faith &amp; Islamic Scholarship</option>
              <option value="Health">Health &amp; Vitality</option>
              <option value="Family">Family &amp; Leadership</option>
              <option value="Omega">Omega &amp; Heritage</option>
              <option value="Polymath">Polymath Synthesis</option>
            </select>
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label class="text-slate-400 block mb-1 font-medium">Book / Paper / Surah Title</label>
            <input type="text" id="lib-title-input" required placeholder="e.g., Ihya Ulum al-Din, Research Design (Creswell), Surah Al-Mulk..." class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200">
          </div>
          <div>
            <label class="text-slate-400 block mb-1 font-medium">Author / Islamic Scholar / Citation</label>
            <input type="text" id="lib-author-input" placeholder="e.g., Imam Al-Ghazali, Creswell (2023), Sahih International..." class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200">
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label class="text-slate-400 block mb-1 font-medium">Chapter / Ayah Range / DOI (Optional)</label>
            <input type="text" id="lib-section-input" placeholder="e.g., Ch. 4 Mixed Methods, Ayahs 1-30, Book III..." class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2 text-slate-200 font-mono">
          </div>
          <div>
            <label class="text-slate-400 block mb-1 font-medium">Attach Book/Paper File (PDF, DOCX, TXT - Optional)</label>
            <input type="file" id="lib-file-attach" accept=".pdf,.docx,.txt,.md,application/pdf" onchange="handleLibraryFileAttach(event)" class="w-full bg-slate-950 border border-slate-800 rounded-xl p-1.5 text-slate-300 text-[11px]">
          </div>
        </div>

        <div>
          <label class="text-slate-400 block mb-1 font-medium">Full Text, Chapter Excerpts, Tafsir, or Study Notes (Used for Audiobook, Video &amp; 3Q Quiz)</label>
          <textarea id="lib-content-input" rows="5" required placeholder="Paste book chapter notes, paper abstract & findings, Quran translation + Tafsir, or scholar biography here..." class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-slate-200 font-mono"></textarea>
        </div>

        <div class="flex justify-end gap-2 pt-2 border-t border-slate-800">
          <button type="button" onclick="closeLibraryResourceModal()" class="px-4 py-2 bg-slate-800 text-slate-300 rounded-xl font-semibold">Cancel</button>
          <button type="submit" class="px-4 py-2 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded-xl flex items-center gap-1.5">
            <i data-lucide="save" class="w-3.5 h-3.5"></i> Save to Vault (Audio, Video &amp; 3Q Ready)
          </button>
        </div>
      </form>
    </div>
  </div>"""

    if 'id="library-resource-modal"' not in html:
        html = html.replace("  <!-- MODALS -->", library_modal_html + "\n\n  <!-- MODALS -->", 1)

    # 5. Add Library Filter Pills ('Books', 'Papers', 'Quran', 'Islamic Scholars') to renderPolymathVaultUI
    old_domains_arr = "const domains = ['All', 'Due Today', 'Videos', 'Doctoral Studies', 'Faith', 'Health', 'Family', 'Omega', 'Polymath'];"
    old_domains_arr_alt = "const domains = ['All', 'Due Today', 'Doctoral Studies', 'Faith', 'Health', 'Family', 'Omega', 'Polymath'];"
    new_domains_arr = "const domains = ['All', 'Due Today', 'Books', 'Papers', 'Quran', 'Islamic Scholars', 'Videos', 'Doctoral Studies', 'Faith', 'Health', 'Family', 'Omega', 'Polymath'];"

    if old_domains_arr in html:
        html = html.replace(old_domains_arr, new_domains_arr, 1)
    elif old_domains_arr_alt in html:
        html = html.replace(old_domains_arr_alt, new_domains_arr, 1)

    old_count_block = """          if (dom === 'All') count = vault.length;
          else if (dom === 'Due Today') count = dueCount;
          else if (dom === 'Videos') count = vault.filter(i => !!i.videoId).length;
          else count = vault.filter(i => getDomain(i) === dom).length;"""

    old_count_block_alt = """          if (dom === 'All') count = vault.length;
          else if (dom === 'Due Today') count = dueCount;
          else count = vault.filter(i => getDomain(i) === dom).length;"""

    new_count_block = """          const isBook = (i) => (i.resourceFormat || i.type || '').toLowerCase().includes('book');
          const isPaper = (i) => (i.resourceFormat || i.type || '').toLowerCase().includes('paper');
          const isQuran = (i) => (i.resourceFormat || i.type || '').toLowerCase().includes('quran');
          const isScholar = (i) => (i.resourceFormat || i.type || '').toLowerCase().includes('scholar') || (i.resourceFormat || i.type || '').toLowerCase().includes('turath');
          if (dom === 'All') count = vault.length;
          else if (dom === 'Due Today') count = dueCount;
          else if (dom === 'Books') count = vault.filter(isBook).length;
          else if (dom === 'Papers') count = vault.filter(isPaper).length;
          else if (dom === 'Quran') count = vault.filter(isQuran).length;
          else if (dom === 'Islamic Scholars') count = vault.filter(isScholar).length;
          else if (dom === 'Videos') count = vault.filter(i => !!i.videoId).length;
          else count = vault.filter(i => getDomain(i) === dom).length;"""

    if "const isScholar =" not in html:
        if old_count_block in html:
            html = html.replace(old_count_block, new_count_block, 1)
        elif old_count_block_alt in html:
            html = html.replace(old_count_block_alt, new_count_block, 1)

    old_filt_block = """      if (window.activePolymathDomain === 'Due Today') filtered = vault.filter(isDue);
      else if (window.activePolymathDomain === 'Videos') filtered = vault.filter(i => !!i.videoId);
      else if (window.activePolymathDomain !== 'All') filtered = vault.filter(i => getDomain(i) === window.activePolymathDomain);"""

    old_filt_block_alt = """      if (window.activePolymathDomain === 'Due Today') filtered = vault.filter(isDue);
      else if (window.activePolymathDomain !== 'All') filtered = vault.filter(i => getDomain(i) === window.activePolymathDomain);"""

    new_filt_block = """      if (window.activePolymathDomain === 'Due Today') filtered = vault.filter(isDue);
      else if (window.activePolymathDomain === 'Books') filtered = vault.filter(i => (i.resourceFormat || i.type || '').toLowerCase().includes('book'));
      else if (window.activePolymathDomain === 'Papers') filtered = vault.filter(i => (i.resourceFormat || i.type || '').toLowerCase().includes('paper'));
      else if (window.activePolymathDomain === 'Quran') filtered = vault.filter(i => (i.resourceFormat || i.type || '').toLowerCase().includes('quran'));
      else if (window.activePolymathDomain === 'Islamic Scholars') filtered = vault.filter(i => { const t = (i.resourceFormat || i.type || '').toLowerCase(); return t.includes('scholar') || t.includes('turath'); });
      else if (window.activePolymathDomain === 'Videos') filtered = vault.filter(i => !!i.videoId);
      else if (window.activePolymathDomain !== 'All') filtered = vault.filter(i => getDomain(i) === window.activePolymathDomain);"""

    if "window.activePolymathDomain === 'Books'" not in html:
        if old_filt_block in html:
            html = html.replace(old_filt_block, new_filt_block, 1)
        elif old_filt_block_alt in html:
            html = html.replace(old_filt_block_alt, new_filt_block, 1)

    # Display Author / Scholar / Section subtitle on Vault Cards
    target_card_h4 = """                <h4 class="font-bold text-white text-sm">${item.title}</h4>"""
    replacement_card_h4 = """                <h4 class="font-bold text-white text-sm">${item.title}</h4>
                ${(item.author || item.sectionRef) ? `<p class="text-[11px] font-mono text-amber-300/90">${[item.author, item.sectionRef].filter(Boolean).join(' • ')}</p>` : ''}"""

    if "item.author || item.sectionRef" not in html and target_card_h4 in html:
        html = html.replace(target_card_h4, replacement_card_h4, 1)

    # 6. Inject JavaScript Handlers for Library Modal, AlQuran Cloud API Pull, and Starter Canon Packs
    library_js = """    // DOCTORAL BOOKS, PAPERS, QURAN & ISLAMIC SCHOLARS LIBRARY ENGINE
    window.openLibraryResourceModal = function(presetFormat) {
      const fmtSel = document.getElementById('lib-format-select');
      const domSel = document.getElementById('lib-domain-select');
      const msgEl = document.getElementById('lib-status-msg');
      if (msgEl) msgEl.classList.add('hidden');
      if (fmtSel && presetFormat) {
        fmtSel.value = presetFormat;
        if (presetFormat.includes('Quran') || presetFormat.includes('Islamic')) {
          if (domSel) domSel.value = 'Faith';
        } else if (presetFormat.includes('Doctoral') || presetFormat.includes('Paper')) {
          if (domSel) domSel.value = 'Doctoral Studies';
        }
      }
      document.getElementById('library-resource-modal').classList.remove('hidden');
      if (window.lucide) lucide.createIcons();
    };

    window.closeLibraryResourceModal = function() {
      document.getElementById('library-resource-modal').classList.add('hidden');
    };

    window.launchIslamicModuleAv = async function(modId, mode) {
      const item = ensureIslamicModuleInVault(modId);
      if (!item) return;
      renderAllUI();
      await pushCloudUserData();
      if (typeof window.launchAvPlayer === 'function') {
        window.launchAvPlayer(item.id, mode);
      } else {
        alert('Audio/Video synth player not loaded yet. Run patch_av_engine.py or open from Knowledge Vault.');
      }
    };

    window.fetchQuranSurahIntoForm = async function() {
      const surahNum = document.getElementById('lib-quran-surah-select').value;
      const rangeStr = (document.getElementById('lib-quran-ayah-range').value || '').trim();
      const btn = document.getElementById('lib-quran-fetch-btn');
      const msgEl = document.getElementById('lib-status-msg');

      btn.disabled = true;
      btn.innerText = 'Pulling Surah...';
      if (msgEl) {
        msgEl.classList.remove('hidden');
        msgEl.innerText = 'Fetching Uthmani Arabic & Sahih International English translation...';
      }

      try {
        const res = await fetch(`https://api.alquran.cloud/v1/surah/${surahNum}/editions/quran-uthmani,en.sahih`);
        if (!res.ok) throw new Error(`AlQuran API returned HTTP ${res.status}`);
        const json = await res.json();
        const arData = json?.data?.[0];
        const enData = json?.data?.[1];
        if (!arData || !enData) throw new Error('Could not parse Surah payload.');

        let startAyah = 1;
        let endAyah = enData.ayahs.length;
        if (rangeStr) {
          if (rangeStr.includes('-')) {
            const parts = rangeStr.split('-').map(n => parseInt(n.trim(), 10));
            if (!isNaN(parts[0])) startAyah = Math.max(1, parts[0]);
            if (!isNaN(parts[1])) endAyah = Math.min(enData.ayahs.length, parts[1]);
          } else {
            const single = parseInt(rangeStr, 10);
            if (!isNaN(single)) {
              startAyah = Math.max(1, single);
              endAyah = Math.min(enData.ayahs.length, single);
            }
          }
        } else if (endAyah > 15) {
          endAyah = 15;
        }

        const compiledLines = [];
        for (let i = startAyah - 1; i < endAyah; i++) {
          const enAyah = enData.ayahs[i];
          const arAyah = arData.ayahs[i];
          if (enAyah) {
            compiledLines.push(`[${surahNum}:${enAyah.numberInSurah}] ${enAyah.text}`);
            if (arAyah) compiledLines.push(`Arabic: ${arAyah.text}`);
          }
        }

        document.getElementById('lib-format-select').value = 'Quran (Surah / Tafsir / Hifz)';
        document.getElementById('lib-domain-select').value = 'Faith';
        document.getElementById('lib-title-input').value = `Surah ${enData.englishName} (${enData.englishNameTranslation})`;
        document.getElementById('lib-author-input').value = 'Al-Quran Al-Kareem • Sahih International';
        document.getElementById('lib-section-input').value = `Surah ${surahNum}, Ayahs ${startAyah}–${endAyah}`;
        document.getElementById('lib-content-input').value = compiledLines.join('\n');

        if (msgEl) {
          msgEl.innerText = `Pulled Surah ${enData.englishName} (Ayahs ${startAyah}–${endAyah})! Add any personal Tafsir reflections below and click Save to Vault.`;
        }
      } catch (err) {
        if (msgEl) msgEl.innerText = `Quran fetch notice: ${err.message}. You can paste any Ayahs & Tafsir manually below.`;
      } finally {
        btn.disabled = false;
        btn.innerText = 'Pull Quran Text';
      }
    };

    window.handleLibraryFileAttach = async function(e) {
      const file = e.target.files[0];
      if (!file) return;
      const msgEl = document.getElementById('lib-status-msg');
      if (msgEl) {
        msgEl.classList.remove('hidden');
        msgEl.innerText = `Extracting text from "${file.name}" locally in browser...`;
      }

      const cleanName = file.name.replace(/\.[^/.]+$/, '').replace(/[_-]+/g, ' ').trim();
      const titleEl = document.getElementById('lib-title-input');
      if (titleEl && !titleEl.value.trim()) titleEl.value = cleanName;

      try {
        if (file.name.toLowerCase().endsWith('.pdf')) {
          const { text, pageCount } = await extractTextFromPdfBuffer(await file.arrayBuffer());
          document.getElementById('lib-content-input').value = text.slice(0, 9000);
          if (msgEl) msgEl.innerText = `Extracted ${pageCount} PDF page(s) into study notes! Ready for Audiobook, Visual Synth & 3Q Quiz.`;
        } else if (file.name.toLowerCase().endsWith('.docx')) {
          const txt = await extractTextFromDocxBuffer(await file.arrayBuffer());
          document.getElementById('lib-content-input').value = txt.slice(0, 9000);
          if (msgEl) msgEl.innerText = `Extracted Word document text! Ready for Audiobook, Visual Synth & 3Q Quiz.`;
        } else {
          const txt = await file.text();
          document.getElementById('lib-content-input').value = txt.slice(0, 9000);
          if (msgEl) msgEl.innerText = `Loaded "${file.name}" into study notes!`;
        }
      } catch (err) {
        if (msgEl) msgEl.innerText = `File read notice: ${err.message}`;
      }
    };

    window.handleSaveLibraryResource = async function(e) {
      if (e) e.preventDefault();
      const resourceFormat = document.getElementById('lib-format-select').value;
      const domain = document.getElementById('lib-domain-select').value;
      const title = document.getElementById('lib-title-input').value.trim();
      const author = document.getElementById('lib-author-input').value.trim();
      const sectionRef = document.getElementById('lib-section-input').value.trim();
      const content = document.getElementById('lib-content-input').value.trim();

      const distilled = distillTextToMicroSession(title, content);
      const today = getTodayIsoDate();

      window.userAppState.knowledgeVault = window.userAppState.knowledgeVault || [];
      window.userAppState.knowledgeVault.unshift({
        id: 'kv_lib_' + Date.now(),
        title,
        domain,
        resourceFormat,
        author,
        sectionRef,
        duration: resourceFormat.includes('Book') ? '30-Min Book Synthesis' : '20-Min Deep Sprint',
        type: `${domain} • ${resourceFormat}`,
        takeaway: distilled.takeaway,
        content,
        microSteps: distilled.microSteps,
        quiz: distilled.quiz,
        masteryLevel: 0,
        nextReviewDate: today,
        quizScore: null,
        date: today
      });

      document.getElementById('lib-title-input').value = '';
      document.getElementById('lib-author-input').value = '';
      document.getElementById('lib-section-input').value = '';
      document.getElementById('lib-content-input').value = '';

      window.activePolymathDomain = 'All';
      renderAllUI();
      await pushCloudUserData();
      closeLibraryResourceModal();
    };

    window.loadIslamicScholarsCanonPack = async function() {
      const today = getTodayIsoDate();
      const scholarsPack = [
        {
          id: 'kv_sch_ghazali_' + Date.now(),
          title: "Ihya' Ulum al-Din (Revival of the Religious Sciences)",
          domain: 'Faith',
          resourceFormat: 'Book on Islamic Scholars',
          author: 'Imam Abu Hamid Al-Ghazali (d. 1111 CE)',
          sectionRef: 'Quarter III: Disciplining the Soul & Guarding the Tongue',
          duration: '30-Min Book Synthesis',
          type: 'Faith • Book on Islamic Scholars',
          takeaway: 'True scholarly knowledge transforms the inward heart (Qalb) through Mujahadah (self-discipline), silence, and sincerity rather than outward debate.',
          content: 'Imam Al-Ghazali demonstrates in Ihya Ulum al-Din that knowledge without inward purification breeds pride. Disciplining the soul requires auditing intentions before speaking, guarding the tongue from backbiting and ostentation, and anchoring daily habits in remembrance of Allah.',
          microSteps: [
            '1. Core Thesis: Knowledge must purify the heart (Qalb) and refine character, not feed ego.',
            '2. Tactical Drill: Audit speech today against Al-Ghazali’s perils of the tongue (ostentation, argumentativeness, backbiting).',
            '3. Active Recall: Contrast outward knowledge with transformative inward certainty.'
          ],
          quiz: [
            { q: '1. According to Imam Al-Ghazali in Ihya Ulum al-Din, what is the true purpose of sacred knowledge?', a: 'Purifying the inward heart (Qalb) and transforming character into sincere devotion rather than seeking status or debate.' },
            { q: '2. Name two major perils of the tongue warned against in Quarter III of the Ihya.', a: 'Ostentation (Riya), backbiting (Gheebah), and contentious arguing for ego.' },
            { q: '3. Applied Synthesis: How will you apply Al-Ghazali’s self-accounting (Muhasabah) tonight?', a: 'Review today’s intentions before Isha and correct one reactive habit.' }
          ],
          masteryLevel: 0,
          nextReviewDate: today,
          quizScore: null,
          date: today
        },
        {
          id: 'kv_sch_khaldun_' + (Date.now() + 1),
          title: 'Al-Muqaddimah (Prolegomena to Universal History)',
          domain: 'Faith',
          resourceFormat: 'Book on Islamic Scholars',
          author: 'Ibn Khaldun (d. 1406 CE)',
          sectionRef: 'Book I: Social Cohesion (Asabiyyah) & Philosophy of Science',
          duration: '30-Min Book Synthesis',
          type: 'Faith • Book on Islamic Scholars',
          takeaway: 'Ibn Khaldun pioneered empirical sociology and historiography, showing how Asabiyyah (social solidarity), justice, and institutional discipline sustain civilizations.',
          content: 'In Al-Muqaddimah, Ibn Khaldun critiques unverified historical reporting and introduces Ilm al-Umran (science of human civilization). Civilizations rise through strong group solidarity (Asabiyyah), moral discipline, and equitable governance, and decline when luxury erodes solidarity and injustice destroys productivity.',
          microSteps: [
            '1. Core Thesis: Group solidarity (Asabiyyah) and justice form the backbone of resilient communities and institutions.',
            '2. Methodological Insight: Always verify primary causes and social conditions rather than accepting surface narratives.',
            '3. Active Recall: Connect Ibn Khaldun’s concept of Asabiyyah to brotherhood and leadership.'
          ],
          quiz: [
            { q: '1. What Arabic term did Ibn Khaldun coin for social cohesion and group solidarity?', a: 'Asabiyyah.' },
            { q: '2. According to Al-Muqaddimah, what factors trigger the decline of a civilization or institution?', a: 'Erosion of solidarity through luxury/complacency and injustice that undermines productive effort.' },
            { q: '3. Applied Synthesis: How does Ibn Khaldun’s critical verification method aid doctoral research?', a: 'It demands testing historical and empirical claims against underlying structural evidence.' }
          ],
          masteryLevel: 0,
          nextReviewDate: today,
          quizScore: null,
          date: today
        },
        {
          id: 'kv_sch_nawawi_' + (Date.now() + 2),
          title: 'Imam Al-Nawawi: Life, Ascetic Scholarship & Al-Arba’in',
          domain: 'Faith',
          resourceFormat: 'Book on Islamic Scholars',
          author: 'Imam Yahya ibn Sharaf Al-Nawawi (d. 1277 CE)',
          sectionRef: 'Hadith Canon & Principles of Legal/Spiritual Precision',
          duration: '20-Min Deep Sprint',
          type: 'Faith • Book on Islamic Scholars',
          takeaway: 'Imam Al-Nawawi exemplifies intense scholarly devotion—authoring foundational Hadith and Fiqh works in 45 years through disciplined time stewardship and sincerity.',
          content: 'Imam Al-Nawawi studied up to twelve lessons a day in Damascus while living with complete simplicity and courage in speaking truth to rulers. His Forty Hadith (Al-Arba’in) distills the comprehensive foundations of Islamic belief, ethics, and jurisprudence.',
          microSteps: [
            '1. Scholarly Model: Focused, distraction-free study paired with humble practice produces enduring works.',
            '2. Core Canon: Master Al-Arba’in al-Nawawiyyah and Riyad as-Salihin as daily ethical anchors.',
            '3. Active Recall: Apply Al-Nawawi’s time-stewardship discipline to your Fajr doctoral block.'
          ],
          quiz: [
            { q: '1. How many lessons per day did Imam Al-Nawawi famously study during his formative years in Damascus?', a: 'Up to twelve lessons per day across Hadith, Fiqh, and Arabic sciences.' },
            { q: '2. Which two Hadith compilations by Imam Al-Nawawi serve as universal primers on Prophetic ethics?', a: 'Al-Arba’in al-Nawawiyyah (Forty Hadith) and Riyad as-Salihin (Gardens of the Righteous).' },
            { q: '3. Applied Synthesis: What distraction can you eliminate this week to honor Al-Nawawi’s focus?', a: 'Protect your morning Fajr-to-Sunrise study window with zero phone interruptions.' }
          ],
          masteryLevel: 0,
          nextReviewDate: today,
          quizScore: null,
          date: today
        },
        {
          id: 'kv_sch_contemp_' + (Date.now() + 3),
          title: 'Islam and the Blackamerican & The Cultural Imperative',
          domain: 'Faith',
          resourceFormat: 'Book on Islamic Scholars',
          author: 'Dr. Sherman A. Jackson & Dr. Umar Faruq Abd-Allah',
          sectionRef: 'Contemporary Western & African-American Islamic Scholarship',
          duration: '30-Min Book Synthesis',
          type: 'Faith • Book on Islamic Scholars',
          takeaway: 'Authentic Islamic scholarship engages indigenous heritage with classical Sunni jurisprudence, cultivating a confident, rooted Muslim identity.',
          content: 'Dr. Sherman Jackson examines the historical trajectory of Islam among Black Americans and the distinction between immigrant Islam and indigenous Blackamerican Muslim identity. Dr. Umar Faruq Abd-Allah shows how classical Islamic law honors healthy local culture (Urf) like clear crystal reflecting light.',
          microSteps: [
            '1. Core Thesis: Classical Islam affirms healthy cultural identity (Urf) while upholding universal sacred law.',
            '2. Intellectual Bridge: Connect Black American historical resilience with classical Islamic scholarship.',
            '3. Active Recall: Articulate how rooted identity strengthens community uplift.'
          ],
          quiz: [
            { q: '1. What metaphor does Dr. Umar Faruq Abd-Allah use to describe how Islam relates to healthy local culture (Urf)?', a: 'Like clear crystal water taking on the color of the bedrock beneath it while remaining pure.' },
            { q: '2. What central theme does Dr. Sherman Jackson analyze in "Islam and the Blackamerican"?', a: 'The historical formation and intellectual agency of Blackamerican Muslims within the broader Muslim community.' },
            { q: '3. Applied Synthesis: How does this scholarship inform community leadership and uplift?', a: 'It unites sacred integrity with authentic cultural literacy and service.' }
          ],
          masteryLevel: 0,
          nextReviewDate: today,
          quizScore: null,
          date: today
        }
      ];

      window.userAppState.knowledgeVault = [...scholarsPack, ...(window.userAppState.knowledgeVault || [])];
      window.activePolymathDomain = 'Islamic Scholars';
      renderAllUI();
      await pushCloudUserData();
      switchTab('tab-knowledge');
      alert('Loaded 4 Islamic Scholars Books & Modules (Al-Ghazali, Ibn Khaldun, Al-Nawawi, Jackson & Abd-Allah) into your vault with Audiobook, Video & 3Q Quizzes!');
    };

    window.loadDoctoralCanonPack = async function() {
      const today = getTodayIsoDate();
      const docCanon = [
        {
          id: 'kv_doc_creswell_' + Date.now(),
          title: 'Research Design: Qualitative, Quantitative, and Mixed Methods Approaches',
          domain: 'Doctoral Studies',
          resourceFormat: 'Doctoral Book / Textbook',
          author: 'John W. Creswell & J. David Creswell',
          sectionRef: 'Part I: Philosophical Worldviews & Research Design Selection',
          duration: '30-Min Book Synthesis',
          type: 'Doctoral Studies • Doctoral Book / Textbook',
          takeaway: 'Every rigorous doctoral study aligns three components: philosophical worldview (postpositivist, constructivist, transformative, pragmatic), research design, and specific methods.',
          content: 'Creswell establishes that research design flows from philosophical assumptions: postpositivism tests deterministic hypotheses quantitatively; constructivism explores subjective meanings qualitatively; pragmatism integrates both via mixed methods around the research problem.',
          microSteps: [
            '1. Core Alignment: Worldview -> Design -> Data Collection & Analysis Methods.',
            '2. Doctoral Check: Explicitly name your philosophical worldview in Chapter 1 and Chapter 3.',
            '3. Active Recall: Match postpositivism, constructivism, and pragmatism to their primary designs.'
          ],
          quiz: [
            { q: '1. What three components must align in Creswell’s framework for research design?', a: 'Philosophical worldview, research design, and specific research methods.' },
            { q: '2. Which philosophical worldview underpins mixed-methods research by focusing on what works for the problem?', a: 'Pragmatism.' },
            { q: '3. Applied Synthesis: Which worldview best anchors your planned January 2027 doctoral inquiry?', a: 'Write a 2-sentence justification linking your worldview to your data strategy.' }
          ],
          masteryLevel: 0,
          nextReviewDate: today,
          quizScore: null,
          date: today
        },
        {
          id: 'kv_doc_kuhn_' + (Date.now() + 1),
          title: 'The Structure of Scientific Revolutions',
          domain: 'Doctoral Studies',
          resourceFormat: 'Doctoral Book / Textbook',
          author: 'Thomas S. Kuhn',
          sectionRef: 'Chapters II–IX: Normal Science, Anomalies & Paradigm Shifts',
          duration: '30-Min Book Synthesis',
          type: 'Doctoral Studies • Doctoral Book / Textbook',
          takeaway: 'Academic fields advance through periods of puzzle-solving "normal science" punctuated by anomalies that trigger revolutionary paradigm shifts.',
          content: 'Thomas Kuhn argues that scientific disciplines operate within shared paradigms until persistent anomalies accumulate that existing frameworks cannot explain, leading to crisis and a paradigm shift that redefines foundational questions and standards of evidence.',
          microSteps: [
            '1. Core Thesis: Normal science refines an existing paradigm; anomalies drive paradigm shifts.',
            '2. Literature Strategy: Look for persistent anomalies or contradictions in your field’s dominant paradigm.',
            '3. Active Recall: Define normal science, anomaly, and incommensurability.'
          ],
          quiz: [
            { q: '1. What does Thomas Kuhn call day-to-day puzzle-solving research conducted within an established framework?', a: 'Normal science.' },
            { q: '2. What triggers a scientific crisis and eventual paradigm shift?', a: 'Persistent anomalies that the prevailing paradigm cannot explain or resolve.' },
            { q: '3. Applied Synthesis: What anomaly or unresolved tension exists in your target doctoral field?', a: 'Note one theoretical contradiction in your Literature Matrix.' }
          ],
          masteryLevel: 0,
          nextReviewDate: today,
          quizScore: null,
          date: today
        },
        {
          id: 'kv_doc_prisma_' + (Date.now() + 2),
          title: 'Systematic Literature Review & Thematic Synthesis Protocol',
          domain: 'Doctoral Studies',
          resourceFormat: 'Academic Paper (Peer-Reviewed)',
          author: 'Doctoral Methodology Series',
          sectionRef: 'PRISMA Screening & Concept-Centric Matrix',
          duration: '20-Min Deep Sprint',
          type: 'Doctoral Studies • Academic Paper (Peer-Reviewed)',
          takeaway: 'A concept-centric literature review maps authors against key theoretical constructs rather than listing summaries paper-by-paper.',
          content: 'Following Webster & Watson and PRISMA guidelines, document search databases, inclusion/exclusion criteria, and code every paper into a concept matrix (Construct A, Construct B, Method, Sample, Key Finding, Gap).',
          microSteps: [
            '1. Core Rule: Build a concept-centric matrix (rows = papers, columns = constructs & methods).',
            '2. Reproducibility: Log search strings, databases, and inclusion/exclusion counts.',
            '3. Active Recall: Convert your concept matrix columns directly into literature review subheadings.'
          ],
          quiz: [
            { q: '1. Why is a concept-centric literature matrix superior to an author-centric summary?', a: 'It synthesizes findings across studies by theoretical construct and reveals empirical gaps directly.' },
            { q: '2. What elements are required for a reproducible systematic literature search?', a: 'Explicit databases, Boolean search strings, and documented inclusion/exclusion criteria.' },
            { q: '3. Applied Synthesis: Identify 3 core constructs that will form the columns of your Literature Matrix.', a: 'List your 3 target constructs in your Journal today.' }
          ],
          masteryLevel: 0,
          nextReviewDate: today,
          quizScore: null,
          date: today
        }
      ];

      window.userAppState.knowledgeVault = [...docCanon, ...(window.userAppState.knowledgeVault || [])];
      window.activePolymathDomain = 'Doctoral Studies';
      renderAllUI();
      await pushCloudUserData();
      closeLibraryResourceModal();
      switchTab('tab-knowledge');
      alert('Loaded 3 Doctoral Books & Seminal Methodology Papers (Creswell, Kuhn, Systematic Review Protocol) into your vault!');
    };"""

    if "function openLibraryResourceModal(" not in html:
        html = html.replace(
            "    // Interactive 3Q Active-Recall Quiz Handlers",
            library_js + "\n\n    // Interactive 3Q Active-Recall Quiz Handlers",
            1,
        )

    with open(INDEX_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)

    onclicks = set(re.findall(r'onclick="([a-zA-Z0-9_]+)\(', html))
    missing = [fn for fn in sorted(onclicks) if f"window.{fn}" not in html and f"function {fn}" not in html]
    assert not missing, f"Missing JS handlers: {missing}"
    print(f"Successfully patched {INDEX_PATH} with Doctoral Books, Papers, Quran & Islamic Scholars Library! ({len(onclicks)} handlers verified)")


if __name__ == "__main__":
    main()

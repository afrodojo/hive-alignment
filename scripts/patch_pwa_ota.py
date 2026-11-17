import os
import re

INDEX_PATH = os.path.join("docs", "index.html")


def main():
    if not os.path.exists(INDEX_PATH):
        raise FileNotFoundError(f"Could not find {INDEX_PATH}. Run this script from the repository root.")

    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Inject PWA Manifest & Mobile Meta Tags in <head>
    pwa_head_tags = """  <link rel="manifest" href="./manifest.json">
  <meta name="theme-color" content="#020617">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="apple-mobile-web-app-title" content="HiveAlign">"""

    if 'rel="manifest"' not in html:
        html = html.replace("</head>", pwa_head_tags + "\n</head>", 1)

    # 2. Add Install PWA button + OTA Update Banner
    install_btn_html = """        <button type="button" id="pwa-install-btn" onclick="triggerPwaInstall()" class="hidden px-3 py-1.5 bg-indigo-950 hover:bg-indigo-900 border border-indigo-700/70 text-indigo-200 font-bold rounded-lg text-xs transition items-center gap-1.5 shadow-sm" title="Install Hive Alignment as Desktop/Mobile App">
          <i data-lucide="download" class="w-3.5 h-3.5 text-indigo-400"></i> Install App
        </button>"""

    if 'id="pwa-install-btn"' not in html:
        html = html.replace(
            '<div id="auth-user-badge" class="hidden items-center gap-2">',
            install_btn_html + '\n\n        <div id="auth-user-badge" class="hidden items-center gap-2">',
            1,
        )

    ota_banner_html = """  <!-- OTA UPDATE TOAST BANNER -->
  <div id="pwa-ota-banner" class="hidden fixed bottom-4 right-4 z-[9999] max-w-sm bg-slate-900 border border-emerald-500/70 rounded-2xl p-4 shadow-2xl flex items-center justify-between gap-3">
    <div class="space-y-0.5">
      <span class="text-[10px] font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
        <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span> OTA Build Update Ready
      </span>
      <p id="pwa-ota-msg" class="text-xs text-slate-200">New cockpit features &amp; sync engine deployed.</p>
    </div>
    <button type="button" onclick="applyPwaOtaUpdateNow()" class="px-3 py-1.5 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold rounded-xl text-xs flex-shrink-0">
      Update Now
    </button>
  </div>"""

    if 'id="pwa-ota-banner"' not in html:
        html = html.replace("  <!-- MODALS -->", ota_banner_html + "\n\n  <!-- MODALS -->", 1)

    # 3. Ensure cleanDefinedProps prevents undefined/NaN% on cloud telemetry merge
    old_get_tel = """    function getWearableTelemetry() {
      if (!window.userAppState.wearableTelemetry) {
        window.userAppState.wearableTelemetry = JSON.parse(JSON.stringify(window.DEFAULT_WEARABLE_TELEMETRY));
      }
      return window.userAppState.wearableTelemetry;
    }"""

    new_get_tel = """    function cleanDefinedProps(obj) {
      const out = {};
      if (!obj || typeof obj !== 'object') return out;
      Object.keys(obj).forEach(k => {
        if (obj[k] !== undefined && obj[k] !== null && obj[k] !== '') out[k] = obj[k];
      });
      return out;
    }

    function getWearableTelemetry() {
      const def = JSON.parse(JSON.stringify(window.DEFAULT_WEARABLE_TELEMETRY));
      const cur = window.userAppState.wearableTelemetry || {};
      window.userAppState.wearableTelemetry = {
        syncedAt: cur.syncedAt || def.syncedAt,
        whoop: Object.assign({}, def.whoop, cleanDefinedProps(cur.whoop)),
        garmin: Object.assign({}, def.garmin, cleanDefinedProps(cur.garmin)),
        scale: Object.assign({}, def.scale, cleanDefinedProps(cur.scale))
      };
      if (!Array.isArray(window.userAppState.wearableTelemetry.whoop.trend7d) ||
          window.userAppState.wearableTelemetry.whoop.trend7d.some(v => typeof v !== 'number' || isNaN(v))) {
        window.userAppState.wearableTelemetry.whoop.trend7d = def.whoop.trend7d;
      }
      return window.userAppState.wearableTelemetry;
    }"""

    if "function cleanDefinedProps(" not in html and old_get_tel in html:
        html = html.replace(old_get_tel, new_get_tel, 1)

    # 4. Inject OTA Service Worker Registration, Fingerprint Check & Install Prompt Logic
    ota_js = """    // PWA INSTALL & OVER-THE-AIR (OTA) AUTO-UPDATE ENGINE
    window.deferredPwaPrompt = null;
    window.initialBuildFingerprint = null;
    window.otaReloadPending = false;

    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      window.deferredPwaPrompt = e;
      const btn = document.getElementById('pwa-install-btn');
      if (btn) {
        btn.classList.remove('hidden');
        btn.classList.add('flex');
      }
    });

    window.triggerPwaInstall = async function() {
      if (!window.deferredPwaPrompt) {
        alert('To install Hive Alignment: open your browser menu (⋮ or Share) and select "Install App" or "Add to Home Screen".');
        return;
      }
      window.deferredPwaPrompt.prompt();
      const choice = await window.deferredPwaPrompt.userChoice;
      if (choice && choice.outcome === 'accepted') {
        const btn = document.getElementById('pwa-install-btn');
        if (btn) btn.classList.add('hidden');
      }
      window.deferredPwaPrompt = null;
    };

    window.applyPwaOtaUpdateNow = function() {
      if (window.otaReloadPending) return;
      window.otaReloadPending = true;
      try { localStorage.setItem('sanctuary_user_state', JSON.stringify(window.userAppState)); } catch (e) {}
      window.location.reload();
    };

    async function computeHtmlFingerprint() {
      try {
        const res = await fetch('./index.html?ota_ts=' + Date.now(), { cache: 'no-store' });
        if (!res.ok) return null;
        const text = await res.text();
        const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text));
        return Array.from(new Uint8Array(buf)).slice(0, 8).map(b => b.toString(16).padStart(2, '0')).join('');
      } catch (e) {
        return null;
      }
    }

    async function checkForOtaPushUpdate(autoApply) {
      if (window._swReg) {
        try { await window._swReg.update(); } catch (e) {}
      }
      const latestHash = await computeHtmlFingerprint();
      if (!latestHash) return;
      if (!window.initialBuildFingerprint) {
        window.initialBuildFingerprint = latestHash;
        return;
      }
      if (latestHash !== window.initialBuildFingerprint) {
        const banner = document.getElementById('pwa-ota-banner');
        const msg = document.getElementById('pwa-ota-msg');
        if (banner) banner.classList.remove('hidden');
        if (msg) msg.innerText = `New GitHub push detected (${latestHash}). Syncing latest cockpit build...`;
        if (autoApply) {
          setTimeout(() => window.applyPwaOtaUpdateNow(), 1400);
        }
      }
    }

    async function initPwaOtaEngine() {
      window.initialBuildFingerprint = await computeHtmlFingerprint();
      if ('serviceWorker' in navigator) {
        try {
          const reg = await navigator.serviceWorker.register('./sw.js', { updateViaCache: 'none' });
          window._swReg = reg;
          reg.addEventListener('updatefound', () => {
            const newWorker = reg.installing;
            if (!newWorker) return;
            newWorker.addEventListener('statechange', () => {
              if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                newWorker.postMessage({ type: 'SKIP_WAITING' });
                const banner = document.getElementById('pwa-ota-banner');
                if (banner) banner.classList.remove('hidden');
              }
            });
          });
          navigator.serviceWorker.addEventListener('controllerchange', () => {
            window.applyPwaOtaUpdateNow();
          });
        } catch (err) {
          console.warn('SW registration notice:', err);
        }
      }

      document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible') {
          checkForOtaPushUpdate(true);
        }
      });
      setInterval(() => checkForOtaPushUpdate(true), 5 * 60 * 1000);
    }"""

    if "function initPwaOtaEngine()" not in html:
        html = html.replace(
            "    // Initialize Icons, Session & Recovery Link Detection on Load",
            ota_js + "\n\n    // Initialize Icons, Session & Recovery Link Detection on Load",
            1,
        )
        html = html.replace(
            "      initIslamicFaithAndPrayerTimes();",
            "      initIslamicFaithAndPrayerTimes();\n      initPwaOtaEngine();",
            1,
        )

    with open(INDEX_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)

    onclicks = set(re.findall(r'onclick="([a-zA-Z0-9_]+)\(', html))
    missing = [fn for fn in sorted(onclicks) if f"window.{fn}" not in html and f"function {fn}" not in html]
    assert not missing, f"Missing JS handlers: {missing}"
    print(f"Successfully patched {INDEX_PATH} for PWA + OTA updates! ({len(onclicks)} button handlers verified)")


if __name__ == "__main__":
    main()

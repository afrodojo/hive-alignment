import os
import re

INDEX_PATH = os.path.join("docs", "index.html")
SYNC_PY_PATH = os.path.join("scripts", "sync_wearables.py")


def main():
    if not os.path.exists(INDEX_PATH):
        raise FileNotFoundError(f"Could not find {INDEX_PATH}. Run from repository root.")

    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    old_pull_merge = r"""        const prevTel = JSON.parse(JSON.stringify(getWearableTelemetry()));
        if (data.encrypted_payload && window.masterPassphrase) {
          try {
            const dec = await window.SanctuaryVaultCrypto.decryptPayload(data.encrypted_payload, window.masterPassphrase);
            window.userAppState = Object.assign(window.userAppState, dec);
          } catch (e) {
            if (data.data) window.userAppState = Object.assign(window.userAppState, data.data);
          }
        } else if (data.data) {
          window.userAppState = Object.assign(window.userAppState, data.data);
        }

        // Deep-merge wearableTelemetry
        const cloudTel = data.data?.wearableTelemetry || {};
        const defTel = JSON.parse(JSON.stringify(window.DEFAULT_WEARABLE_TELEMETRY));
        window.userAppState.wearableTelemetry = {
          syncedAt: cloudTel.syncedAt || prevTel.syncedAt,
          whoop: Object.assign({}, defTel.whoop, cleanDefinedProps(prevTel.whoop), cleanDefinedProps(cloudTel.whoop)),
          garmin: Object.assign({}, defTel.garmin, cleanDefinedProps(prevTel.garmin), cleanDefinedProps(cloudTel.garmin)),
          scale: Object.assign({}, defTel.scale, cleanDefinedProps(prevTel.scale), cleanDefinedProps(cloudTel.scale))
        };"""

    new_pull_merge = r"""        const localBeforePull = JSON.parse(JSON.stringify(getWearableTelemetry()));
        let decryptedTel = {};
        if (data.encrypted_payload && window.masterPassphrase) {
          try {
            const dec = await window.SanctuaryVaultCrypto.decryptPayload(data.encrypted_payload, window.masterPassphrase);
            if (dec && dec.wearableTelemetry) {
              decryptedTel = JSON.parse(JSON.stringify(dec.wearableTelemetry));
            }
            window.userAppState = Object.assign(window.userAppState, dec);
          } catch (e) {
            if (data.data) window.userAppState = Object.assign(window.userAppState, data.data);
          }
        } else if (data.data) {
          window.userAppState = Object.assign(window.userAppState, data.data);
        }

        // Deep-merge: Defaults -> Local before pull -> Decrypted cross-device vault -> Live Cloud Worker telemetry
        const cloudTel = data.data?.wearableTelemetry || {};
        const defTel = JSON.parse(JSON.stringify(window.DEFAULT_WEARABLE_TELEMETRY));
        window.userAppState.wearableTelemetry = {
          syncedAt: cloudTel.syncedAt || decryptedTel.syncedAt || localBeforePull.syncedAt,
          whoop: Object.assign(
            {},
            defTel.whoop,
            cleanDefinedProps(localBeforePull.whoop),
            cleanDefinedProps(decryptedTel.whoop),
            cleanDefinedProps(cloudTel.whoop)
          ),
          garmin: Object.assign(
            {},
            defTel.garmin,
            cleanDefinedProps(localBeforePull.garmin),
            cleanDefinedProps(decryptedTel.garmin),
            cleanDefinedProps(cloudTel.garmin)
          ),
          scale: Object.assign(
            {},
            defTel.scale,
            cleanDefinedProps(localBeforePull.scale),
            cleanDefinedProps(decryptedTel.scale),
            cleanDefinedProps(cloudTel.scale)
          )
        };"""

    assert old_pull_merge in html, "Could not locate pullCloudUserData merge block in docs/index.html"
    html = html.replace(old_pull_merge, new_pull_merge, 1)

    old_manual_feedback = r"""        if (manualTrigger) {
          const scoutMsg = addedScouted > 0 ? ` • +${addedScouted} New Scouted Paper(s)` : '';
          setSyncFeedback(`Cloud synced! Garmin Readiness: ${localTel.garmin?.readiness ?? '--'} • Steps: ${Number(localTel.garmin?.steps || 0).toLocaleString()}${scoutMsg}`, false);
        }"""

    new_manual_feedback = r"""        if (manualTrigger) {
          setWearableDashboardView('all');
          const scoutMsg = addedScouted > 0 ? ` • +${addedScouted} New Scouted Paper(s)` : '';
          setSyncFeedback(`Cloud synced! WHOOP: ${localTel.whoop?.recovery ?? '--'}% • Garmin Readiness: ${localTel.garmin?.readiness ?? '--'} • Steps: ${Number(localTel.garmin?.steps || 0).toLocaleString()}${scoutMsg}`, false);
        }"""

    if old_manual_feedback in html:
        html = html.replace(old_manual_feedback, new_manual_feedback, 1)

    onclicks = set(re.findall(r'onclick="([a-zA-Z0-9_]+)\(', html))
    missing = [fn for fn in sorted(onclicks) if f"window.{fn}" not in html and f"function {fn}" not in html]
    assert not missing, f"Missing JS handlers: {missing}"

    with open(INDEX_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    print(f"Updated {INDEX_PATH} (cross-device E2EE telemetry merge + All Devices view switch).")

    if os.path.exists(SYNC_PY_PATH):
        with open(SYNC_PY_PATH, "r", encoding="utf-8") as f:
            py_txt = f.read()
        old_whoop_post = (
            '                data={\n'
            '                    "grant_type": "refresh_token",\n'
            '                    "refresh_token": WHOOP_REFRESH_TOKEN,\n'
            '                    "client_id": WHOOP_CLIENT_ID,\n'
            '                    "client_secret": WHOOP_CLIENT_SECRET,\n'
            '                },'
        )
        new_whoop_post = (
            '                data={\n'
            '                    "grant_type": "refresh_token",\n'
            '                    "refresh_token": WHOOP_REFRESH_TOKEN,\n'
            '                    "client_id": WHOOP_CLIENT_ID,\n'
            '                    "client_secret": WHOOP_CLIENT_SECRET,\n'
            '                    "scope": "offline",\n'
            '                },'
        )
        if old_whoop_post in py_txt:
            py_txt = py_txt.replace(old_whoop_post, new_whoop_post, 1)
            with open(SYNC_PY_PATH, "w", encoding="utf-8", newline="\n") as f:
                f.write(py_txt)
            print(f"Updated {SYNC_PY_PATH} with WHOOP scope='offline' refresh parameter.")


if __name__ == "__main__":
    main()

import os
import io
import json
import uuid
import base64
import tarfile
import tempfile
from datetime import datetime, timedelta, timezone
import requests

SUPA_URL = os.environ.get("SUPABASE_URL", "https://jsyooxahstzrhipbocss.supabase.co").rstrip("/")
SUPA_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_ANON_KEY", "")
TARGET_EMAIL = os.environ.get("HIVE_USER_EMAIL", "cyberdojosensei@gmail.com").strip().lower()

GARMIN_EMAIL = os.environ.get("GARMIN_EMAIL", "").strip()
GARMIN_PASSWORD = os.environ.get("GARMIN_PASSWORD", "").strip()
GARMIN_TOKENSTORE = os.environ.get("GARMIN_TOKENSTORE", "").strip()

WHOOP_CLIENT_ID = os.environ.get("WHOOP_CLIENT_ID", "").strip()
WHOOP_CLIENT_SECRET = os.environ.get("WHOOP_CLIENT_SECRET", "").strip()
WHOOP_REFRESH_TOKEN = os.environ.get("WHOOP_REFRESH_TOKEN", "").strip()
WHOOP_ACCESS_TOKEN = os.environ.get("WHOOP_ACCESS_TOKEN", "").strip()

GH_PAT = os.environ.get("GH_PAT", "").strip()
GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY", "afrodojo/hive-alignment").strip()


def supa_headers(extra=None):
    h = {
        "apikey": SUPA_KEY,
        "Authorization": f"Bearer {SUPA_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    if extra:
        h.update(extra)
    return h


def fmt_millis_hm(ms_val) -> str:
    total_mins = round(float(ms_val or 0) / 60000.0)
    hours = total_mins // 60
    mins = total_mins % 60
    return f"{hours}h {mins:02d}m"


def rotate_github_secret(secret_name: str, new_value: str):
    if not (GH_PAT and GITHUB_REPOSITORY and new_value):
        return False
    try:
        from nacl import encoding, public
        gh_headers = {
            "Authorization": f"Bearer {GH_PAT}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        pk_url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/actions/secrets/public-key"
        pk_res = requests.get(pk_url, headers=gh_headers, timeout=15)
        if not pk_res.ok:
            print(f"GitHub secret public-key status: {pk_res.status_code}")
            return False
        pk_data = pk_res.json()
        pub_key = public.PublicKey(pk_data["key"].encode("utf-8"), encoding.Base64Encoder())
        sealed_box = public.SealedBox(pub_key)
        encrypted_b64 = base64.b64encode(sealed_box.encrypt(new_value.encode("utf-8"))).decode("utf-8")

        put_url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/actions/secrets/{secret_name}"
        put_res = requests.put(
            put_url,
            headers=gh_headers,
            json={"encrypted_value": encrypted_b64, "key_id": pk_data["key_id"]},
            timeout=15,
        )
        if put_res.status_code in (201, 204):
            print(f"Rotated GitHub Secret {secret_name} successfully.")
            return True
        print(f"GitHub secret PUT status for {secret_name}: {put_res.status_code}")
    except Exception as exc:
        print(f"Secret rotation notice ({secret_name}): {exc}")
    return False


def unpack_garmin_tokenstore(b64_blob: str, target_dir: str) -> bool:
    if not b64_blob:
        return False
    try:
        raw_bytes = base64.b64decode(b64_blob)
        with tarfile.open(fileobj=io.BytesIO(raw_bytes), mode="r:gz") as tf:
            tf.extractall(path=target_dir)
        return any(os.scandir(target_dir))
    except Exception as exc:
        print(f"Garmin tokenstore unpack notice: {exc}")
        return False


def pack_garmin_tokenstore(source_dir: str) -> str:
    if not os.path.isdir(source_dir):
        return ""
    files = [f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f))]
    if not files:
        return ""
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tf:
        for fname in sorted(files):
            fpath = os.path.join(source_dir, fname)
            info = tf.gettarinfo(fpath, arcname=fname)
            info.mtime = 0
            with open(fpath, "rb") as fh:
                tf.addfile(info, fh)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def fetch_existing_row():
    url = f"{SUPA_URL}/rest/v1/brotherhood_status?brother=eq.{requests.utils.quote(TARGET_EMAIL)}&select=*"
    res = requests.get(url, headers=supa_headers(), timeout=20)
    if res.ok and res.json():
        return res.json()[0]
    return None


def build_schema_safe_insert_payload(state_data, now_iso):
    payload = {
        "brother": TARGET_EMAIL,
        "data": state_data,
        "updated_at": now_iso,
    }
    try:
        spec_res = requests.get(f"{SUPA_URL}/rest/v1/", headers=supa_headers(), timeout=15)
        if spec_res.ok:
            spec = spec_res.json()
            defs = (
                spec.get("definitions", {}).get("brotherhood_status")
                or spec.get("components", {}).get("schemas", {}).get("brotherhood_status", {})
            )
            props = defs.get("properties") or {}
            required_cols = defs.get("required") or []

            if "fellowship_circle" in props:
                payload["fellowship_circle"] = "brothers"
            if "spiritual_path" in props:
                payload["spiritual_path"] = "islam"

            for col in required_cols:
                if col in payload:
                    continue
                prop = props.get(col, {})
                fmt = str(prop.get("format", "")).lower()
                typ = str(prop.get("type", "string")).lower()
                if "uuid" in fmt:
                    payload[col] = str(uuid.uuid4())
                elif "email" in col.lower():
                    payload[col] = TARGET_EMAIL
                elif "date" in fmt or "time" in fmt:
                    payload[col] = now_iso
                elif typ in ("integer", "number"):
                    payload[col] = 0
                elif typ == "boolean":
                    payload[col] = False
                else:
                    payload[col] = "default"

            if props:
                payload = {k: v for k, v in payload.items() if k in props}
    except Exception as exc:
        print(f"Schema inspection notice: {exc}")
    return payload


def authenticate_garmin_with_tokenstore(token_dir: str):
    from garminconnect import Garmin

    has_cached = unpack_garmin_tokenstore(GARMIN_TOKENSTORE, token_dir)
    if has_cached:
        try:
            client = Garmin()
            client.login(tokenstore=token_dir)
            print("Garmin Connect resumed directly from GARMIN_TOKENSTORE (SSO skipped).")
            return client
        except Exception as exc:
            print(f"Stored Garmin token expired or invalid ({exc}); falling back to credential login...")

    if not (GARMIN_EMAIL and GARMIN_PASSWORD):
        return None

    client = Garmin(GARMIN_EMAIL, GARMIN_PASSWORD)
    client.login(tokenstore=token_dir)
    if not any(os.scandir(token_dir)) and hasattr(client, "garth"):
        try:
            client.garth.dump(token_dir)
        except Exception:
            pass
    return client


def preserve_fitdays_scale(scale_block: dict):
    """Ensure Fitdays smart scale measurements remain authoritative and are never overwritten by Garmin."""
    if not isinstance(scale_block, dict):
        return
    # If Garmin previously overwrote the 4 main tiles on top of the Nov 20, 2026 Fitdays record, restore them
    if scale_block.get("fatMass") == 59.5 and scale_block.get("weight") == 235:
        scale_block.update(
            {
                "source": "Fitdays • Nov 20, 2026",
                "weight": 233.0,
                "weightDelta": "-5.5 lbs (Target 100%)",
                "bodyFat": 25.5,
                "fatMass": 59.5,
                "fatFreeMass": 173.5,
                "muscleMass": 161.8,
                "skeletalMusclePct": 43.1,
                "hydration": 54.6,
                "waterWeight": 127.2,
                "visceralFat": 10.0,
                "bmi": 31.6,
                "whr": 0.89,
                "bmr": 2072,
            }
        )
    elif scale_block.get("weight") and not scale_block.get("source"):
        scale_block["source"] = "Fitdays Smart Scale"


def sync_garmin(telemetry):
    scale_block = telemetry.setdefault("scale", {})
    preserve_fitdays_scale(scale_block)

    if not (GARMIN_TOKENSTORE or (GARMIN_EMAIL and GARMIN_PASSWORD)):
        print("Skipping Garmin sync (neither GARMIN_TOKENSTORE nor GARMIN_EMAIL/GARMIN_PASSWORD set).")
        return

    try:
        with tempfile.TemporaryDirectory(prefix="garmin_tokens_") as token_dir:
            client = authenticate_garmin_with_tokenstore(token_dir)
            if not client:
                print("Skipping Garmin sync (credentials not available).")
                return

            packed_tokens = pack_garmin_tokenstore(token_dir)
            if packed_tokens and packed_tokens != GARMIN_TOKENSTORE:
                rotate_github_secret("GARMIN_TOKENSTORE", packed_tokens)

            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            stats = client.get_stats(today) or {}
            garmin_block = telemetry.setdefault("garmin", {})

            if isinstance(stats, dict):
                if stats.get("totalSteps") is not None:
                    garmin_block["steps"] = int(stats["totalSteps"])
                if stats.get("bodyBatteryMostRecentValue") is not None:
                    garmin_block["bodyBattery"] = int(stats["bodyBatteryMostRecentValue"])
                elif stats.get("bodyBatteryChargedValue") is not None:
                    garmin_block["bodyBattery"] = int(stats["bodyBatteryChargedValue"])

            try:
                readiness = client.get_training_readiness(today)
                if isinstance(readiness, list) and readiness:
                    score = readiness[0].get("score")
                    if score is not None:
                        garmin_block["readiness"] = int(score)
                elif isinstance(readiness, dict) and readiness.get("score") is not None:
                    garmin_block["readiness"] = int(readiness["score"])
            except Exception as e:
                print(f"Garmin training readiness warning: {e}")

            try:
                for d_off in range(0, 14):
                    check_day = (datetime.now(timezone.utc) - timedelta(days=d_off)).strftime("%Y-%m-%d")
                    max_met = client.get_max_metrics(check_day)
                    entry = max_met[0] if isinstance(max_met, list) and max_met else (max_met if isinstance(max_met, dict) else {})
                    vo2 = (entry.get("generic") or {}).get("vo2MaxPreciseValue") or (entry.get("generic") or {}).get("vo2MaxValue")
                    if vo2:
                        garmin_block["vo2Max"] = round(float(vo2), 1)
                        break
            except Exception as e:
                print(f"Garmin VO2 max warning: {e}")

            activities = client.get_activities(0, 40) or []
            if activities:
                latest = activities[0]
                act_name = latest.get("activityName", "GPS Session")
                dur_min = round((latest.get("duration") or 0) / 60)
                avg_hr = round(latest.get("averageHR") or 0)
                garmin_block["lastActivity"] = f"{act_name} • {dur_min} min • Avg HR {avg_hr} bpm"

                now_dt = datetime.now(timezone.utc)
                acute_load = 0.0
                chronic_load = 0.0
                for act in activities:
                    start_str = act.get("startTimeGMT") or act.get("startTimeLocal")
                    if not start_str:
                        continue
                    try:
                        act_dt = datetime.fromisoformat(start_str.replace(" ", "T")).replace(tzinfo=timezone.utc)
                    except Exception:
                        continue
                    age_days = (now_dt - act_dt).total_seconds() / 86400.0
                    load = float(act.get("activityTrainingLoad") or ((act.get("duration") or 0) / 60.0) * 1.4)
                    if age_days <= 7:
                        acute_load += load
                    if age_days <= 28:
                        chronic_load += load

                weekly_chronic = chronic_load / 4.0 if chronic_load > 0 else 0.0
                if weekly_chronic > 0:
                    garmin_block["acwr"] = round(acute_load / weekly_chronic, 2)
                    garmin_block["acuteLoad"] = round(acute_load)
                    garmin_block["chronicLoad"] = round(weekly_chronic)

            # Only fall back to Garmin body composition if Fitdays smart scale data is not present
            has_fitdays = (
                "fitdays" in str(scale_block.get("source", "")).lower()
                or scale_block.get("fatMass") is not None
                or scale_block.get("visceralFat") is not None
                or scale_block.get("weight") is not None
            )
            if not has_fitdays:
                try:
                    start_28 = (datetime.now(timezone.utc) - timedelta(days=28)).strftime("%Y-%m-%d")
                    body = client.get_body_composition(start_28, today) or {}
                    weight_list = body.get("dateWeightList") or []
                    if weight_list:
                        w_latest = weight_list[-1]
                        if w_latest.get("weight"):
                            scale_block["weight"] = round(float(w_latest["weight"]) / 453.59237, 1)
                        if w_latest.get("bodyFat"):
                            scale_block["bodyFat"] = round(float(w_latest["bodyFat"]), 1)
                        if w_latest.get("muscleMass"):
                            scale_block["muscleMass"] = round(float(w_latest["muscleMass"]) / 453.59237, 1)
                        if w_latest.get("bodyWater"):
                            scale_block["hydration"] = round(float(w_latest["bodyWater"]), 1)
                except Exception as e:
                    print(f"Garmin body composition warning: {e}")

            print("Garmin Connect sync completed successfully (Fitdays scale preserved).")
    except Exception as exc:
        print(f"Garmin sync warning: {exc}")


def sync_whoop(telemetry):
    token = WHOOP_ACCESS_TOKEN
    if WHOOP_CLIENT_ID and WHOOP_CLIENT_SECRET and WHOOP_REFRESH_TOKEN:
        try:
            tok_res = requests.post(
                "https://api.prod.whoop.com/oauth/oauth2/token",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": WHOOP_REFRESH_TOKEN,
                    "client_id": WHOOP_CLIENT_ID,
                    "client_secret": WHOOP_CLIENT_SECRET,
                    "scope": "offline",
                },
                timeout=20,
            )
            if tok_res.ok:
                tok_json = tok_res.json()
                token = tok_json.get("access_token", token)
                new_refresh = tok_json.get("refresh_token")
                if new_refresh and new_refresh != WHOOP_REFRESH_TOKEN:
                    rotate_github_secret("WHOOP_REFRESH_TOKEN", new_refresh)
            else:
                print(f"WHOOP token refresh status: {tok_res.status_code}")
        except Exception as exc:
            print(f"WHOOP refresh warning: {exc}")

    if not token:
        print("Skipping WHOOP API sync (no WHOOP_REFRESH_TOKEN or WHOOP_ACCESS_TOKEN set).")
        return

    try:
        headers = {"Authorization": f"Bearer {token}"}
        rec_res = requests.get("https://api.prod.whoop.com/developer/v2/recovery?limit=7", headers=headers, timeout=20)
        cyc_res = requests.get("https://api.prod.whoop.com/developer/v2/cycle?limit=1", headers=headers, timeout=20)
        slp_res = requests.get("https://api.prod.whoop.com/developer/v2/activity/sleep?limit=3", headers=headers, timeout=20)

        if not rec_res.ok:
            print(f"WHOOP API status {rec_res.status_code}")
            return

        whoop_block = telemetry.setdefault("whoop", {})
        rec_records = rec_res.json().get("records") or []
        if rec_records:
            s0 = rec_records[0].get("score") or {}
            if s0.get("recovery_score") is not None:
                whoop_block["recovery"] = round(float(s0["recovery_score"]))
            if s0.get("hrv_rmssd_milli") is not None:
                whoop_block["hrv"] = round(float(s0["hrv_rmssd_milli"]))
            if s0.get("resting_heart_rate") is not None:
                whoop_block["rhr"] = round(float(s0["resting_heart_rate"]))
            if s0.get("spo2_percentage") is not None:
                whoop_block["spo2"] = round(float(s0["spo2_percentage"]), 1)
            if s0.get("skin_temp_celsius") is not None:
                whoop_block["skinTemp"] = f"{float(s0['skin_temp_celsius']):.2f}"
            trend = [round(float(r.get("score", {}).get("recovery_score", 0))) for r in reversed(rec_records) if r.get("score")]
            if trend:
                whoop_block["trend7d"] = trend

        if cyc_res.ok:
            cyc_records = cyc_res.json().get("records") or []
            if cyc_records and cyc_records[0].get("score", {}).get("strain") is not None:
                whoop_block["strain"] = f"{float(cyc_records[0]['score']['strain']):.1f}"

        if slp_res.ok:
            slp_records = slp_res.json().get("records") or []
            # Prefer the latest scored primary sleep session (non-nap)
            primary_sleeps = [
                r for r in slp_records
                if not r.get("nap") and (r.get("score_state") == "SCORED" or r.get("score"))
            ]
            chosen_sleep = primary_sleeps[0] if primary_sleeps else (slp_records[0] if slp_records else None)
            if chosen_sleep:
                slp_score = chosen_sleep.get("score") or {}
                if slp_score.get("sleep_performance_percentage") is not None:
                    whoop_block["sleepPerf"] = round(float(slp_score["sleep_performance_percentage"]))

                stages = slp_score.get("stage_summary") or {}
                rem_ms = stages.get("total_rem_sleep_time_milli")
                deep_ms = stages.get("total_slow_wave_sleep_time_milli")
                light_ms = stages.get("total_light_sleep_time_milli")

                if rem_ms is not None:
                    whoop_block["rem"] = fmt_millis_hm(rem_ms)
                if deep_ms is not None:
                    whoop_block["deep"] = fmt_millis_hm(deep_ms)
                if light_ms is not None:
                    whoop_block["light"] = fmt_millis_hm(light_ms)

                if any(v is not None for v in (rem_ms, deep_ms, light_ms)):
                    total_asleep_ms = float(rem_ms or 0) + float(deep_ms or 0) + float(light_ms or 0)
                    whoop_block["sleepDuration"] = fmt_millis_hm(total_asleep_ms)
                elif stages.get("total_in_bed_time_milli") is not None:
                    in_bed_ms = float(stages.get("total_in_bed_time_milli") or 0)
                    awake_ms = float(stages.get("total_awake_time_milli") or 0)
                    whoop_block["sleepDuration"] = fmt_millis_hm(max(0.0, in_bed_ms - awake_ms))

        print("WHOOP API v2 sync (recovery, strain & sleep stages) completed successfully.")
    except Exception as exc:
        print(f"WHOOP sync warning: {exc}")


def main():
    if not SUPA_KEY:
        print("ERROR: Missing SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY environment variable.")
        return

    existing_row = fetch_existing_row()
    state_data = (existing_row.get("data") if existing_row else None) or {}
    if not isinstance(state_data, dict):
        state_data = {}
    telemetry = state_data.setdefault("wearableTelemetry", {})

    sync_garmin(telemetry)
    sync_whoop(telemetry)

    now_iso = datetime.now(timezone.utc).isoformat()
    telemetry["syncedAt"] = now_iso
    telemetry.setdefault("whoop", {})["lastSync"] = f"Cloud Auto-Sync ({datetime.now(timezone.utc).strftime('%b %d, %H:%M UTC')})"
    state_data["wearableTelemetry"] = telemetry

    if existing_row:
        patch_url = f"{SUPA_URL}/rest/v1/brotherhood_status?brother=eq.{requests.utils.quote(TARGET_EMAIL)}"
        res = requests.patch(
            patch_url,
            headers=supa_headers({"Prefer": "return=minimal"}),
            data=json.dumps({"data": state_data, "updated_at": now_iso}),
            timeout=20,
        )
        print("Supabase PATCH status:", res.status_code, res.text[:200])
    else:
        payload = build_schema_safe_insert_payload(state_data, now_iso)
        res = requests.post(
            f"{SUPA_URL}/rest/v1/brotherhood_status",
            headers=supa_headers({"Prefer": "return=minimal"}),
            data=json.dumps(payload),
            timeout=20,
        )
        print("Supabase INSERT status:", res.status_code, res.text[:200])


if __name__ == "__main__":
    main()

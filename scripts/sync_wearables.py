import os
import json
import uuid
from datetime import datetime, timedelta, timezone
import requests

SUPA_URL = os.environ.get("SUPABASE_URL", "https://jsyooxahstzrhipbocss.supabase.co").rstrip("/")
SUPA_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_ANON_KEY", "")
TARGET_EMAIL = os.environ.get("HIVE_USER_EMAIL", "cyberdojosensei@gmail.com").strip().lower()

GARMIN_EMAIL = os.environ.get("GARMIN_EMAIL", "").strip()
GARMIN_PASSWORD = os.environ.get("GARMIN_PASSWORD", "").strip()

WHOOP_CLIENT_ID = os.environ.get("WHOOP_CLIENT_ID", "").strip()
WHOOP_CLIENT_SECRET = os.environ.get("WHOOP_CLIENT_SECRET", "").strip()
WHOOP_REFRESH_TOKEN = os.environ.get("WHOOP_REFRESH_TOKEN", "").strip()
WHOOP_ACCESS_TOKEN = os.environ.get("WHOOP_ACCESS_TOKEN", "").strip()


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


def sync_garmin(telemetry):
    if not (GARMIN_EMAIL and GARMIN_PASSWORD):
        print("Skipping Garmin sync (GARMIN_EMAIL / GARMIN_PASSWORD not set).")
        return

    try:
        from garminconnect import Garmin
        client = Garmin(GARMIN_EMAIL, GARMIN_PASSWORD)
        client.login()

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        stats = client.get_stats(today) or {}
        garmin_block = telemetry.setdefault("garmin", {})
        scale_block = telemetry.setdefault("scale", {})

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
            max_met = client.get_max_metrics(today)
            entry = max_met[0] if isinstance(max_met, list) and max_met else (max_met if isinstance(max_met, dict) else {})
            vo2 = entry.get("generic", {}).get("vo2MaxPreciseValue")
            if vo2:
                garmin_block["vo2Max"] = round(float(vo2), 1)
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

        print("Garmin Connect sync completed successfully.")
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
                },
                timeout=20,
            )
            if tok_res.ok:
                token = tok_res.json().get("access_token", token)
        except Exception as exc:
            print(f"WHOOP refresh warning: {exc}")

    if not token:
        print("Skipping WHOOP API sync (no WHOOP_REFRESH_TOKEN or WHOOP_ACCESS_TOKEN set).")
        return

    try:
        headers = {"Authorization": f"Bearer {token}"}
        rec_res = requests.get("https://api.prod.whoop.com/developer/v2/recovery?limit=7", headers=headers, timeout=20)
        cyc_res = requests.get("https://api.prod.whoop.com/developer/v2/cycle?limit=1", headers=headers, timeout=20)
        slp_res = requests.get("https://api.prod.whoop.com/developer/v2/activity/sleep?limit=1", headers=headers, timeout=20)

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
            if slp_records:
                slp_score = slp_records[0].get("score") or {}
                if slp_score.get("sleep_performance_percentage") is not None:
                    whoop_block["sleepPerf"] = round(float(slp_score["sleep_performance_percentage"]))

        print("WHOOP API v2 sync completed successfully.")
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
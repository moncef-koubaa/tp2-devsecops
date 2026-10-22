"""Fait échouer le pipeline si le rapport ZAP contient des alertes High (riskcode >= 3)."""
import json
import sys

THRESHOLD = 3  # 3 = High, 2 = Medium, 1 = Low, 0 = Info
RISK = {"0": "Info", "1": "Low", "2": "Medium", "3": "High"}

with open(sys.argv[1]) as f:
    report = json.load(f)

blocking = []
for site in report.get("site", []):
    for alert in site.get("alerts", []):
        print(f"[{RISK[alert['riskcode']]}] {alert['name']} ({alert['count']} instance(s))")
        if int(alert["riskcode"]) >= THRESHOLD:
            blocking.append(alert["name"])

if blocking:
    print(f"\nECHEC : {len(blocking)} faille(s) critique(s) détectée(s) par ZAP : {', '.join(blocking)}")
    sys.exit(1)
print("\nOK : aucune faille de sévérité High détectée par ZAP")

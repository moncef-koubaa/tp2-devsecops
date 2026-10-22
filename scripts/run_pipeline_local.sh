#!/usr/bin/env bash
# Reproduit en local les étapes du pipeline .github/workflows/ci.yml
# Usage : ./scripts/run_pipeline_local.sh   (code retour 0 = pipeline vert)
set -uo pipefail
cd "$(dirname "$0")/.."
OUT=${OUT:-evidence/local}
mkdir -p "$OUT"
status=0
step() { echo; echo "===== $1 ====="; }
result() { if [ "$1" -eq 0 ]; then echo ">>> $2 : SUCCES"; else echo ">>> $2 : ECHEC"; status=1; fi; }

[ -d .venv ] || python3 -m venv .venv
. .venv/bin/activate
pip install -q -r requirements-dev.txt

step "1. Build + tests unitaires"
python -m compileall -q app && pytest -q 2>&1 | tee "$OUT/tests.txt"
result "${PIPESTATUS[0]}" "BUILD-TEST"

step "2. SAST (Bandit, seuil HIGH)"
bandit -r app --severity-level high --confidence-level medium 2>&1 | tee "$OUT/bandit.txt"
result "${PIPESTATUS[0]}" "SAST"

step "3. SCA (Trivy, seuil HIGH/CRITICAL)"
docker run --rm -v "$PWD:/src" aquasec/trivy:0.58.1 fs /src --skip-dirs /src/.venv \
  --scanners vuln --severity HIGH,CRITICAL --exit-code 1 --format table 2>&1 | tee "$OUT/trivy.txt"
result "${PIPESTATUS[0]}" "SCA"

step "4. DAST (déploiement éphémère + OWASP ZAP)"
docker build -q -t tp2-app:local . >/dev/null
docker rm -f tp2-app >/dev/null 2>&1
docker run -d --name tp2-app -p 5000:5000 tp2-app:local >/dev/null
for i in $(seq 1 30); do curl -sf http://localhost:5000/health >/dev/null && break; sleep 1; done
chmod -R a+w . 2>/dev/null
docker run --rm --network host -v "$PWD:/zap/wrk:rw" ghcr.io/zaproxy/zaproxy:stable zap-api-scan.py \
  -t openapi.yaml -f openapi -O http://localhost:5000 -J zap-report.json -r zap-report.html -I \
  > "$OUT/zap-scan.log" 2>&1
python3 scripts/zap_gate.py zap-report.json 2>&1 | tee "$OUT/zap-gate.txt"
result "${PIPESTATUS[0]}" "DAST"
mv zap-report.* "$OUT/" 2>/dev/null
docker rm -f tp2-app >/dev/null

echo
if [ $status -eq 0 ]; then echo "PIPELINE : VERT (déploiement autorisé)"; else echo "PIPELINE : ROUGE (déploiement bloqué)"; fi
exit $status

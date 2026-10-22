# TP2 DevSecOps : sécurité intégrée au pipeline CI/CD

Petite API Flask protégée par un pipeline GitHub Actions ([.github/workflows/ci.yml](.github/workflows/ci.yml)) :

| Job | Outil | Bloque si |
|-----|-------|-----------|
| `build-test` | compileall + pytest | compilation ou test en échec |
| `sast` | Bandit | issue de sévérité **HIGH** |
| `sca` | Trivy (fs) | CVE **HIGH/CRITICAL** dans les dépendances |
| `dast` | Docker (env. éphémère) + Trivy image + OWASP ZAP API scan | CVE CRITICAL dans l'image ou alerte ZAP **High** |

## Lancer le pipeline en local

```bash
./scripts/run_pipeline_local.sh        # code retour 0 = pipeline vert
```

## Branches de démonstration

- `main` : version sécurisée (pipeline vert)
- `feature/ping-vulnerable` : ajoute `/ping` avec `shell=True` + `urllib3==1.26.4` → pipeline rouge
- `feature/ping-fix` : valide l'IP, supprime le shell, met à jour urllib3 → pipeline vert

## Publier sur GitHub et ouvrir les PR

```bash
git remote add origin https://github.com/<user>/tp2-devsecops.git
git push -u origin main feature/ping-vulnerable feature/ping-fix
# PR 1 : feature/ping-vulnerable -> main  (doit échouer)
# PR 2 : feature/ping-fix -> main         (doit passer)
```

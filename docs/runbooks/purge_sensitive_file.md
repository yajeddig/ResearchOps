# Runbook : purge d'un fichier sensible du dépôt public

À utiliser si un fichier commité contient des données personnelles ou
confidentielles (le cas du 09/01/2026 : bulletin de paie dans
`content/_Inbox/`). **Procédure manuelle, à exécuter uniquement par le
propriétaire du dépôt (`yajeddig`).** WF1/WF2/WF4 ne l'exécutent jamais
automatiquement — `pii_guard.py` sert à empêcher la fuite en amont, pas à
la corriger après coup.

## Pré-requis

- `git-filter-repo` installé (`pip install git-filter-repo`).
- Le chemin exact du/des fichier(s) à purger.

## 1. Retirer le fichier du HEAD de `main`

Toujours en premier, avant la purge d'historique : coupe l'exposition
immédiate sur GitHub et sur le site le temps de faire le reste.

```bash
git checkout main && git pull
git rm "<chemin/du/fichier>"
git commit -m "security: remove leaked file from HEAD"
git push origin main
```

Vérifier qu'aucune autre branche distante n'a le fichier à sa racine
(`git ls-tree -r origin/<branche> --name-only | grep <fichier>` pour
chaque branche listée par `git ls-remote --heads origin`) — pas seulement
`main`. Le traiter de la même façon sur chaque branche concernée.

## 2. Vérifier les forks

```bash
curl -sS "https://api.github.com/repos/yajeddig/ResearchOps" | python3 -c \
  "import json,sys; print(json.load(sys.stdin)['forks_count'])"
```

S'il y a des forks : demander au support GitHub
(https://support.github.com) la purge des vues en cache pour ces forks —
un `git filter-repo` local ne les touche pas.

## 3. Purger l'historique (irréversible)

Toujours sur un clone isolé (jamais le clone de travail), branche par
branche concernée :

```bash
git clone --single-branch --branch main https://github.com/yajeddig/ResearchOps.git purge-tmp
cd purge-tmp
git filter-repo --path "<chemin/du/fichier>" --invert-paths --force
git remote add origin https://github.com/yajeddig/ResearchOps.git
git push --force origin main
```

Vérifier après coup qu'aucun commit ne référence plus le fichier :

```bash
curl -sS "https://api.github.com/repos/yajeddig/ResearchOps/commits?path=<chemin/du/fichier>"
# doit renvoyer []
```

Puis, dans le clone de travail habituel :

```bash
git fetch origin main
git reset --hard origin/main
```

Tout autre clone local (autre poste) doit être re-cloné ou remis à
`origin/main` de la même façon — il ne se remettra pas à jour par un
simple `git pull`.

## 4. Régénérer `gh-pages`

Si `.github/workflows/docs_site.yml` utilise `mkdocs gh-deploy --no-history`
(cas actuel), un simple push sur `main` touchant `content/**` suffit à
tout régénérer sans historique. Sinon, déclencher `workflow_dispatch`
manuellement et vérifier le run.

## 5. Désindexation Google

Google Search Console → Suppressions → Nouvelle demande → coller l'URL de
la page publiée. Manuel, hors de portée des workflows.

## 6. Si la donnée est un NIR ou un IBAN

Considérer la donnée comme compromise : vigilance sur les usurpations
(courriers CPAM/impôts inattendus, mouvements bancaires non reconnus)
dans les mois qui suivent.

# WF2 : Rapport de veille mensuel

**But** : un rapport citable qui croise vos captures du mois avec les publications récentes sur vos thèmes.

## Déclencheur

Cron `0 6 1 * *` (1er du mois, 06:00 UTC) ou `workflow_dispatch`.

## Sources

| Section | Source | Référence |
|---|---|---|
| A · Interne | Fiches `content/**` dont la date est dans le mois précédent | `[I n]` |
| B · Externe | Semantic Scholar, pour chaque sujet **actif** de `config/monitoring.json` (voir ci-dessous) | `[P n]` |

Par sujet :
- `seed_paper_ids` non vide → **API Recommendations** (`POST /recommendations/v1/papers`, `positivePaperIds` / `negativePaperIds`). Pas de filtre de période : l'API renvoie les papiers les plus proches des graines, et `data/monitor_seen.json` empêche de les reproposer les mois suivants.
- Sinon → **recherche par mots-clés** (`paper/search`, `keywords_academic`, période = mois précédent).
- Dans les deux cas : filtre `min_year` et `exclude_keywords` (titre + résumé), dédup inter-mois, tri par citations, `paper_limit`.

Retry avec backoff sur 429. Une clé `SEMANTIC_SCHOLAR_API_KEY` (optionnelle) relève la limite de débit.

## Génération

- Modèle : `claude-opus-5` (override par `CLAUDE_MODEL`), repli automatique en cas de refus.
- Le prompt fournit une **bibliographie numérotée fermée** ; le modèle ne peut citer que ce qui lui a été donné.
- Section **« Santé du pipeline »** ajoutée après le texte de Claude, calculée en Python (pas par le modèle) : ingestions traitées par statut, rejets par raison, taux de passage en `_Inbox`, répartition par catégorie, papiers par sujet. Source : `data/ingest_log.jsonl`, une ligne par issue traitée par WF1 (statut, code de raison, catégorie — jamais de contenu).
- Si le mois n'a ni capture ni publication, aucun rapport n'est généré (notification Telegram seulement).

## Sortie

`reports/<année>/<AAAA-MM>_Monitor.md` où `AAAA-MM` est le **mois de génération**. Seules les publications effectivement rapportées sont ajoutées à `data/monitor_seen.json` (`paperId → date du premier rapport`).

## Configuration des thèmes (`config/monitoring.json` v2)

Validée au chargement (jsonschema) : un champ inconnu, un `status` invalide, un `id` dupliqué ou un `keywords_academic` manquant fait échouer WF2 avec un message explicite, aussi envoyé sur Telegram. Un sujet v1 (sans les nouveaux champs) reste valide.

```json
{
  "id": "hybrid-sciml-bioprocess",
  "name": "Hybrid SciML for Bioprocesses",
  "status": "active",
  "priority": 1,
  "projects": [],
  "keywords_academic": ["hybrid modeling bioprocess machine learning"],
  "exclude_keywords": ["medical imaging"],
  "seed_paper_ids": [],
  "negative_paper_ids": [],
  "min_year": 2023,
  "paper_limit": 3
}
```

| Champ | Défaut | Rôle |
|---|---|---|
| `status` | `active` | `paused` : sujet ignoré |
| `priority` | 3 | ordre de traitement |
| `exclude_keywords` | `[]` | rejette un papier si présent dans titre/résumé |
| `seed_paper_ids` | `[]` | active l'API Recommendations |
| `min_year` | aucun | année de publication minimale |
| `paper_limit` | 3 | papiers max par sujet et par mois |

## Proposer des graines

```bash
python scripts/seed_from_fiches.py
```

Parcourt les fiches ayant un DOI ou un identifiant arXiv, résout le `paperId` Semantic Scholar et propose un sujet par recouvrement de mots-clés. Lecture seule : copiez à la main les `paperId` retenus dans `seed_paper_ids`. La suggestion de sujet est une heuristique grossière, à vérifier.

# WF2 : Rapport de veille mensuel

**But** : un rapport citable qui croise vos captures du mois avec les publications récentes sur vos thèmes.

## Déclencheur

Cron `0 6 1 * *` (1er du mois, 06:00 UTC) ou `workflow_dispatch`.

## Sources

| Section | Source | Référence |
|---|---|---|
| A · Interne | Fiches `content/**` dont la date est dans le mois précédent | `[I n]` |
| B · Externe | Semantic Scholar `paper/search`, filtre `publicationDateOrYear` sur le mois, requêtes = `keywords_academic` de `config/monitoring.json`, `paper_limit` par thème | `[P n]` |

SerpAPI (Google Scholar) et Perplexity ont été retirés : payants, faible rappel, et les news Perplexity n'étaient pas numérotées donc jamais citées. Semantic Scholar est gratuit ; une clé `SEMANTIC_SCHOLAR_API_KEY` (optionnelle) relève la limite de débit.

Pour compléter le rappel académique, créez des alertes Google Scholar sur les mêmes mots-clés et envoyez au bot les articles qui vous intéressent : ils deviennent des fiches `[I n]` du mois suivant.

## Génération

- Modèle : `claude-opus-5` (override par `CLAUDE_MODEL`), réflexion adaptative, repli automatique en cas de refus.
- Le prompt fournit une **bibliographie numérotée fermée** ; le modèle ne peut citer que ce qui lui a été donné et doit la recopier en fin de rapport.
- Si le mois n'a ni capture ni publication, aucun rapport n'est généré (notification Telegram seulement).

## Sortie

`reports/<année>/<AAAA-MM>_Monitor.md` où `AAAA-MM` est le **mois de génération** (convention historique conservée) ; l'en-tête indique explicitement la période couverte. Seules les publications effectivement rapportées sont ajoutées à `data/history.json`.

## Configuration des thèmes

```json
{
  "topics": [
    {
      "id": "n2o-emissions",
      "name": "N₂O Emissions in WWTP",
      "keywords_academic": ["nitrous oxide wastewater treatment", "N2O emissions modeling WWTP"],
      "paper_limit": 3
    }
  ]
}
```

`keywords_news` n'est plus utilisé.

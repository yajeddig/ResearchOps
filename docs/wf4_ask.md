# WF4 : Interroger la base

**But** : poser une question depuis Telegram et obtenir une réponse sourcée à partir de vos propres fiches.

## Déclencheur

Issue GitHub avec le label `ask`. Le pont Make la crée quand un message Telegram commence par `?` ; le titre de l'issue est la question. Vous pouvez aussi ouvrir l'issue à la main (template « Ask the knowledge base »).

## Pipeline (`src/wf4_ask.py`)

1. **Index** : titre, catégorie, date et tags de toutes les fiches (`utils/frontmatter.load_cards`).
2. **Sélection** (Claude, effort `low`) : renvoie les numéros des fiches pertinentes, 8 au plus.
3. **Réponse** (Claude `claude-opus-5`) : lit les fiches sélectionnées en entier (9 000 caractères max chacune), répond en français, cite `[C n]`, liste les sources avec leur chemin. Si rien n'est pertinent, le dit.
4. **Livraison** : commentaire complet dans l'issue, message Telegram (tronqué à 3 500 caractères avec lien vers l'issue), issue fermée.

Rien n'est commité : la réponse est éphémère, la base reste propre.

## Limites

- Recherche par index lexical via le modèle, pas d'embeddings : suffisant jusqu'à quelques centaines de fiches. Au-delà, ajouter un index vectoriel.
- Coût par question : 2 appels, de l'ordre de quelques centimes.

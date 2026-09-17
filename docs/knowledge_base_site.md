# Site de consultation

Le dépôt seul n'offre ni recherche ni navigation par tag. Le workflow `docs_site.yml` publie `content/` et `reports/` en site statique **MkDocs Material**.

## Mise en place (une fois)

1. Le workflow pousse le site sur la branche `gh-pages` à chaque push sur `main` touchant `content/`, `reports/` ou la config.
2. Dans GitHub : *Settings → Pages → Build and deployment → Source : Deploy from a branch → Branch : `gh-pages` / `(root)`*.
3. URL : `https://yajeddig.github.io/ResearchOps/`.

Le dépôt est public : le site l'est aussi. Si la base doit rester privée, passez le dépôt en privé (GitHub Pages privé nécessite un plan payant) ou consultez-la avec Obsidian.

## Ce que fait `scripts/build_site.py`

- Copie les Markdown dans `site_src/` (ignoré par git), en normalisant le frontmatter (tags en liste de chaînes).
- Génère `index.md` (compteurs, 20 dernières fiches, liste des rapports), une page par catégorie et `tags.md` (plugin `tags` de Material).
- `mkdocs build --strict` échoue sur tout lien cassé : le workflow ne publie pas un site incohérent.

## Fonctions activées

Recherche plein texte (fr/en), tags cliquables, LaTeX (MathJax), diagrammes Mermaid, mode sombre, copie de code.

## Alternative locale

Ouvrir le dossier du dépôt comme vault **Obsidian** : les fiches ont un frontmatter compatible (tags, dates), le graphe et la recherche fonctionnent sans build.

## En local

```bash
pip install -r requirements-docs.txt
python scripts/build_site.py && mkdocs serve
```

# Legacy

Code retiré en v1.2, conservé pour référence uniquement. Rien ici n'est exécuté :
les workflows ne sont plus sous `.github/workflows/` et les tests ne sont plus collectés.

| Élément | Raison du retrait |
|---|---|
| `workflows/wf3_deep_research.yml`, `src/wf3_triforce.py`, `src/agents/` | WF3 jamais utilisé (0 issue `research`), modèles retirés (`claude-3-opus`, `gemini-1.5-pro`), dominé par les produits Deep Research |
| `workflows/triforce_deep.yml`, `src/triforce_deep.py` | Stub vide exécuté chaque semaine avec des secrets exposés pour rien |
| `src/multimodal.py` | Doublon de la logique de WF1, SDK `google-generativeai` obsolète |
| `tests/test_agents.py`, `tests/test_wf3_triforce.py` | Tests des modules ci-dessus |
| `docs/wf3_deep_research.md`, `docs/deep_research.md` | Documentation associée |

À supprimer définitivement : `git rm -r legacy`.

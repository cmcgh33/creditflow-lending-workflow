# Streamlit demo deployment

The demo is deployed at [https://carla-creditflow.streamlit.app/](https://carla-creditflow.streamlit.app/). Live-browser checks on 2026-10-06 confirmed eligible, review, and decline outcomes and saved-evaluation inspection.

## Community Cloud settings

| Setting | Value |
| --- | --- |
| Repository | cmcgh33/creditflow-lending-workflow |
| Branch | main |
| Main file path | streamlit_app.py |
| Python version | 3.12 |
| App subdomain | carla-creditflow |
| Secrets | None required |

1. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/).
2. Click **Create app**, then choose the option to deploy from an existing repository.
3. Enter the repository, branch, and main file path from the table.
4. In advanced settings, choose Python 3.12. Optionally select the suggested subdomain if available.
5. Click **Deploy**. Wait for the application to finish building.
6. Verify the three scenarios, inspect history, and download an evaluation JSON.
7. Update the project README and profile README if the deployed URL changes.

[Official deployment instructions](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy).

## Behavior and verification

The hosted adapter uses the same fictional rules and evaluation function. History is **per browser session**, capped at 100 entries. It can clear on reload or session termination. Export JSON to retain a record. This differs from the original local app, whose SQLite history survives reloads.

Local run:

```bash
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

Adapter checks (from repository root, set PYTHONPATH to `.`):

```bash
PYTHONPATH=. python tests/streamlit_smoke.py
```

The hosted interface uses Streamlit controls with the same dark ombré palette. It does not expose the local API. No real loan data should be entered. No authenticated access or production lending workflow is provided.

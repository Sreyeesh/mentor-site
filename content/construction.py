# Rebuild-board content for the construction dashboard. The workstream
# stat panel derives shipped/total from this list — update it here only.
CONSTRUCTION_PAGE = {
    'workstreams': [
        {'label': 'design system', 'state': 'shipped'},
        {'label': 'static build pipeline', 'state': 'shipped'},
        {'label': 'self-hosted deployment (wsl2)', 'state': 'in progress'},
        {'label': 'cv, devops edition', 'state': 'queued'},
    ],
    'deploy_target': [
        {'label': 'compute', 'value': 'WSL2, Windows laptop'},
        {'label': 'provisioning', 'value': 'Ansible'},
        {'label': 'serving', 'value': 'gunicorn + nginx, Docker'},
        {'label': 'current host', 'value': 'GitHub Pages, static'},
    ],
}

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_production_docker_build_receives_site_url():
    dockerfile = (ROOT / 'Dockerfile').read_text(encoding='utf-8')
    freeze_step = dockerfile.index('RUN python freeze.py')

    assert dockerfile.index('ARG SITE_URL=') < freeze_step
    assert dockerfile.index('ENV SITE_URL=${SITE_URL}') < freeze_step


def test_compose_passes_site_url_as_build_arg():
    compose = (ROOT / 'docker-compose.yml').read_text(encoding='utf-8')

    assert 'SITE_URL: ${SITE_URL:-}' in compose


def test_make_docker_build_passes_site_url_as_build_arg():
    makefile = (ROOT / 'Makefile').read_text(encoding='utf-8')

    assert '--build-arg SITE_URL=$$(grep -m1 SITE_URL .env | cut -d' in makefile

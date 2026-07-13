from content.loader import load_page, load_toml, message


def test_load_toml_reads_content_file():
    data = load_toml('pages/construction.toml')

    assert data['meta']['title_suffix'] == 'Site in transition'
    assert data['workstreams'][0]['label'] == 'design system'


def test_load_page_reads_page_content():
    data = load_page('construction')

    assert data['topbar']['state_label'] == 'Site in transition — rebuild board'
    assert data['deploy_target'][0]['label'] == 'production host'


def test_site_content_contains_defaults_and_nav():
    data = load_toml('site.toml')

    assert data['site']['brand_name'] == 'Toucan Studios'
    assert data['nav_links'][0] == {
        'label': 'Home',
        'href': '/',
        'slug': 'home',
    }


def test_message_formats_values():
    result = message(
        'authoring',
        'duplicate_slug',
        slug='example-post',
    )

    assert result == 'A post with slug "example-post" already exists.'

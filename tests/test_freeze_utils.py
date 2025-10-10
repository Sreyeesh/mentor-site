from blog import strip_leading_metadata_lines


def test_strip_leading_metadata_removes_metadata_block():
    content = (
        "title: Example Post\n"
        "slug: example-post\n"
        "tags: foo, bar\n\n"
        "# Heading\n\nBody text."
    )
    cleaned = strip_leading_metadata_lines(content)
    assert cleaned.startswith('# Heading')
    assert 'example-post' not in cleaned


def test_strip_leading_metadata_leaves_normal_text():
    content = "First line\nSecond line"
    cleaned = strip_leading_metadata_lines(content)
    assert cleaned == content

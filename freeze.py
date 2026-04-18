from math import ceil
from app import app, POSTS_PER_PAGE
from models import Post, db
from flask_frozen import Freezer

app.config['FREEZER_DESTINATION'] = 'build'
freezer = Freezer(app)


@freezer.register_generator
def blog_detail():
    for p in Post.query.filter_by(draft=False).all():
        yield {'slug': p.slug}


@freezer.register_generator
def blog_tag():
    tags = {t for p in Post.query.filter_by(draft=False).all() for t in p.tag_list()}
    for tag in tags:
        yield {'tag': tag}


@freezer.register_generator
def blog_page():
    n = Post.query.filter_by(draft=False).count()
    for page in range(2, ceil(n / POSTS_PER_PAGE) + 1):
        yield {'page': page}


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    freezer.freeze()

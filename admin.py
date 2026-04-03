from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from models import Post, db


class PostAdmin(ModelView):
    column_list = ['title', 'slug', 'date', 'draft', 'featured', 'tags']
    column_sortable_list = ['title', 'date', 'draft', 'featured']
    column_searchable_list = ['title', 'slug', 'tags']
    column_filters = ['draft', 'featured', 'date']
    column_default_sort = ('date', True)

    form_columns = [
        'title', 'slug', 'date', 'description', 'excerpt',
        'hero_image', 'tags', 'featured', 'draft', 'body',
    ]
    form_widget_args = {
        'body': {'rows': 30, 'style': 'font-family: monospace; font-size: 13px;'},
        'excerpt': {'rows': 4},
        'description': {'rows': 2},
        'tags': {'placeholder': 'python, flask, web (comma-separated)'},
    }

    # Show draft badge in list
    column_labels = {
        'body': 'Content (Markdown)',
        'description': 'SEO Description',
        'hero_image': 'Hero Image URL',
    }


def init_admin(app):
    admin = Admin(
        app,
        name='Blog Admin',
        template_mode='bootstrap4',
        url='/admin',
        base_template='admin/base.html',
    )
    admin.add_view(PostAdmin(Post, db.session, name='Posts', endpoint='posts'))

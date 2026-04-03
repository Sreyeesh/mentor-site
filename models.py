from datetime import datetime, date

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    slug = db.Column(db.String(300), unique=True, nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, default=date.today)
    body = db.Column(db.Text, nullable=False, default='')
    excerpt = db.Column(db.Text)
    description = db.Column(db.String(500))
    hero_image = db.Column(db.String(500))
    tags = db.Column(db.String(300))  # comma-separated, e.g. "python,flask,web"
    draft = db.Column(db.Boolean, default=False, nullable=False)
    featured = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ------------------------------------------------------------------
    # Computed properties (not stored in DB)
    # ------------------------------------------------------------------

    @property
    def rendered_body(self) -> str:
        """Return the post body rendered from Markdown to HTML."""
        from blog.utils import render_body
        return render_body(self.body or '')

    @property
    def reading_time(self) -> int:
        """Estimated reading time in minutes."""
        from blog.utils import reading_time
        return reading_time(self.body or '')

    @property
    def computed_excerpt(self) -> str:
        """Return the explicit excerpt or auto-generate one from the body."""
        if self.excerpt:
            return self.excerpt
        from blog.utils import auto_excerpt
        return auto_excerpt(self.body or '')

    @property
    def date_display(self) -> str:
        """Human-readable date string, e.g. 'April 03, 2026'."""
        if self.date:
            return self.date.strftime('%B %d, %Y')
        return ''

    def tag_list(self) -> list[str]:
        """Return tags as a cleaned list of strings."""
        if not self.tags:
            return []
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    def __repr__(self):
        return f'<Post {self.slug!r}>'

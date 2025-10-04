
# Mentor Site

A Flask-based mentoring website with static site generation and Docker deployment.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker (optional)
- Git

### Local Development

```bash
# Clone the repository
git clone <your-repo-url>
cd mentor-site

# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py
```

### Docker Development

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or use custom deployment script
./deploy.sh
```

## 📁 Project Structure

```
.
├── app.py                     # Flask application entry point
├── deploy.sh                  # Local deployment script
├── docker-compose.yml         # Docker Compose setup
├── Dockerfile                 # Docker configuration
├── .env                       # Environment variables (local)
├── .env.example              # Environment variables template
├── .flake8                    # Flake8 configuration
├── freeze.py                  # Static site generator
├── .github/
│   └── workflows/
│       └── deploy-pages.yml   # GitHub Actions deployment
├── .gitignore                 # Git ignore rules
├── pytest.ini                # Pytest configuration
├── README.md                  # Project documentation
├── requirements.txt           # Python dependencies
├── static/
│   ├── css/
│   │   └── style.css         # Main stylesheet
│   ├── images/
│   │   ├── GameCity.png      # Game development image
│   │   └── SreyeeshProfilePic.jpg  # Profile image
│   └── js/
│       └── script.js         # JavaScript functionality
├── templates/
│   └── index.html            # Main site template
└── tests/
    └── test_app.py           # Test suite

9 directories, 19 files
```

## 🛠️ Development

### Environment Setup
Create a `.env` file for local development:
```env
SITE_NAME=Sreyeesh Garimella
SITE_EMAIL=toucan.sg@gmail.com
SITE_CALENDLY_LINK=https://calendly.com/toucan-sg/consulting-link
BASE_PATH=/mentor-site
FLASK_DEBUG=True
```

### Running Tests
```bash
pytest
```

### Code Quality
```bash
# Linting
flake8 .

# Type checking (if using mypy)
mypy .
```

### Static Site Generation
```bash
# Generate static files
python freeze.py
```

### Writing Blog Posts
- Draft a new Markdown file in `content/posts/` with front matter (`title`, `slug`, `date`, optional `tags`).
- Run `python freeze.py` to rebuild `build/blog/` pages.
- Commit the Markdown and regenerated `build/` directory (or let your deployment pipeline run the freeze step).
- Comments and reactions are powered by Giscus—configure the environment variables below so every post gets a discussion thread.

### Enabling Comments (Giscus)
1. Enable Discussions in your GitHub repository and create/pick a category for blog comments.
2. Visit [giscus.app](https://giscus.app), select your repo and category, and copy the values for `data-repo`, `data-repo-id`, `data-category`, and `data-category-id` (plus any optional settings).
3. Add those values to `.env` (see `.env.example` for all supported keys such as `GISCUS_THEME_LIGHT`/`GISCUS_THEME_DARK`).
4. Restart Flask or rerun `python freeze.py` so the updated configuration propagates into generated pages.
5. Deploy and open any blog post—new comments show up in GitHub Discussions under the category you set.

## 🚀 Deployment

### Local Docker Deployment
```bash
# Build and run container
./deploy.sh

# Access at: http://localhost:5000/mentor-site/
```

### Production Deployment
- **GitHub Actions**: Automatically deploys to GitHub Pages on push to `master`
- **Docker**: Containerized deployment with Nginx
- **Static Generation**: Uses `freeze.py` to generate static HTML

## Technical Stack

- **Backend**: Flask (Python 3.11)
- **Frontend**: HTML5, CSS3, JavaScript
- **Deployment**: Docker, GitHub Actions, GitHub Pages
- **Static Generation**: Custom freeze.py script
- **Testing**: pytest
- **Code Quality**: flake8

## 📄 License

This project is private and proprietary. All rights reserved.

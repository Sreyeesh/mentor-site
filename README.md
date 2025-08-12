# Mentor Site

A Flask-based mentoring website for **Sreyeesh Garimella** offering animation and game development coaching. Converts to static files for GitHub Pages deployment.

## Tech Stack

- Flask 2.3.3 with Python 3.11
- HTML5, CSS3, JavaScript
- Docker with nginx
- pytest for testing
- GitHub Actions for CI/CD

## Project Structure

```
mentor-site/
├── app.py                    # Flask application
├── freeze.py                 # Static site generator
├── deploy.sh                 # Local Docker deployment script
├── requirements.txt          # Python dependencies
├── Dockerfile               # Container configuration
├── docker-compose.yml       # Container orchestration
├── templates/
│   └── index.html           # Main template
├── static/
│   ├── css/                 # Stylesheets
│   ├── js/                  # JavaScript files
│   └── images/              # Assets and profile images
├── tests/
│   └── test_app.py          # Test suite
└── .github/workflows/
    └── deploy-pages.yml     # GitHub Actions CI/CD
```

## Setup

```bash
git clone <repository-url>
cd mentor-site
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Development

```bash
python app.py
```

Visit `http://localhost:5000`

## Build Static Site

```bash
python freeze.py
```

Generated files will be in the `build/` directory.

## Docker

**Local testing:**
```bash
chmod +x deploy.sh
./deploy.sh  # For local deployment and testing only
```

**Manual:**
```bash
docker build -t mentor-site .
docker run -d --name mentor-site-prod -p 5000:80 mentor-site
```

**Docker Compose:**
```bash
docker-compose up -d                    # Production
docker-compose --profile dev up -d      # Development
```

## Testing

```bash
pytest                                  # Run all tests
pytest --cov=app --cov-report=html     # With coverage report
```

## Deployment

Push to `master` branch - GitHub Actions automatically builds and deploys to GitHub Pages.

**Manual deployment:**
1. Generate static files: `python freeze.py`
2. Copy `build/` contents to GitHub Pages repository

## Configuration

```bash
SITE_NAME="Sreyeesh Garimella"
SITE_TAGLINE="Mentoring & Coaching in Animation and Video Game Development"
SITE_EMAIL="toucan.sg@gmail.com"
SITE_CALENDLY_LINK="https://calendly.com/toucan-sg/60min"
BASE_PATH="/mentor-site"  # For GitHub Pages subdirectory
```

## Live Site

**[https://toucan.ee](https://toucan.ee)**
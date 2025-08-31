
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
SITE_CALENDLY_LINK=https://calendly.com/toucan-sg/60min
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
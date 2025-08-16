
```markdown:README.md
# Sreyeesh Garimella - Mentor Site

A professional mentoring website showcasing **Sreyeesh Garimella**'s expertise in animation and game development. Built with Flask and modern web technologies, this site serves as a digital portfolio and lead generation platform for one-on-one mentoring services.

## 🚀 Quick Start

### Docker Build Commands

```bash
# Build and run with Docker Compose
docker-compose up --build

# Build only (without running)
docker-compose build

# Run in detached mode
docker-compose up -d

# Stop containers
docker-compose down

# Rebuild and restart
docker-compose up --build --force-recreate
```

##  Features

### Professional Showcase
- **Interactive Timeline** - Detailed career progression with role descriptions and skills
- **Portfolio Integration** - Showcase of work experience and achievements
- **Focus Areas** - Clear specialization in animation workflow, game design, and career guidance

### User Experience
- **Responsive Design** - Optimized for desktop, tablet, and mobile devices
- **Dark/Light Mode** - User preference toggle with persistent settings
- **Smooth Navigation** - Intuitive scrolling and section transitions
- **Accessibility** - ARIA labels and semantic HTML structure

### Contact & Lead Generation
- **Multiple Contact Options** - Email, LinkedIn, and WhatsApp integration
- **Professional Presentation** - Clean, modern design that builds trust
- **SEO Optimized** - Open Graph tags and meta descriptions for social sharing

### Technical Excellence
- **Static Site Generation** - Fast loading with pre-built HTML/CSS
- **Docker Support** - Easy deployment and testing across environments
- **Modern Stack** - Flask, Python 3.11, and contemporary web standards

## 📁 Project Structure

```
mentor-site/
├── app.py                 # Flask application entry point
├── freeze.py             # Static site generator
├── requirements.txt      # Python dependencies
├── templates/
│   └── index.html       # Main site template
├── static/
│   ├── css/
│   │   └── style.css    # Main stylesheet
│   ├── js/
│   │   └── script.js    # JavaScript functionality
│   └── images/          # Site images and assets
├── tests/
│   └── test_app.py      # Test suite
├── build/               # Generated static site
├── Dockerfile           # Docker configuration
└── docker-compose.yml   # Docker Compose setup
```

## 🛠️ Development

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

### Environment Variables
Create a `.env` file for local development:
```env
SITE_NAME=Sreyeesh Garimella
SITE_EMAIL=toucan.sg@gmail.com
SITE_CALENDLY_LINK=https://calendly.com/toucan-sg/60min
BASE_PATH=/mentor-site
FLASK_DEBUG=True
```

##  Live Sites

- **🌐 Production:** [https://toucan.ee](https://toucan.ee)
- **🔧 Development:** [http://localhost:5000/mentor-site/](http://localhost:5000/mentor-site/) (when running locally)

## Development Status

### Completed
- Core site functionality and routing
- Professional timeline with career progression
- Contact integration (Email, LinkedIn, WhatsApp)
- Responsive design for all devices
- Dark/light mode toggle
- Static site generation
- Docker containerization
- Basic test coverage

### In Progress
- Content updates and optimization
- Performance improvements
- SEO enhancements

###  Planned
- Contact form with lead tracking
- Analytics integration
- Blog/portfolio section
- Testimonial showcase

##  License

This project is private and proprietary. All rights reserved.





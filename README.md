I'll update the README to include the exact tree structure from your project. Here's the updated version:

```markdown:README.md
# Sreyeesh Garimella - Mentor Site

A professional mentoring website for **Sreyeesh Garimella**, offering personalized one-on-one guidance in animation and video game development. This platform serves as both a digital portfolio showcasing extensive industry experience and a lead generation system for high-quality mentoring services.

## 🎯 About the Mentoring Service

### What I Offer
- **Personalized 1-on-1 Sessions**: Tailored guidance based on your specific goals and skill level
- **Animation Workflow & Storytelling**: From concept to final render, covering the complete animation pipeline
- **Game Design Fundamentals**: Core principles, mechanics, and player experience design
- **Career Guidance**: Strategic advice for breaking into and advancing in creative industries
- **Portfolio & Project Feedback**: Expert review and improvement suggestions for your work

### My Background
With over 15 years of experience in the animation and gaming industry, I've worked with:
- **Walt Disney Animation Studios** - Assistant Technical Director
- **Brown Bag Films** - Render Support for Ireland's first CG feature film
- **Multiple AAA game studios** - Technical and creative roles
- **Freelance animation projects** - Diverse portfolio of work

## 🚀 Quick Start

### Local Development
```bash
# Clone the repository
git clone <your-repo-url>
cd mentor-site

# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py

# Or use Docker
./deploy.sh
```

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build

# Deploy locally with custom script
./deploy.sh
```

## 📁 Project Structure

```
.
├── app.py
├── deploy.sh
├── docker-compose.yml
├── Dockerfile
├── .env
├── .env.example
├── .flake8
├── freeze.py
├── .github
│   └── workflows
│       └── deploy-pages.yml
├── .gitignore
├── pytest.ini
├── README.md
├── requirements.txt
├── static
│   ├── css
│   │   └── style.css
│   ├── images
│   │   ├── GameCity.png
│   │   └── SreyeeshProfilePic.jpg
│   └── js
│       └── script.js
├── templates
│   └── index.html
└── tests
    └── test_app.py

9 directories, 19 files
```

##️ Technical Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Deployment**: Docker, GitHub Actions, GitHub Pages
- **Static Generation**: Custom freeze.py script
- **Testing**: pytest
- **Code Quality**: flake8

## 🎨 Features

### For Mentees
- **Professional Portfolio**: View my extensive experience and projects
- **Clear Service Offerings**: Understand exactly what mentoring includes
- **Easy Contact**: Multiple ways to get in touch (Email, LinkedIn, WhatsApp)
- **Transparent Process**: Know what to expect from mentoring sessions

### For the Platform
- **Responsive Design**: Works perfectly on all devices
- **Fast Loading**: Optimized static site generation
- **SEO Optimized**: Built for discoverability
- **Automated Updates**: Copyright and content management
- **Professional Presentation**: Clean, modern design

## 🚀 Deployment

### Local Development
```bash
# Run with Flask development server
python app.py

# Or use Docker
./deploy.sh
```

### Production Deployment
- **GitHub Actions**: Automatically deploys to GitHub Pages on push to `master`
- **Docker**: Containerized deployment with Nginx
- **Static Generation**: Uses `freeze.py` to generate static HTML

## 📞 Contact & Booking

### Get Started
- **Email**: toucan.sg@gmail.com
- **LinkedIn**: [Sreyeesh Garimella](https://www.linkedin.com/in/sreyeeshgarimella)
- **WhatsApp**: +372 5827 7155
- **Booking**: [Schedule a Session](https://calendly.com/toucan-sg/60min)

### Response Time
I personally reply within 24 hours to all inquiries.

## Live Sites

- **🌐 Production:** [https://toucan.ee](https://toucan.ee)
- **🔧 Development:** [http://localhost:5000/mentor-site/](http://localhost:5000/mentor-site/) (when running locally)

## Development Status

### ✅ Completed
- Professional portfolio and experience showcase
- Mentoring service descriptions and offerings
- Contact integration (Email, LinkedIn, WhatsApp)
- Responsive design for all devices
- Static site generation and deployment
- Docker containerization
- Automated copyright year
- GitHub Actions deployment pipeline
- Environment variable configuration

### 🔄 In Progress
- Content optimization and updates
- Performance improvements
- SEO enhancements

### 📋 Planned
- Contact form with lead tracking
- Analytics integration
- Blog/portfolio section
- Testimonial showcase
- Session booking integration

## 📄 License

This project is private and proprietary. All rights reserved.

---
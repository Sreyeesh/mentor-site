from flask import Flask, render_template
import os

app = Flask(__name__)

# Site settings - easy to update content
SITE_CONFIG = {
    'name': 'Sreyeesh Garimella',
    'tagline': 'Mentor & Coach',
    'email': 'sgarime1@gmail.com',
    'calendly_link': 'https://calendly.com/your-link',  # Update this with your actual Calendly link
    'meta_description': 'Personal mentoring and coaching with Sreyeesh Garimella. Transform your skills and achieve your goals.',
    'focus_areas': [
        'Career Development',
        'Leadership Skills',
        'Personal Growth',
        'Technical Skills'
    ]
}

@app.route('/')
def index():
    return render_template('index.html', config=SITE_CONFIG)

if __name__ == '__main__':
    app.run(debug=True)

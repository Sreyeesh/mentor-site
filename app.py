from flask import Flask, render_template
import os

app = Flask(__name__)

# Site settings - easy to update content
SITE_CONFIG = {
    'name': 'Sreyeesh Garimella',
    'tagline': 'Mentoring & Coaching in Animation and Video Game Development',
    'email': 'toucan.sg@gmail.com',
    'calendly_link': 'https://calendly.com/toucan-sg/60min',
    'meta_description': 'One-on-one mentoring and coaching in animation and game development — practical guidance for your projects and career.',
    'focus_areas': [
        'Animation workflow & storytelling',
        'Game design fundamentals',
        'Career guidance in creative industries',
        'Portfolio and project feedback'
    ]
}

@app.route('/')
def index():
    return render_template('index.html', config=SITE_CONFIG)

if __name__ == '__main__':
    app.run(debug=True)

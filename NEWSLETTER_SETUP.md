# Newsletter Setup Guide

This guide explains how to set up the GDPR-compliant newsletter signup system for your Flask website.

## Features

- ✅ GDPR-compliant with explicit consent requirement
- ✅ Integration with open-source newsletter tools (Listmonk/Keila)
- ✅ Local database storage for audit trail
- ✅ Exit intent popup
- ✅ Analytics tracking (Matomo/GA4 compatible)
- ✅ Duplicate submission handling
- ✅ Production-ready error handling

## Quick Setup

### 1. Environment Configuration

Create a `.env` file in your project root with the following variables:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-change-this
FLASK_DEBUG=True
HOST=0.0.0.0
PORT=5000

# Database
DATABASE_URL=sqlite:///newsletter.db

# Newsletter Service Configuration
NEWSLETTER_SERVICE=listmonk

# Listmonk Configuration
LISTMONK_API_URL=http://localhost:9000
LISTMONK_API_KEY=your-listmonk-api-key
LISTMONK_LIST_ID=1

# Keila Configuration (alternative)
KEILA_API_URL=http://localhost:8080
KEILA_API_KEY=your-keila-api-key
KEILA_LIST_ID=1

# Site Configuration
BASE_PATH=
SITE_NAME=Sreyeesh Garimella
SITE_TAGLINE=Mentoring & Coaching in Animation and Video Game Development
SITE_EMAIL=toucan.sg@gmail.com
SITE_CALENDLY_LINK=https://calendly.com/toucan-sg/60min
SITE_META_DESCRIPTION=One-on-one mentoring and coaching in animation and game development — practical guidance for your projects and career.
SITE_FOCUS_AREAS=Animation workflow & storytelling,Game design fundamentals,Career guidance in creative industries,Portfolio and project feedback
```

### 2. Install Dependencies

```bash
pip install Flask-SQLAlchemy
```

### 3. Database Setup

The database will be created automatically when you first run the application. The system uses SQLite by default, but you can configure PostgreSQL by changing the `DATABASE_URL`.

### 4. Newsletter Service Setup

#### Option A: Listmonk (Recommended)

1. Install Listmonk using Docker:
```bash
docker run -p 9000:9000 -p 9001:9001 \
  -v listmonk_data:/app/data \
  listmonk/listmonk:latest
```

2. Access the admin panel at `http://localhost:9001`
3. Create a list and get your API key
4. Update your `.env` file with the API key and list ID

#### Option B: Keila

1. Install Keila using Docker:
```bash
docker run -p 8080:8080 \
  -e DATABASE_URL=postgresql://keila:keila@localhost/keila \
  ghcr.io/keila/keila:latest
```

2. Access the admin panel at `http://localhost:8080`
3. Create a list and get your API key
4. Update your `.env` file with the API key and list ID

## API Endpoint

The newsletter signup endpoint is available at `/api/newsletter`:

### Request Format

```json
{
  "email": "user@example.com",
  "consent": true,
  "source": "homepage"
}
```

### Response Format

Success:
```json
{
  "status": "success",
  "message": "Successfully subscribed! Check your email for confirmation."
}
```

Error:
```json
{
  "status": "error",
  "message": "Please enter a valid email address"
}
```

## Frontend Integration

The newsletter forms are already integrated into your `index.html`. The system includes:

1. **Main Newsletter Form**: Located in the newsletter section
2. **Exit Intent Popup**: Appears when users try to leave the page
3. **Analytics Tracking**: Automatically tracks form views, submissions, and errors

### Form Structure

```html
<form id="newsletter-form" class="newsletter-form">
    <div class="form-group">
        <label for="newsletter-email">Email Address</label>
        <input type="email" id="newsletter-email" name="email" required>
    </div>
    
    <div class="form-group">
        <label class="checkbox-label">
            <input type="checkbox" id="newsletter-consent" name="consent" required>
            I agree to receive newsletter updates and accept the 
            <a href="/privacy-policy" target="_blank">Privacy Policy</a>
        </label>
    </div>
    
    <button type="submit">Subscribe to Newsletter</button>
    <div id="newsletter-message" class="newsletter-message"></div>
</form>
```

## GDPR Compliance

The system is designed to be GDPR-compliant:

1. **Explicit Consent**: Users must check the consent checkbox
2. **Data Storage**: All signups are stored locally with timestamps
3. **Audit Trail**: Complete record of consent, source, and ESP responses
4. **No Direct Marketing**: Only forwards to newsletter service, doesn't send emails directly

## Analytics Events

The system automatically tracks these events:

- `form_view`: When newsletter forms are displayed
- `form_submit`: When users submit the form
- `submit_success`: When subscription is successful
- `submit_error`: When subscription fails

Events are compatible with:
- Matomo (`_paq.push()`)
- Google Analytics 4 (`gtag()`)

## Testing

### Test the API Endpoint

```bash
curl -X POST http://localhost:5000/api/newsletter \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "consent": true,
    "source": "homepage"
  }'
```

### Test Frontend Forms

1. Start your Flask application
2. Navigate to the homepage
3. Try submitting the newsletter form
4. Try leaving the page to trigger the exit intent popup

## Production Deployment

### Security Considerations

1. **Change the SECRET_KEY**: Use a strong, random secret key
2. **HTTPS**: Always use HTTPS in production
3. **API Keys**: Keep your newsletter service API keys secure
4. **Database**: Consider using PostgreSQL for production

### Environment Variables

Make sure to set these in production:
- `FLASK_DEBUG=False`
- `SECRET_KEY=<strong-random-key>`
- `DATABASE_URL=<production-database-url>`

### Monitoring

The system logs all newsletter signups to the database. You can monitor:
- Signup success/failure rates
- Consent rates
- Source attribution (homepage vs exit intent)
- ESP response times and errors

## Troubleshooting

### Common Issues

1. **Database not created**: Run the Flask app once to create tables
2. **API connection errors**: Check your newsletter service configuration
3. **Form not submitting**: Check browser console for JavaScript errors
4. **Styling issues**: Ensure CSS files are being served correctly

### Debug Mode

Enable debug mode to see detailed error messages:
```env
FLASK_DEBUG=True
```

## Support

For issues or questions:
1. Check the browser console for JavaScript errors
2. Check Flask application logs
3. Verify your environment configuration
4. Test the API endpoint directly with curl

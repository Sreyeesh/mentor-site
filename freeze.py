import os
import shutil
import re
from app import app

def fix_static_urls(html_content, base_path="/mentor-site"):
    """Fix static URLs in generated HTML for subdirectory deployment"""
    # Replace /static/ with /mentor-site/static/
    html_content = re.sub(r'="/static/', f'="{base_path}/static/', html_content)
    html_content = re.sub(r"='/static/", f"='{base_path}/static/", html_content)
    
    # Also fix any content="" attributes for Open Graph tags
    html_content = re.sub(r'content="/static/', f'content="{base_path}/static/', html_content)
    
    return html_content

if __name__ == '__main__':
    # Configure Flask for subdirectory deployment
    app.config['APPLICATION_ROOT'] = '/mentor-site'
    
    # Use BASE_PATH from environment if set (for GitHub Actions)
    base_path = os.getenv('BASE_PATH', '/mentor-site')
    
    # Create build directory
    build_dir = 'build'
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir)
    
    # Copy static files
    if os.path.exists('static'):
        shutil.copytree('static', os.path.join(build_dir, 'static'))
    
    # Generate HTML files using Flask with proper context
    with app.app_context():
        with app.test_request_context():
            with app.test_client() as client:
                # Get the main page
                response = client.get('/')
                html_content = response.data.decode('utf-8')
                
                # Fix static URLs for subdirectory deployment
                html_content = fix_static_urls(html_content, base_path)
                
                # Write to build directory
                with open(os.path.join(build_dir, 'index.html'), 'w', encoding='utf-8') as f:
                    f.write(html_content)

    # Ensure GitHub Pages serves files as-is (no Jekyll processing)
    with open(os.path.join(build_dir, '.nojekyll'), 'w') as f:
        f.write('')
    
    print("Static site generated in 'build' directory!")
    print("Files created:")
    for root, dirs, files in os.walk(build_dir):
        for file in files:
            print(f"  {os.path.join(root, file)}")
    
    # Verify the generated URLs
    with open(os.path.join(build_dir, 'index.html'), 'r') as f:
        content = f.read()
    
    print("\n=== URL Verification ===")
    static_urls = re.findall(r'(?:href|src|content)="([^"]*static[^"]*)"', content)
    if static_urls:
        print("Generated static URLs:")
        for url in static_urls[:5]:  # Show first 5 URLs
            if url.startswith('/mentor-site/'):
                print(f"  ✅ {url}")
            else:
                print(f"  ❌ {url} (should start with /mentor-site/)")
    else:
        print("  ⚠️  No static URLs found!")
    
    print(f"\nUsing base path: {base_path}")
    print("Ready for GitHub Pages deployment! 🚀")
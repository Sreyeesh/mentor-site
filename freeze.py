import os
import shutil
import re
from app import app

if __name__ == '__main__':
    # For custom domains, we don't need a base path
    # The site will be served from the root domain (toucan.ee)
    BASE_PATH = os.getenv('GITHUB_PAGES_BASE_PATH', '')
    
    # Create build directory
    build_dir = 'build'
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir)
    
    # Copy static files
    if os.path.exists('static'):
        shutil.copytree('static', os.path.join(build_dir, 'static'))
    
    # Generate HTML files using Flask test client
    with app.test_client() as client:
        # Routes to generate
        routes = ['/', '/contact', '/thank-you']
        
        for route in routes:
            try:
                print(f"Generating {route}...")
                response = client.get(route)
                
                if response.status_code != 200:
                    print(f"❌ Error: {route} returned status {response.status_code}")
                    continue
                
                html_content = response.data.decode('utf-8')
                
                # Debug: Check if we got the right content
                if route == '/contact' and 'contact-form-section' not in html_content:
                    print(f"❌ Warning: {route} doesn't contain contact form")
                
                # For custom domains, static files should be served from root paths
                # No need to modify the static file paths - they should remain as /static/
                
                # Determine filename
                if route == '/':
                    filename = 'index.html'
                else:
                    filename = route[1:] + '.html'  # Remove leading slash
                
                # Write to build directory
                filepath = os.path.join(build_dir, filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                print(f"✅ Generated {filename}")
                
            except Exception as e:
                print(f"❌ Error generating {route}: {e}")
                import traceback
                traceback.print_exc()
    
    # Ensure GitHub Pages serves files as-is (no Jekyll processing)
    with open(os.path.join(build_dir, '.nojekyll'), 'w') as f:
        f.write('')
    
    print(f"\nStatic site generated in 'build' directory for custom domain: toucan.ee")
    print("Files created:")
    for root, dirs, files in os.walk(build_dir):
        for file in files:
            print(f"  {os.path.join(root, file)}")
    
    print("\nReady for GitHub Pages deployment! 🚀")
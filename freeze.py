import os
import shutil
import re
from app import app

if __name__ == '__main__':
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
        # Get the main page
        response = client.get('/')
        html_content = response.data.decode('utf-8')
        
        # Simple and direct URL replacement
        html_content = html_content.replace('="/static/', '="./static/')
        html_content = html_content.replace("='/static/", "='./static/")
        html_content = html_content.replace('content="/static/', 'content="./static/')
        
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
        for url in static_urls[:5]:
            if url.startswith('./static/'):
                print(f"  ✅ {url}")
            else:
                print(f"  ❌ {url} (should start with ./static/)")
    else:
        print("  ⚠️  No static URLs found!")
    
    print("Ready for GitHub Pages deployment! 🚀")
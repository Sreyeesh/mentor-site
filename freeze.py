import os
import shutil
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
        
        # Write to build directory
        with open(os.path.join(build_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(response.data.decode('utf-8'))
    
    print("Static site generated in 'build' directory!")
    print("Files created:")
    for root, dirs, files in os.walk(build_dir):
        for file in files:
            print(f"  {os.path.join(root, file)}")

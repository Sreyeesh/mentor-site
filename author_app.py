import os

from authoring_app import create_app


app = create_app()


if __name__ == '__main__':
    host = os.getenv('AUTHORING_HOST', '0.0.0.0')
    port = int(os.getenv('AUTHORING_PORT', '5000'))
    debug = os.getenv('AUTHORING_DEBUG', 'true').lower() == 'true'
    app.run(host=host, port=port, debug=debug)

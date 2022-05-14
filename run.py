# Build-in modules
import os

# Local modules
from app.application import app

if __name__ == '__main__':
    """
    Run the application.
    """

    if 'CLOUD' not in os.environ:
        # If the application is running locally, use local IP settings
        app.run(host='0.0.0.0', port='8000', use_reloader=True)
    else:
        app.run()

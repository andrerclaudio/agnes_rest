# Local modules
from app.main import app

if __name__ == '__main__':
    """
    Run the application.
    """
    app.run(host='0.0.0.0', port='8000', use_reloader=True)

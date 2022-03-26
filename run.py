from app.main import app 
import logging


# Print in software terminal
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s | %(process)d | %(name)s | %(levelname)s:  %(message)s',
                    datefmt='%d/%b/%Y - %H:%M:%S')

logger = logging.getLogger(__name__)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=443, debug=True)
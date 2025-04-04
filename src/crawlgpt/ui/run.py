from src.crawlgpt.ui.app import app
import os

if __name__ == '__main__':
    env = os.environ.get('FLASK_ENV', 'development')
    debug = env == 'development'
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=debug, port=port, host='0.0.0.0')


#  python -m src.crawlgpt.ui.run
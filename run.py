import os
from src import app

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.config['SECRET_KEY'] = 'random'
    app.debug=True
    app.run('0.0.0.0', port=port)
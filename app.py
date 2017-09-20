import os
import sys
from src import app


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    print("Using:{}".format(os.environ['APP_SETTINGS']))
    app.debug=True if "-d" in sys.argv else False
    if "-t" in sys.argv:
        from flask_debugtoolbar import DebugToolbarExtension
        toolbar = DebugToolbarExtension(app)
    app.run('0.0.0.0', port=port)
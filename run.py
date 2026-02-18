import os
from app import create_app
from app.models import db  # Correctly import db from the models folder

# Initialize the app (Removed the argument causing the error)
app = create_app()

# Automated Table Creation for Render
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

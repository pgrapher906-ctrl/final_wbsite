import os
from app import create_app
from app.models import db  # Import db from the correct location

# Initialize the app (No arguments needed)
app = create_app()

# Automated Table Creation for Render
# (This ensures your database tables exist when the app starts)
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    # Get port from environment variable or use 10000 as default
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

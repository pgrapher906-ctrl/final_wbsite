from app import create_app

# Vercel looks for the 'app' variable to start the server
app = create_app()

if __name__ == "__main__":
    app.run()
  

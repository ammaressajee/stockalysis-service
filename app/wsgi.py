from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)  # This is for development, for production use Gunicorn or similar

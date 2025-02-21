from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)  # This will run the app on http://127.0.0.1:5000

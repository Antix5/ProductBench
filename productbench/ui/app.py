from flask import Flask, render_template

def create_app(leaderboard_data):
    """Creates and configures the Flask application."""
    app = Flask(__name__)

    @app.route('/')
    def index():
        """Renders the main leaderboard page."""
        return render_template('index.html', leaderboard=leaderboard_data)

    return app

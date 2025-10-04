import os

TOKEN = os.environ.get("TOKEN")  # Set in Render environment variables
WELCOME_MESSAGE = "Welcome to the group, {first_name} 👋"
BAD_WORDS = ["badword1", "badword2"]  # Add your list of banned words

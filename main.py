import threading
from bot import client, TOKEN
from api import app
import os

def run_discord_bot():
    client.run(TOKEN)

def services():
    discord_thread = threading.Thread(target=run_discord_bot, daemon=True)
    discord_thread.start()
    
    return app

application = services()

if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    app.run(host=host, port=port, debug=True)
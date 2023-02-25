import logging
logging.getLogger("urllib3").setLevel(logging.ERROR)

#IMPORT SETTINGS
import settings.Settings as Settings

#IMPORT SERVER APP
from api.ChatGPT_Server import app

if __name__ == '__main__':
    app.run(host=Settings.API_HOST, port=Settings.API_PORT, threaded=True)

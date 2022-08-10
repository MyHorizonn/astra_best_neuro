from flask import Flask
import os
from flask_config import Config

def create_app():
    
    app = Flask(__name__)
    
    # Загрузка конфигурации сервера
    app.config.from_object(Config)

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint)
    
    return app
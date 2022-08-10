import os
from flask import (
    request,
    jsonify,
    make_response
)
from werkzeug.utils import secure_filename
from flask_config import Config
from cv.run_cv import main
import json
from . import api

@api.route('/post_file', methods=['POST'])
def get_file():

    file = request.files['file']

    # Создание папки, если не существует
    if not os.path.exists(Config.MEDIA_FOLDER):
        os.makedirs(Config.MEDIA_FOLDER)
    
    # Сохранение файла
    try:
        filename = secure_filename(file.filename)
        file_path = os.path.join(Config.MEDIA_FOLDER, filename)
        file.save(file_path)
        # При debug_mode == True процесс обработки файла выводится в консоль 
        result = main(doc_path=file_path, debug_mode=False)
    except FileNotFoundError as e:    
        return make_response(jsonify({'msg': 'file not found'}), 400)

    return make_response(result, 200)

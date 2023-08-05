import datetime
import logging as rel_log
import os
import shutil
from datetime import timedelta
from flask import *
from processor.AIDetector_pytorch import Detector

import core.main

UPLOAD_FOLDER = r'F:\flaskProject2\back-end\uploads'

ALLOWED_EXTENSIONS = set(['png', 'jpg'])
# 创建flask应用实例
app = Flask(__name__)
app.secret_key = 'secret!'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 这两行代码创建了一个名为werkzeug_logger的日志记录器对象，并将其关联到Werkzeug库中的日志记录器。
# 然后，通过调用setLevel()方法将日志级别设置为ERROR,表示只记录错误级别的日志消息。
werkzeug_logger = rel_log.getLogger('werkzeug')
werkzeug_logger.setLevel(rel_log.ERROR)

# 解决缓存刷新问题
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)


# 添加header解决跨域
@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'POST'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-Requested-With'
    return response


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/')
def hello_world():
    return redirect(url_for('static', filename='./index.html'))


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    file = request.files['file']
    print(datetime.datetime.now(), file.filename)
    if file and allowed_file(file.filename):
        src_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(src_path)
        print(src_path)
        shutil.copy(src_path, 'F://flaskProject2//back-end//tmp//ct')
        image_path = os.path.join('F://flaskProject2//back-end//tmp//ct', file.filename)
        pid, image_info = core.main.c_main(
            image_path, current_app.model, file.filename.rsplit('.', 1)[1])
        print("pid:{}".format(pid))
        print(image_info)
        return jsonify({'status': 1,
                        'image_url': 'http://127.0.0.1:5000/tmp/ct/' + pid,
                        'draw_url': 'http://127.0.0.1:5000/tmp/draw/' + pid,
                        'image_info': image_info})

    return jsonify({'status': 0})


@app.route("/download", methods=['GET'])
def download_file():
    # 需要知道2个参数, 第1个参数是本地目录的path, 第2个参数是文件名(带扩展名)
    return send_from_directory('data', 'testfile.zip', as_attachment=True)


# show photo
@app.route('/tmp/<path:file>', methods=['GET'])
def show_photo(file):
    if request.method == 'GET':
        if not file is None:
            image_data = open(f'tmp/{file}', "rb").read()
            response = make_response(image_data)
            response.headers['Content-Type'] = 'image/png'
            return response


if __name__ == '__main__':
    print('------------------------')
    files = [
        'uploads', 'tmp/ct', 'tmp/draw',
        'tmp/image', 'tmp/mask', 'tmp/uploads'
    ]
    for ff in files:
        if not os.path.exists(ff):
            os.makedirs(ff)

    with app.app_context():
        print('进来实例化')
        current_app.model = Detector()
        print('实例化成功')
    app.run(host='127.0.0.1', port=5000, debug=True)

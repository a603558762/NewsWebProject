from flask import Flask


app = Flask(__name__)


@app.route('/')
def index():
    return '欢迎到光临!!'


if __name__ == '__main__':
    app.run()
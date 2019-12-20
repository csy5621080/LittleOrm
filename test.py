from flask import Flask
from base import Person

app = Flask(__name__)


@app.route('/')
def index():
    p = Person().query.filter(id=1).first().execute()
    result = p.one().id
    return str(result)


if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0', 8888)
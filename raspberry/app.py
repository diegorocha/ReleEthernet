from datetime import timedelta, datetime

from flask import Flask, render_template
from flask.json import jsonify

from pi import ReleInterface

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/api/rele')
@app.route('/api/rele/<action>', methods=['POST'])
def api(action=''):
    rele = ReleInterface()
    error = ''
    if action:
        try:
            getattr(rele, action)()
        except:
            error = 'Não foi possível executar a operação'
    return jsonify({'rele': rele.is_on, 'error': error})


@app.route("/0", defaults={'command': '?'})
@app.route("/0<command>")
def api_compatibilidade(command):
    command_map = {'0': 'off', '1': 'on', '!': 'toggle', '?': ''}
    action = command_map.get(command)
    return api(action)


@app.after_request
def set_cache_headers(response):
    default_max_age = 3600
    if app.debug:
        response.cache_control.max_age = 0
    if response.cache_control.max_age == 0:
        response.cache_control.no_cache = True
        response.cache_control.no_store = True
        response.cache_control.must_revalidate = True
    elif response.cache_control.max_age is None:
        response.cache_control.max_age = default_max_age
    if not response.expires:
        response.expires = datetime.utcnow() + timedelta(seconds=response.cache_control.max_age)
    return response


if __name__ == "__main__":
    app.run(host='0.0.0.0')

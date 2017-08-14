from flask import Flask
from flask.json import jsonify

from pi import ReleInterface

app = Flask(__name__)


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

if __name__ == "__main__":
    app.run(host='0.0.0.0')

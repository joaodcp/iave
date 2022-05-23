from flask import Flask, make_response, jsonify
from services import scraper, gtsearch
app = Flask(__name__)

app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

@app.route('/api/obterProvas/<tipo>/<ano>/<epocic>', methods=['GET'])
def returnProvas(tipo, ano, epocic):
    res = make_response(jsonify(scraper.scrapeIAVE(tipo, ano, epocic)))
    return res
 
@app.route('/api/globalTextSearch/<filtered>', methods=['GET'])
def returnResults(filtered):
    return 'textResults'

@app.errorhandler(404)
def not_found_error(error):
    return "<h1>404 Ficheiro não encontrado</h1><p>A página ou recurso que procura não foi encontrada.<br>Se escreveu o URL manualmente, verifique-o.</p>"

if __name__ == "__main__":
   app.run()
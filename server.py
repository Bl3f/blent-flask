from datetime import timedelta
from flask import Flask, request, jsonify
import joblib

app = Flask(__name__)

cart = [{
    'id': "je8zng",
    'quantity': 3
}]


def check_fields(body, fields):
    # On récupère les champs requis au format 'ensemble'
    required_parameters_set = set(fields)
    # On récupère les champs du corps de la requête au format 'ensemble'
    fields_set = set(body.keys())
    # Si l'ensemble des champs requis n'est pas inclut dans l'ensemble des champs du corps de la requête
    # Alors s'il manque des paramètres et la valeur False sera renvoyée
    return required_parameters_set <= fields_set


@app.route('/')
def hello_world():
    return "Coucou !"


@app.route('/cart', methods=['GET'])
def list_cart():
    return jsonify(cart), 200


@app.route('/cart', methods=['POST'])
def add_to_cart():
    try:
        body = request.get_json()
        if not check_fields(body, {'id', 'quantity'}):
            # S'il manque un paramètre on retourne une erreur 400
            return jsonify({'error': "Missing fields."}), 400

        # On vérifie si le produit n'existe pas déjà
        for i, item in enumerate(cart):
            if item['id'] == body.get('id', ""):
                # On a retrouvé ce produit dans le panier, on ajoute à la quantité existante
                cart[i]['quantity'] += int(body.get('quantity', 0))
                # On retourne un code 200 pour signaler que tout s'est bien passé
                return jsonify({}), 200

        # Si l'on atteint cette partie, alors le produit n'existait pas déjà
        cart.append(body)
        return jsonify({}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/cart', methods=['PATCH'])
def edit_cart():
    try:
        body = request.get_json()
        if not check_fields(body, {'id', 'quantity'}):
            # S'il manque un paramètre on retourne une erreur 400
            return jsonify({'error': "Missing fields."}), 400

        for i, item in enumerate(cart):
            if item['id'] == body.get('id', ""):
                # On met à jour la quantité
                cart[i]['quantity'] = int(body.get('quantity', 0))
                return jsonify({}), 200

        # Si l'on atteint cette partie, alors le produit n'existait pas : on ne peut pas mettre à jour !
        return jsonify({'error': "Product not found."}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/cart', methods=['DELETE'])
def remove_from_cart():
    try:
        body = request.get_json()
        if not check_fields(body, {'id'}):
            # S'il manque un paramètre on retourne une erreur 400
            return jsonify({'error': "Missing fields."}), 400

        for i, item in enumerate(cart):
            if item['id'] == body['id']:
                # On supprime le produit du panier
                del cart[i]
                return jsonify({}), 200

        # Si l'on atteint cette partie, alors le produit n'existait pas : on ne peut pas supprimer !
        return jsonify({'error': "Product not found."}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# To dump
# rf = RandomForestRegressor(n_estimators=n_estimators, max_depth=max_depth)
# joblib.dump(rf, "model_rfr.bin")

model = joblib.load("model_rfr.bin")


@app.route('/predict', methods=['POST'])
def predict():
    body = request.get_json()
    features = body.get("features")
    prediction = model.predict([features])

    return "{}".format(str(timedelta(seconds=prediction[0])))

# requests.post("http://127.0.0.1:5000/predict", json={"features": [1, 2, 3, 4, 5, 6]}, headers=headers).content
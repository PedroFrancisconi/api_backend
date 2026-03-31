from flask import Flask, jsonify, request, render_template
import random
import firebase_admin
from firebase_admin import credentials, firestore
from auth import gerar_token, token_obrigatorio
from flask_cors import CORS
import os
from dotenv import load_dotenv
import json
load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
CORS(app, origins=["*"])

ADM_USUARIO = os.getenv("ADM_USUARIO")
ADM_SENHA = os.getenv("ADM_SENHA")

if os.getenv("VERCEL"):
    #ONLINE NA VERCEL
    cred = credentials.Certificate(json.loads(os.getenv("FIREBASE_CREDENTIALS")))
else:
    #LOCAL
    cred = credentials.Certificate("firebase.json")

firebase_admin.initialize_app(cred)


db = firestore.client()

TOKEN_API = "1234567890"


@app.route('/', methods=['GET'])
def root():
    return jsonify({
        "api": "Charadas",
        "version": "1.0",
        "author": "Pedro"
    })

#rota login

@app.route("/login", methods=['POST'])
def login():
    dados = request.get_json()
    
    if not dados:
        return jsonify({"Error": "Dados incompletos"}), 400
    
    usuario = dados.get("usuario")
    senha = dados.get("senha")

    if not usuario or not senha:
        return jsonify({"Error": "Dados incompletos"}), 400
    
    if usuario == ADM_USUARIO and senha == ADM_SENHA:
        token = gerar_token(usuario)
        return jsonify({
            "message": "Login bem-sucedido",
            "token": token
        }), 200

    return jsonify({"Error": "Credenciais inválidas"}), 401

@app.route("/charadas", methods=['GET'])
def get_charadas():
    charadas = []
    lista = db.collection("charadas").stream()

    for item in lista:
        charadas.append(item.to_dict())

    return jsonify(charadas), 


@app.route("/charadas/aleatorias", methods=['GET'])
def get_charada_random():
    charadas = []
    lista = db.collection("charadas").stream()

    for item in lista:
        charadas.append(item.to_dict())
    
    return jsonify(random.choice(charadas)), 200


#Rota 3 - método get para buscar charada por id
@app.route("/charadas/<int:id>", methods=['GET'])
def get_charada_by_id(id):
    lista = db.collection("charadas").where("id", "==", id).stream()
    for item in lista:
        return jsonify(item.to_dict()), 200
    return jsonify({"Error": "Charada não encontrada"}), 404


#Rota 4 - Método post para criar charada
@app.route("/charadas", methods=['POST'])
@token_obrigatorio
def create_charada():

    dados = request.get_json()
    # Lógica para criar a charada no Firestore
    if not dados or not "pergunta" in dados or not "resposta" in dados:
        return jsonify({"Error": "Dados incompletos"}), 400
    try:
        #busca pelo novo contador
        contador_ref = db.collection("contador").document("controle_id")
        contador_doc = contador_ref.get()
        ultimo_id = contador_doc.to_dict().get("ultimo_id")
        #somar 1 ao ultimo id
        novo_id = ultimo_id + 1
        #atualizar o id do contador
        contador_ref.update({"ultimo_id": novo_id})

        #Cadastrar a nova charada
        db.collection("charadas").add({
            "id": novo_id,
            "pergunta": dados["pergunta"],
            "resposta": dados["resposta"]
        })

        return jsonify({"Message": "Charada criada com sucesso"}), 201
    except:
        return jsonify({"Error": "Falha em enviar a charada"}), 400

#Rota 5 - Método PUT - alteração total
@app.route("/charadas/<int:id>", methods=['PUT'])
@token_obrigatorio
def update_charada(id):
    
    dados = request.get_json()
    #PUT - É necessário enviar PERGUNTA e RESPOSTA
    if not dados or not "pergunta" in dados or not "resposta" in dados:
        return jsonify({"Error": "Dados incompletos"}), 400
    
    try:
        docs = db.collection("charadas").where("id", "==", id).limit(1).get()
        if not docs:
            return jsonify({"Error": "Charada não encontrada"}), 404
        
        #Pega o primeiro e unico documento da lista
        for doc in docs:
            doc_ref = db.collection("charadas").document(doc.id)
            doc_ref.update({
                "pergunta": dados["pergunta"],
                "resposta": dados["resposta"]
            })

        return jsonify({"Message": "Charada atualizada com sucesso"}), 200
    except:
        return jsonify({"Error": "Falha em atualizar a charada"}), 400
    
#Rota 6 - Método PATCH - alteração parcial
@app.route("/charadas/<int:id>", methods=['PATCH'])
@token_obrigatorio
def charadas_patch(id):

    
    dados = request.get_json()
    #PATCH - É necessário enviar PERGUNTA e RESPOSTA
    if not dados or ("pergunta" not in dados and "resposta" not in dados):
        return jsonify({"Error": "Dados incompletos"}), 400
    
    try:
        docs = db.collection("charadas").where("id", "==", id).limit(1).get()
        if not docs:
            return jsonify({"Error": "Charada não encontrada"}), 404
        
        #Pega o primeiro e unico documento da lista
        for doc in docs:
            doc_ref = db.collection("charadas").document(doc[0].id)
            update_charada = {}
            if "pergunta" in dados:
                update_charada["pergunta"] = dados["pergunta"]
            if "resposta" in dados:
                update_charada["resposta"] = dados["resposta"]
            doc_ref.update(update_charada)

        return jsonify({"message": "Charada atualizada com sucesso"}), 200
    except:
        return jsonify({"error": "Falha em atualizar a charada"}), 400


#Rota 7 - Método DELETE - deletar charada
@app.route("/charadas/<int:id>", methods=['DELETE'])
@token_obrigatorio
def delete_charada(id):
    
    docs = db.collection("charadas").where("id", "==", id).limit(1).get()
    if not docs:
        return jsonify({"Error": "Charada não encontrada"}), 404
        
    doc_ref = db.collection("charadas").document(docs[0].id)
    doc_ref.delete()
    return jsonify({"message": "Charada excluida com sucesso"}), 200


#tratamento de erros
@app.errorhandler(500)
def erro500(error):
    return jsonify({"Error": "Erro interno do servidor"}), 500

if __name__ == "__main__":
    app.run(debug=True) # Adicione o port=5500 aqui
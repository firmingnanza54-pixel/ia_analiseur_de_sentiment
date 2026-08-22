from flask import Flask, jsonify, render_template, request
from ceveau3 import Reseau_de_neuronne, x_train, cree_vocabulaire, vectoriser_phrase
import json
from supabase import create_client, Client

app = Flask(__name__)

ia = Reseau_de_neuronne(taille_entre=len(x_train[0]), taille_cache=10, taille_sortie=1)




supabase_url = 'https://qkfpshnuzbfqwdlcxfru.supabase.co'
supabase_key = 'sb_publishable_JPicoM76nsqg0mQDMa_CDA_O6u3h-Sg'
supabase: Client = create_client(supabase_url, supabase_key)

with open("/home/gnanza/projet_ia/pojet_ia_comm/prosauvegarde_cerveau2.json", "r") as f:
    cerveau = json.load(f)

ia.charger(cerveau)



@app.route("/")
def acceuil():
    return render_template('index.html')

@app.route('/prediction', methods=['POST'])
def predire():
    donnees = request.get_json()  
    phrase = donnees.get('phrase', '')

    vecteur = vectoriser_phrase(phrase, ia.vocab)

    predire_val = ia.forward(vecteur)
    resultat = predire_val[0]

    if resultat > 0.5:
        reponse = "Resultat positif 😀 "
        certitude = resultat
    else:
        reponse = "Resultat negatif 🙁 "
        certitude = 1 - resultat

    return jsonify({"reponse": reponse, "certitude": certitude * 100})

@app.route('/ajouter_une_nouvel_phrase', methods=['POST'])
def ajouter_une_phrase():
    donnees = request.get_json()
    phrase = donnees.get('phrase')
    cible = donnees.get('cible')

    if phrase and cible is not None:
        supabase.table('donnees_ia').insert({
            "phrase": phrase,
            "cible": cible
        }).execute()
        return jsonify({"statut": "success", "message": "Phrase sauvegardée !"}), 200

    return jsonify({"statut": "erreur", "message": "Données invalides"}), 400



if __name__ == "__main__":
    app.run(debug=True, port=5000)
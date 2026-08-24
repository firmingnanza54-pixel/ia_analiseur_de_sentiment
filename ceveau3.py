import random
import math
import json
import pickle
from supabase import client, create_client

supabase_url = 'https://qkfpshnuzbfqwdlcxfru.supabase.co'
supabase_key = 'sb_publishable_JPicoM76nsqg0mQDMa_CDA_O6u3h-Sg'

supabase: client = create_client(supabase_url, supabase_key)

res= supabase.table('donnees_ia').select('phrase, cible').execute()

phrase = [item['phrase'] for item in res.data]

recu = [item['cible'] for item in res.data]

print(f"{len(phrase)} phrases récupérées depuis le cloud pour le réentraînement !")

label = [int(je) for je in recu]


def cree_vocabulaire(phrase):
    tous_les_mots= []
    for x in phrase:
        mot= x.lower().split()
        for mots in mot:
            tous_les_mots.append(mots)
    vocabulaire= list(set(tous_les_mots))
    return vocabulaire
        
def vectoriser_phrase(phrase, vocabulaire):
    phrase = phrase.lower().split()
    vecteur= [0] * len(vocabulaire)

    for x in phrase:
        for index, i in enumerate(vocabulaire):
            if i == x:
                vecteur[index]= 1
    return vecteur

vocab= cree_vocabulaire(phrase)

x_train= [vectoriser_phrase(p, vocab) for p in phrase]
y_train= label


         

def sigmoide(x):
    return 1 / (1 + math.exp(-x))

def deriv_sigmoide(x):
    return x * (1 - x)

class Reseau_de_neuronne:
    def __init__(self, taille_entre, taille_cache, taille_sortie):
        self.taille_entre = taille_entre
        self.taille_cache = taille_cache
        self.taille_sortie = taille_sortie

        # Initialisation aléatoire des poids et biais
        self.poid_cache = [[random.uniform(-1, 1) for _ in range(taille_cache)] for _ in range(taille_entre)]
        self.biais_cache = [random.uniform(-1, 1) for _ in range(taille_cache)]

        self.poid_sortie = [[random.uniform(-1, 1) for _ in range(taille_sortie)] for _ in range(taille_cache)]
        self.biais_sortie = [random.uniform(-1, 1) for _ in range(taille_sortie)]

    def sauvegade(self, vocab):
        return{
            "vocabulaire": vocab,
            "taille_entre": self.taille_entre,
            "taille_cache": self.taille_cache,
            "taille_sortie": self.taille_sortie,
            "poid_cache": self.poid_cache,
            "biais_cache": self.biais_cache,
            "poid_sortie": self.poid_sortie ,
            "biais_sortie": self.biais_sortie
        }

    def charger(self, sauvegarde):
        self.vocab= sauvegarde["vocabulaire"]
        self.taille_entre= sauvegarde["taille_entre"]
        self.taille_cache= sauvegarde["taille_cache"]
        self.taille_sortie= sauvegarde["taille_sortie"]
        self.poid_cache= sauvegarde["poid_cache"]
        self.biais_cache= sauvegarde["biais_cache"]
        self.poid_sortie= sauvegarde["poid_sortie"]
        self.biais_sortie= sauvegarde["biais_sortie"]

    def forward(self, x):
        self.sortie_cache = []
        
        # 1. Couche cachée
        for j in range(self.taille_cache):
            score = 0
            for i in range(self.taille_entre):
                score += x[i] * self.poid_cache[i][j]
            score += self.biais_cache[j]
            self.sortie_cache.append(sigmoide(score))

        # 2. Couche de sortie
        self.prediction = []
        for g in range(self.taille_sortie):
            score_sortie = 0
            for h in range(self.taille_cache):
                score_sortie += self.sortie_cache[h] * self.poid_sortie[h][g]
            score_sortie += self.biais_sortie[g]
            self.prediction.append(sigmoide(score_sortie))

        return self.prediction

    def backward(self, pred, cible, lr, x):
        # 1. Gradient de sortie
        gradient_sortie = (cible - pred) * deriv_sigmoide(pred)

        # 2. Gradient couche cachée
        gradient_cache = []
        for i in range(self.taille_cache):
            j = gradient_sortie * self.poid_sortie[i][0] * deriv_sigmoide(self.sortie_cache[i]) 
            gradient_cache.append(j)

        # 3. Mise à jour poids et biais de sortie
        for k in range(self.taille_cache):
            self.poid_sortie[k][0] += lr * gradient_sortie * self.sortie_cache[k]
        self.biais_sortie[0] += lr * gradient_sortie

        # 4. Mise à jour poids et biais cachés
        for l in range(self.taille_entre):       
            for m in range(self.taille_cache):   
                self.poid_cache[l][m] += lr * gradient_cache[m] * x[l]
        
        for m in range(self.taille_cache):
            self.biais_cache[m] += lr * gradient_cache[m]

    def train(self, epoques, lr, x_train, y_train):
        for epoque in range(epoques):
            erreur_totale = 0
            
            for i in range(len(x_train)):
                x = x_train[i]
                cible = y_train[i]

                predictions = self.forward(x)
                pred = predictions[0]

                erreur_totale += abs(cible - pred)

                self.backward(pred, cible, lr, x)
   
            if epoque % 5000 == 0:
                erreur_moyenne = erreur_totale / len(x_train)
                print(f"Époque {epoque} - Erreur moyenne : {erreur_moyenne:.4f}")
if __name__ == "__main__":

    XOR = Reseau_de_neuronne(taille_entre = len(x_train[0]), taille_cache=10, taille_sortie= 1)

    print("------- DEBUT DE L'ENRAINEMENT---------")

    XOR.train(epoques= 30000, lr= 0.5, x_train=x_train, y_train=y_train)

    print("\n--- Résultats après entraînement ---")
    for i in range(len(x_train)):
        x = x_train[i] 
        pred = XOR.forward(x)[0]
        print(f"Entrée {x} -> Prédiction : {pred:.4f} (Attendu : {y_train[i]})")

    cerveau= {}

    cerveau = XOR.sauvegade(vocab)

    with open ('prosauvegarde_cerveau2.json', "w") as f:
        json.dump(cerveau , f, indent = 4)

    

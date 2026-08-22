function prediction() {
    let receuilir = document.getElementById("zone_de_saisie").value.trim();

    
    if (!receuilir) {
        document.getElementById("reponse").innerText = "Veuillez d'abord saisir une phrase.";
        return;
    }

    document.getElementById('reponse').innerText = 'Calcul en cours...';
    
    fetch("/prediction", {
        method: 'POST',
        headers: {
            'content-type': 'application/json'
        },
        body: JSON.stringify({'phrase': receuilir})
    })
    .then(reponse => reponse.json())
    .then(data => {
        document.getElementById('reponse').innerText = data.reponse + " (certitude: " + data.certitude.toFixed(1) + "%)";
    })
    .catch(error => {
        console.error("Erreur: ", error);
        document.getElementById('reponse').innerText = "Une erreur s'est produite pendant le calcul";
    }); 
}

function Effacer() {
    
    document.getElementById("zone_de_saisie").value = '';
    document.getElementById("reponse").innerText = '';
    if (document.getElementById("envoi")) {
        document.getElementById("envoi").innerText = '';
    }
}

function envoyer() {
    let receuilir = document.getElementById("zone_de_saisie").value.trim();

    if (!receuilir) {
        document.getElementById("envoi").innerText = "Veuillez d'abord saisir une phrase.";
        return;
    }

    let choix = document.querySelector('input[name="verdict"]:checked').value;
    let reponseTxt = document.getElementById('reponse').innerText;
    let envoie = 0;

    if (choix == "1") {
        if (reponseTxt.includes("Resultat positif 😀")) {
            envoie = 1;
        } else {
            envoie = 0;
        }
    } else {
        if (reponseTxt.includes("Resultat negatif 🙁")) {
            envoie = 1;
        } else {
            envoie = 0;
        }
    }

    fetch('/ajouter_une_nouvel_phrase', {
        method: 'POST', 
        headers: {
            'content-type': 'application/json'
        },
        body: JSON.stringify({"phrase": receuilir, "cible": envoie}) 
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("envoi").innerText = "Phrase envoyée avec succès !";
    })
    .catch(error => {
        console.error("Erreur", error);
        document.getElementById("envoi").innerText = "Une erreur s'est produite pendant l'envoi";
    });
}
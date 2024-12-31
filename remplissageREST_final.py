from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import httpx
from fastapi import Request
from typing import List, Optional
import psycopg2
import psycopg2.extras
import random
import datetime

app = FastAPI()

DB_URL = "postgresql://logementdb_owner:yTfuDP2s8iBM@ep-black-art-a2hjm7sg.eu-central-1.aws.neon.tech/logementdb?sslmode=require"

templates = Jinja2Templates(directory="templates")

# Création des classes
class Mesure(BaseModel):
    capteur_id: int
    valeur: float


class Facture(BaseModel):
    logement_id: int
    type_facture: str
    montant: float
    valeur: float

class Logement(BaseModel):
    id : int
    adresse: str
    adresse_ip: str
    telephone: str

class Piece(BaseModel):
    id : int
    logement_id : int
    nom : str
    localisation1: float
    localisation2: float
    localisation3: float

class CapteurActionneur(BaseModel):
    cap_type: str
    ref_comm: str
    ref_piece: int
    port_com: int


class RandomRequest(BaseModel):
    num: int = 5


#  Fonctions pour psycopg2, les random date (obsolète, pour les tests) et les types de facture
def get_db_connection():
    conn = psycopg2.connect(DB_URL, cursor_factory=psycopg2.extras.RealDictCursor)
    return conn


def date_random(start_date, end_date):
    start_timestamp = int(start_date.timestamp())
    end_timestamp = int(end_date.timestamp())
    random_timestamp = random.randint(start_timestamp, end_timestamp)
    return datetime.datetime.fromtimestamp(random_timestamp)


def prise_id_factures(type_name):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM Type_Facture WHERE Fac_Type = %s", (type_name,))
    result = c.fetchone()
    conn.close()
    return result["id"] if result else None


# Tous les GET
# Le template des get, post, put et delete a été créé en collaboration avec chat GPT
# je remercie également la chaîne "Bande de Codeur" pour leurs vidéos explicatives

@app.get("/logements", response_model=List[dict])
async def get_logements():
    """Récupérer tous les logements."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM Logement")
    logements = [dict(row) for row in c.fetchall()]
    conn.close()
    return logements

@app.get("/pieces", response_model=List[dict])
async def get_pieces():
    """Récupérer toutes les pièces dans la base."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM Piece")
    pieces = [dict(row) for row in c.fetchall()]
    conn.close()
    return pieces

@app.get("/mesures", response_model=List[dict])
async def get_mesures():
    """Récupérer toutes les mesures dans la base."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM Mesure")
    mesures = c.fetchall()
    conn.close()
    return mesures

@app.get("/capteurs_actionneurs", response_model=List[dict])
async def get_capteurs_actionneurs():
    """Récupérer tous les capteurs/actionneurs."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM Capteur_Actionneur")
    capteurs_actionneurs = [dict(row) for row in c.fetchall()]
    conn.close()
    return capteurs_actionneurs

@app.get("/factures", response_model=List[dict])
async def get_factures():
    """Récupérer toutes les factures dans la base."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM Facture")
    factures = c.fetchall()
    conn.close()
    return factures

# à changer, marchait jeudi ----- UPDATE, plus besoin, mais inutile parce que jamais utilisée
@app.get("/meteo/{ville}", response_class=HTMLResponse)
async def previsions_meteo(ville: str, request: Request):
    """
    Récupérer les prévisions météo pour les 5 prochains jours en utilisant wttr.in.
    """
    try:
        url = f"https://wttr.in/{ville}?format=v2&lang=fr&format=%l:+%c+%t"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()

        meteo_data = response.text
        return templates.TemplateResponse(
            "meteo.html",
            {"request": request, "ville": ville.capitalize(), "meteo_data": meteo_data.splitlines()},
        )

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des données météo : {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur inattendue : {e}")


# Tous les POST
@app.post("/logements", response_model=dict)
async def add_logement(logement: Logement):
    """Ajouter un nouveau logement."""
    conn = get_db_connection()
    c = conn.cursor()

    try:
        c.execute('''
            INSERT INTO Logement (Adresse, AdresseIP, Telephone)
            VALUES (%s, %s, %s)
        ''', (logement.adresse, logement.adresse_ip, logement.telephone))
        conn.commit()
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur SQL : {e}")
    finally:
        conn.close()

    return {"message": "Logement ajouté avec succès"}

@app.post("/pieces", response_model=dict)
async def add_piece(piece: Piece):
    """Ajouter une nouvelle pièce."""
    conn = get_db_connection()
    c = conn.cursor()

    try:
        # Vérification si le logement associé existe
        c.execute("SELECT id FROM Logement WHERE id = %s", (piece.logement_id,))
        logement = c.fetchone()
        if not logement:
            raise HTTPException(status_code=404, detail=f"Logement avec id {piece.logement_id} introuvable.")

        # Insertion de la pièce
        c.execute('''
            INSERT INTO Piece (Nom, Logement_id, Localisation1, Localisation2, Localisation3)
            VALUES (%s, %s, %s, %s, %s)
        ''', (piece.nom, piece.logement_id, piece.localisation1, piece.localisation2, piece.localisation3))
        conn.commit()
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Contrainte violée : {e}")
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur SQL : {e}")
    finally:
        conn.close()

    return {"message": "Pièce ajoutée avec succès"}

@app.post("/mesures", response_model=dict)
async def add_mesure(mesure: Mesure):
    """Ajouter une nouvelle mesure."""
    conn = get_db_connection()
    c = conn.cursor()

    try:
        c.execute(
            """
            INSERT INTO Mesure (Capteur_Actionneur_id, Valeur)
            VALUES (%s, %s)
            """,
            (mesure.capteur_id, mesure.valeur),
        )
        conn.commit()
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur SQL : {e}")
    finally:
        conn.close()

    return {"message": "Mesure ajoutée avec succès"}


@app.post("/factures", response_model=dict)
async def add_facture(facture: Facture):
    """Ajouter une nouvelle facture."""
    type_facture_id = prise_id_factures(facture.type_facture)
    if not type_facture_id:
        raise HTTPException(
            status_code=404, detail=f"Type de facture '{facture.type_facture}' introuvable"
        )

    conn = get_db_connection()
    c = conn.cursor()

    try:
        c.execute(
            """
            INSERT INTO Facture (Logement_id, Type_Facture_id, Valeur, Montant)
            VALUES (%s, %s, %s, %s)
            """,
            (facture.logement_id, type_facture_id, facture.valeur, facture.montant),
        )
        conn.commit()
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur SQL : {e}")
    finally:
        conn.close()

    return {"message": "Facture ajoutée avec succès"}

@app.post("/capteurs_actionneurs", response_model=dict)
async def add_capteur_actionneur(capteur: CapteurActionneur):
    """Ajouter un nouveau capteur/actionneur."""
    conn = get_db_connection()
    c = conn.cursor()

    try:
        c.execute("SELECT id FROM Piece WHERE id = %s", (capteur.ref_piece,))
        piece = c.fetchone()
        if not piece:
            raise HTTPException(status_code=404, detail=f"Pièce avec id {capteur.ref_piece} introuvable.")

        c.execute('''
            INSERT INTO Capteur_Actionneur (Cap_Type, RefComm, RefPiece, PortCom)
            VALUES (%s, %s, %s, %s)
        ''', (capteur.cap_type, capteur.ref_comm, capteur.ref_piece, capteur.port_com))
        conn.commit()
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Contrainte violée : {e}")
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Erreur SQL : {e}")
    finally:
        conn.close()

    return {"message": "Capteur/actionneur ajouté avec succès"}

# Random pour les test (à supp?)
@app.post("/mesures/random", response_model=dict)
async def add_random_mesures(request: RandomRequest):
    """Ajouter des mesures aléatoires pour tous les capteurs."""
    num_mesures = request.num
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM Capteur_Actionneur")
    capteurs = c.fetchall()

    for capteur in capteurs:
        for _ in range(num_mesures):
            if capteur["id"] == 1:  # Température
                valeur = round(random.uniform(15.0, 25.0), 1)
            elif capteur["id"] == 2:  # Humidité
                valeur = round(random.uniform(35.0, 65.0), 1)
            else:
                valeur = random.randint(0, 1)

            c.execute(
                """
                INSERT INTO Mesure (Capteur_Actionneur_id, Valeur)
                VALUES (%s, %s)
                """,
                (capteur["id"], valeur),
            )

    conn.commit()
    conn.close()

    return {"message": f"{num_mesures} mesures aléatoires ajoutées pour chaque capteur"}


@app.post("/factures/random", response_model=dict)
async def add_random_factures(request: RandomRequest):
    """Ajouter des factures aléatoires pour tous les logements."""
    num_factures = request.num
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM Logement")
    logements = c.fetchall()

    for logement in logements:
        for _ in range(num_factures):
            type_facture = random.choice(["Eau", "Electricité", "Internet"])
            type_facture_id = prise_id_factures(type_facture)

            montant = round(random.uniform(0.0, 500.0), 2)
            valeur = round(random.uniform(0.0, 300.0), 2)

            c.execute(
                """
                INSERT INTO Facture (Logement_id, Type_Facture_id, Valeur, Montant)
                VALUES (%s, %s, %s, %s)
                """,
                (logement["id"], type_facture_id, valeur, montant),
            )

    conn.commit()
    conn.close()

    return {"message": f"{num_factures} factures aléatoires ajoutées pour chaque logement"}

#Tous les PUT
@app.put("/logements/{logement_id}", response_model=dict)
async def update_logement(logement_id: int, updated_logement: Logement):
    """Mettre à jour un logement existant."""
    conn = get_db_connection()
    c = conn.cursor()

    try:
        c.execute(
            """
            UPDATE Logement
            SET Adresse = %s, AdresseIP = %s, Telephone = %s
            WHERE id = %s
            """,
            (updated_logement.adresse, updated_logement.adresse_ip, updated_logement.telephone, logement_id),
        )
        if c.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Logement avec id {logement_id} introuvable.")
        conn.commit()
    finally:
        conn.close()

    return {"message": "Logement mis à jour avec succès"}

@app.put("/pieces/{piece_id}", response_model=dict)
async def update_piece(piece_id: int, updated_piece: Piece):
    """Mettre à jour une pièce existante."""
    conn = get_db_connection()
    c = conn.cursor()

    try:
        c.execute(
            """
            UPDATE Piece
            SET Nom = %s, Logement_id = %s, Localisation1 = %s, Localisation2 = %s, Localisation3 = %s
            WHERE id = %s
            """,
            (
                updated_piece.nom,
                updated_piece.logement_id,
                updated_piece.localisation1,
                updated_piece.localisation2,
                updated_piece.localisation3,
                piece_id,
            ),
        )
        if c.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Pièce avec id {piece_id} introuvable.")
        conn.commit()
    finally:
        conn.close()

    return {"message": "Pièce mise à jour avec succès"}

@app.put("/capteurs_actionneurs/{capteur_id}", response_model=dict)
async def update_capteur_actionneur(capteur_id: int, updated_capteur: CapteurActionneur):
    """Mettre à jour un capteur/actionneur existant."""
    conn = get_db_connection()
    c = conn.cursor()

    try:
        c.execute(
            """
            UPDATE Capteur_Actionneur
            SET Cap_Type = %s, RefComm = %s, RefPiece = %s, PortCom = %s
            WHERE id = %s
            """,
            (
                updated_capteur.cap_type,
                updated_capteur.ref_comm,
                updated_capteur.ref_piece,
                updated_capteur.port_com,
                capteur_id,
            ),
        )
        if c.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Capteur/actionneur avec id {capteur_id} introuvable.")
        conn.commit()
    finally:
        conn.close()

    return {"message": "Capteur/actionneur mis à jour avec succès"}

@app.put("/mesures/{mesure_id}", response_model=dict)
async def update_mesure(mesure_id: int, updated_mesure: Mesure):
    """Mettre à jour une mesure existante."""
    conn = get_db_connection()
    c = conn.cursor()

    try:
        c.execute(
            """
            UPDATE Mesure
            SET Capteur_Actionneur_id = %s, Valeur = %s
            WHERE id = %s
            """,
            (updated_mesure.capteur_id, updated_mesure.valeur, mesure_id),
        )
        if c.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Mesure avec id {mesure_id} introuvable.")
        conn.commit()
    finally:
        conn.close()

    return {"message": "Mesure mise à jour avec succès"}

@app.put("/factures/{facture_id}", response_model=dict)
async def update_facture(facture_id: int, updated_facture: Facture):
    """Mettre à jour une facture existante."""
    conn = get_db_connection()
    c = conn.cursor()

    try:
        type_facture_id = prise_id_factures(updated_facture.type_facture)
        if not type_facture_id:
            raise HTTPException(
                status_code=404, detail=f"Type de facture '{updated_facture.type_facture}' introuvable"
            )

        c.execute(
            """
            UPDATE Facture
            SET Logement_id = %s, Type_Facture_id = %s, Valeur = %s, Montant = %s
            WHERE id = %s
            """,
            (
                updated_facture.logement_id,
                type_facture_id,
                updated_facture.valeur,
                updated_facture.montant,
                facture_id,
            ),
        )
        if c.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Facture avec id {facture_id} introuvable.")
        conn.commit()
    finally:
        conn.close()

    return {"message": "Facture mise à jour avec succès"}

#Tous les DELETE
@app.delete("/logements/{logement_id}", response_model=dict)
async def delete_logement(logement_id: int):
    """Supprimer un logement."""
    conn = get_db_connection()
    c = conn.cursor()

    try:
        c.execute("DELETE FROM Logement WHERE id = %s", (logement_id,))
        if c.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Logement avec id {logement_id} introuvable.")
        conn.commit()
    finally:
        conn.close()

    return {"message": "Logement supprimé avec succès"}

@app.delete("/pieces/{piece_id}", response_model=dict)
async def delete_piece(piece_id: int):
    """Supprimer une pièce."""
    conn = get_db_connection()
    c = conn.cursor()

    try:
        c.execute("DELETE FROM Piece WHERE id = %s", (piece_id,))
        if c.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Pièce avec id {piece_id} introuvable.")
        conn.commit()
    finally:
        conn.close()

    return {"message": "Pièce supprimée avec succès"}

@app.delete("/capteurs_actionneurs/{capteur_id}", response_model=dict)
async def delete_capteur_actionneur(capteur_id: int):
    """Supprimer un capteur/actionneur."""
    conn = get_db_connection()
    c = conn.cursor()

    try:
        c.execute("DELETE FROM Capteur_Actionneur WHERE id = %s", (capteur_id,))
        if c.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Capteur/actionneur avec id {capteur_id} introuvable.")
        conn.commit()
    finally:
        conn.close()

    return {"message": "Capteur/actionneur supprimé avec succès"}

@app.delete("/mesures/{mesure_id}", response_model=dict)
async def delete_mesure(mesure_id: int):
    """Supprimer une mesure."""
    conn = get_db_connection()
    c = conn.cursor()

    try:
        c.execute("DELETE FROM Mesure WHERE id = %s", (mesure_id,))
        if c.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Mesure avec id {mesure_id} introuvable.")
        conn.commit()
    finally:
        conn.close()

    return {"message": "Mesure supprimée avec succès"}

@app.delete("/factures/{facture_id}", response_model=dict)
async def delete_facture(facture_id: int):
    """Supprimer une facture."""
    conn = get_db_connection()
    c = conn.cursor()

    try:
        c.execute("DELETE FROM Facture WHERE id = %s", (facture_id,))
        if c.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Facture avec id {facture_id} introuvable.")
        conn.commit()
    finally:
        conn.close()

    return {"message": "Facture supprimée avec succès"}

# Partie Front end
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Page d'accueil."""
    data = {"title": "Le logement éco-responsable", "content": "Projet d'IoT"}
    return templates.TemplateResponse("accueil.html", {"request": request, "data": data})

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    """Page 'À propos'."""
    return templates.TemplateResponse("about.html", {"request": request, "title": "À propos"})

@app.get("/ressources", response_class=HTMLResponse)
async def ressources(request: Request):
    """Page 'Ressources'."""
    return templates.TemplateResponse("ressources.html", {"request": request, "title": "Ressources"})

@app.get("/newLogements", response_class=HTMLResponse)
async def ressources(request: Request):
    """Page 'Logements'."""
    return templates.TemplateResponse("newLogements.html", {"request": request, "title": "Logements"})

@app.get("/newPieces", response_class=HTMLResponse)
async def newPieces(request: Request):
    """Page 'Pieces'."""
    return templates.TemplateResponse("newPieces.html", {"request": request, "title": "Pieces"})

@app.get("/newFactures", response_class=HTMLResponse)
async def newPieces(request: Request):
    """Page 'Factures'."""
    return templates.TemplateResponse("newFactures.html", {"request": request, "title": "Factures"})

@app.get("/leaderboard", response_class=HTMLResponse)
async def about(request: Request):
    """Page 'Leaderboard'."""
    return templates.TemplateResponse("leaderboard.html", {"request": request, "title": "Leaderboard"})

@app.get("/newCapteur", response_class=HTMLResponse)
async def about(request: Request):
    """Page 'Capteur / Actionneur'."""
    return templates.TemplateResponse("newCapteur.html", {"request": request, "title": "Capteur / Actionneur"})

# Lancement du serveur
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

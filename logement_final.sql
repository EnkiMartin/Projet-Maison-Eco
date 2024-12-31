--Question 2
DROP TABLE IF EXISTS Logement;
DROP TABLE IF EXISTS Piece;
DROP TABLE IF EXISTS Facture;
DROP TABLE IF EXISTS Mesure;
DROP TABLE IF EXISTS Capteur_Actionneur;
DROP TABLE IF EXISTS Type_de_capteur;
DROP TABLE IF EXISTS Type_de_facture;

--Question 3
CREATE TABLE Logement ( 
    id INTEGER PRIMARY KEY,
    Adresse TEXT, AdresseIP TEXT, Telephone TEXT, Date_insert TIMESTAMP DEFAULT CURRENT_TIMESTAMP
); --J'ai viré les autoincrement sinon rien ne marchait

CREATE TABLE Piece ( 
    id SERIAL PRIMARY KEY,
    Nom TEXT, Logement_id INTEGER NOT NULL, Localisation1 FLOAT, Localisation2 FLOAT, Localisation3 FLOAT,
    FOREIGN KEY (Logement_id) REFERENCES Logement(id)
);

CREATE TABLE Capteur_Actionneur ( 
    id INTEGER PRIMARY KEY,
    Cap_Type TEXT, RefComm TEXT, RefPiece INTEGER, PortCom INTEGER, Date_insert TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (RefPiece) REFERENCES Piece(id)
);

CREATE TABLE Type_de_capteur ( 
    id INTEGER PRIMARY KEY,
    Cap_Type TEXT, Unite TEXT, ValMin FLOAT, ValMax FLOAT
);

CREATE TABLE Mesure ( 
    id INTEGER PRIMARY KEY,
    Capteur_Actionneur_id INTEGER, Date_insert TIMESTAMP DEFAULT CURRENT_TIMESTAMP, Valeur FLOAT,
    FOREIGN KEY (Capteur_Actionneur_id) REFERENCES Capteur_Actionneur(id)
);

CREATE TABLE Type_Facture ( 
    id INTEGER PRIMARY KEY,
    Fac_Type TEXT, Unite TEXT
);

CREATE TABLE Facture ( 
    id INTEGER PRIMARY KEY,
    Logement_id INTEGER, Type_Facture_id INTEGER, Type_Facture TEXT, Valeur FLOAT, Montant FLOAT, Date_insert TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (Logement_id) REFERENCES Logement(id), FOREIGN KEY (Type_Facture_id) REFERENCES Type_Facture(id)
);

--Question 4
INSERT INTO Logement (id, Adresse, AdresseIP, Telephone) 
VALUES (1, 'Rendu adresse', '12345', '0782665550');

INSERT INTO Piece (id, Nom, Logement_id, Localisation1, Localisation2, Localisation3) 
VALUES 
(1, 'Salon', 1, 0.0, 0.0, 0.0),
(2, 'Chambre', 1, 5.0, 0.0, 0.0),
(3, 'Cuisine', 1, 0.0, 5.0, 0.0),
(4, 'Salle de bain', 1, 0.0, 0.0, 5.0);

--Question 5
INSERT INTO Type_de_capteur (id, Cap_Type, Unite, ValMin, ValMax) 
VALUES 
(1, 'Température', '°C', -20.0, 50.0), --Le minimum et le maximum en France depuis 10 ans (merci ChatGPT pour les valeurs)
(2, 'Humidité', '%', 0.0, 100.0),
(3, 'Luminosité', 'Lux', 0.0, 3500.0), --3(00 lux = lumière dans une salle ensoleillée par la lumière naturelle, ça devrait suffir 
(4, 'Mouvement', 'Détection', 0.0, 1.0); --1 si mouvement, 0 sinon

--Question 6
INSERT INTO Capteur_Actionneur (id, Cap_Type, RefComm, RefPiece, PortCom) 
VALUES 
(1, 'Température', 'TAPO T310', 1, 1), -- Capteur de température placé dans le salon, port random. Tapo T310 comme exemple
(2, 'Humidité', 'Aqara', 2, 2);-- Capteur d'humidité placé dans la chambre, port random et différent. Aqara comme exemple

--Question 7
INSERT INTO Mesure (id, Capteur_Actionneur_id, Valeur) 
VALUES 
(1, 1, 16.5),
(2, 1, 28.8),
(3, 2, 55.0),
(4, 2, 60.0);

--Question 8
INSERT INTO Type_Facture (id, Fac_Type, Unite) 
VALUES 
(1, 'Eau', 'm³'),
(2, 'Electricité', 'kWh'),
(3, 'Internet', 'Go');

INSERT INTO Facture (id, Logement_id, Type_Facture_id, Valeur, Montant) 
VALUES 
(1, 1, 50.0, 207.0),  --50 m³ d'eau pour 207€
(1, 2, 50.0, 12.58), --50 kWh pour 12,58€
(1, 3, 50.0, 6.99),  --50 Go d'internet pour 7€
(1, 1, 10.0, 4.14);  --re 10 m³ d'eau pour 4,14 €

--2 types identiques pour vérifier si le logement peut prendre plusieurs factures
--et surtout parce que j'avais plus d'idées de facture
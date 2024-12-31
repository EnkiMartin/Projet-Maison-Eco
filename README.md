ATTENTION : J'AI ENVOYE LES MAUVAIS FICHIERS LE JOUR DU RENDU, vOUS ÊTES DEVANT LA VERSION COMMIT LE LENDEMAIN A 7H30
J'AURAIS SÛREMENT ENVOYE UN MAIL A MONSIEUR HILAIRE POUR M'EXPLIQUER PLUS EN DETAIL

Voici le compte-rendu de mon projet. Un read me était demandé, je vais donc parler des spécificités de ce projet.
Tout d'abord, je souhaite pointer du doigt le fait que le front end est loin d'être parfait.
N'ayant pas fait de html auparavant, je n'ai pas réussi à faire autant que ce que je voulais.
Je vous recommande donc de tester le mode pro si l'ergonomie vous gêne, il vous renvoie vers une partie du site qui fonctionne sans problème.
Vous aurez plus de commandes possibles et l'expérience pourrait vous paraître plus agréable.

Ensuite, j'aimerai parler de ma base de données.
Elle peut vous sembler particulière car je n'ai pas utilisé sqlite3.
Pour plus de clarté de ma partie, je suis passé sur un site appelé neon.tech qui prends du PostgreSQL.
Cela m'a été utile au début pour mieux voir où j'en étais.
Et cela me sera sûrement utile pour mieux préparer la présentation.

Ne faites pas attention à la météo, je l'ai créé mais jamais utilisé.

La partie Leaderboard est une preuve de concept plus qu'autre chose.
Si je devais pousser ce projet plus loin, j'irai sûrement dans la direction d'un classement pour faire entrer en compétition les clients.
Ce serait aussi de l'IoT car nous "interconnecteront" les pc des individus (je sais, très mal dit)

Commandes pour lancer le projet :
cd C:\(répertoire du fichier)
python -m venv env
env\Scripts\activate
pip install fastapi[standard]
pip install psycopg2
pip install jinja2
fastapi dev remplissageREST_final.py

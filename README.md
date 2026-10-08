# Bank Marketing Insights

Dashboard de pilotage des campagnes bancaires, avec Streamlit, FastAPI et un pipeline d'entrainement orchestre par Airflow.

## Apercu

- Synthese historique avec filtres par mois et profession.
- KPI de souscription, graphiques par canal et periode, comparaison des segments et recommandations de campagne.
- Scoring optionnel de fichiers clients via l'API FastAPI.
- Pipeline Airflow, PostgreSQL et MLflow pour l'entrainement et le suivi des modeles.

Les indicateurs de la synthese decrivent les resultats historiques du jeu UCI Bank Marketing. Ils ne constituent pas des previsions garanties. La duree d'appel (`duration`) est exclue des variables de prediction, car elle n'est connue qu'apres le contact.

## Donnees

Le jeu de donnees n'est pas versionne dans Git. Placez le fichier `bank-full.csv` dans `bank/` avant de lancer la plateforme. Le fichier est ignore par `.gitignore` et doit etre fourni localement sur chaque machine ou serveur.

## Lancement complet

Prerequis : Docker et Docker Compose v2.

```bash
docker compose up --build
```

- Dashboard : http://localhost:8501
- API et documentation : http://localhost:8000/docs
- Airflow : http://localhost:8080
- MLflow : http://localhost:5000
- PostgreSQL : localhost:5432

Au premier lancement, activez le DAG `bank_marketing_train` dans Airflow. A la fin de l'entrainement, l'API charge `models/model.pkl`.

## Dashboard seul sur un serveur

Fournissez `bank/bank-full.csv`, installez Docker Compose, puis lancez :

```bash
docker compose -f docker-compose.dashboard.yml up --build -d
```

Le dashboard est disponible sur le port 8501. Modifiez `DASHBOARD_HOST_PORT` dans `.env` si ce port est deja utilise. La vue historique fonctionne sans API ; la page de scoring necessite une API joignable, configurable avec `API_URL` et `API_DOCS_URL`.

## API

- `GET /health` : disponibilite de l'API et du modele.
- `GET /model-info` : version et variables requises.
- `POST /predict` : score d'un profil.
- `POST /predict/batch` : scores par lot, jusqu'a 10 000 profils.

Le CSV de scoring doit contenir les 15 variables du modele : `age`, `job`, `marital`, `education`, `default`, `balance`, `housing`, `loan`, `contact`, `day`, `month`, `campaign`, `pdays`, `previous`, `poutcome`. Les identifiants facultatifs restent dans le fichier exporte et ne sont pas transmis a l'API.

## Stack

Python 3.11, Streamlit, FastAPI, pandas, scikit-learn, XGBoost, Airflow, PostgreSQL, MLflow et Docker Compose.

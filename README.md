# Liste PC Montage

Application web auto-hébergée pour suivre le workflow des PCs vendus / montés / livrés.

## Pré-requis

- Docker + Docker Compose

## Installation rapide

1. Copier `.env.example` vers `.env` et adapter les valeurs.
2. Lancer les services :

```bash
docker-compose up -d --build
```

Un compte admin est créé automatiquement au premier démarrage si aucun utilisateur n'existe encore.
L'application est disponible sur `http://localhost:5173` et l'API sur `http://localhost:8000`.
Sur Synology, remplacez `localhost` par l'IP du NAS.

## Configuration `.env`

- `POSTGRES_PASSWORD` : mot de passe PostgreSQL.
- `JWT_SECRET` : secret de signature des JWT.
- `CORS_ORIGINS` : liste d'origines autorisées (par défaut `*`).
- `VITE_API_BASE` : URL de l'API utilisée par le frontend (par défaut `http://localhost:8000`).
- `ADMIN_USERNAME` : identifiant admin initial (par défaut `admin`).
- `ADMIN_PASSWORD` : mot de passe admin initial (par défaut `admin1234`).
- `ADMIN_ROLE` : rôle admin initial (par défaut `ADMIN`).

## Sauvegardes

Les sauvegardes quotidiennes sont stockées dans `./data/backups`.

### Restauration

```bash
# Arrêter les services

docker-compose down

# Restaurer une sauvegarde (adapter le nom de fichier)

docker run --rm -v $(pwd)/data/backups:/backups -v $(pwd)/data/postgres:/var/lib/postgresql/data \
  postgres:16 bash -c "gunzip -c /backups/<backup>.sql.gz | psql -U postgres -d pcmontage"
```

Ensuite :

```bash
docker-compose up -d
```

## Commandes utiles

```bash
# Logs

docker-compose logs -f

# Migrations manuelles

docker-compose exec backend alembic upgrade head
```

## Tests backend

```bash
pip install -r backend/requirements.txt -r backend/requirements-dev.txt
PYTHONPATH=backend pytest
```

## Import de factures PDF

Le modèle actuellement supporté correspond au PDF d'exemple `tests/fixtures/facture_exemple.pdf`
(facture DreamStation avec une ligne "PC GAMER").

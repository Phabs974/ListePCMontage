# Liste PC Montage

Application web auto-hébergée pour suivre le workflow des PCs vendus / montés / livrés.

## Pré-requis

- Docker + Docker Compose
- Un domaine (optionnel) pour HTTPS automatique via Caddy

## Installation rapide

1. Copier `.env.example` vers `.env` et adapter les valeurs.
2. Lancer les services :

```bash
docker compose up -d --build
```

3. Créer le premier utilisateur admin :

```bash
docker compose exec backend python -m app.cli create-user --username admin --password "motdepasse" --role ADMIN
```

L'application est disponible sur `http://localhost` (ou votre domaine si configuré).

## Configuration `.env`

- `POSTGRES_PASSWORD` : mot de passe PostgreSQL.
- `JWT_SECRET` : secret de signature des JWT.
- `DOMAIN` : domaine utilisé par Caddy (ex: `pcs.example.com`). Mettre `localhost` pour LAN.
- `CADDY_EMAIL` : email pour les certificats Let's Encrypt.
- `CORS_ORIGINS` : liste d'origines autorisées (par défaut `*`).

## Sauvegardes

Les sauvegardes quotidiennes sont stockées dans `./data/backups`.

### Restauration

```bash
# Arrêter les services

docker compose down

# Restaurer une sauvegarde (adapter le nom de fichier)

docker run --rm -v $(pwd)/data/backups:/backups -v $(pwd)/data/postgres:/var/lib/postgresql/data \
  postgres:16 bash -c "gunzip -c /backups/<backup>.sql.gz | psql -U postgres -d pcmontage"
```

Ensuite :

```bash
docker compose up -d
```

## Commandes utiles

```bash
# Logs

docker compose logs -f

# Migrations manuelles

docker compose exec backend alembic upgrade head
```

## Tests backend

```bash
pip install -r backend/requirements.txt -r backend/requirements-dev.txt
PYTHONPATH=backend pytest
```

## Import de factures PDF

Le modèle actuellement supporté correspond au PDF d'exemple `tests/fixtures/facture_exemple.pdf`
(facture DreamStation avec une ligne "PC GAMER").

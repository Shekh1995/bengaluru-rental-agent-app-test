# Casa Bengaluru Rental Agent

A FastAPI application for comparing Bengaluru rental homes by monthly cost, commute, locality, and move-in expense. The application supports a PostgreSQL-backed live listing catalog and an explicit sample-data fallback for local development.

## What it does

- Imports permitted rental listings from a source API.
- Stores active listings in PostgreSQL.
- Synchronizes listings on startup and every 15 minutes by default.
- Supports manual synchronization through `POST /api/sync`.
- Marks listings missing from the latest source response inactive instead of deleting their history.
- Orders live results by monthly rent so lower-priced homes appear first.
- Filters by BHK, rent, locality, furnishing, work location, and commute time.
- Calculates monthly burn, initial move-in cost, deposit ratio, annual projection, and estimated savings.
- Serves the responsive web interface and API from one FastAPI service.

## Important data requirement

The importer must use an API or website source that you are allowed to access. Do not scrape a third-party website if its terms prohibit automated access. The application does not guess or scrape arbitrary websites.

The configured source must return either a JSON array:

```json
[
  {
    "id": "listing-001",
    "title": "Green Haven Builder Floor",
    "area": "Banashankari 3rd Stage",
    "bhk": 2,
    "property_type": "Builder Floor",
    "rent_monthly": 24500,
    "deposit": 120000,
    "maintenance": 1500,
    "furnishing": "Semi-Furnished",
    "built_up_sqft": 1050,
    "floor": "2nd Floor",
    "parking": "1 Covered Car",
    "availability": "Immediate",
    "nearest_metro": "Banashankari Metro",
    "metro_distance_km": 2.2,
    "work_commutes": [
      {
        "destination": "CBD / MG Road",
        "travel_time_mins": 28,
        "mode": "Metro + Auto"
      }
    ],
    "area_character": "Quiet residential streets with good access to transit.",
    "nearby_essentials": ["Supermarket", "Hospital"],
    "verification_flags": ["Owner verified"],
    "google_maps_url": "https://maps.google.com/?q=Banashankari+Bengaluru",
    "listing_source": "Permitted source API",
    "locality_metrics": {
      "water_score": 4.5,
      "noise_level": "Low",
      "green_cover": "High",
      "metro_proximity_km": 2.2
    }
  }
]
```

or an object containing the same array:

```json
{ "listings": [ ... ] }
```

Every listing needs a stable unique `id`. Existing listings with the same ID are updated during sync.

## Requirements

- Python 3.11 or newer
- Git
- PostgreSQL 14 or newer for live data
- Docker Desktop, optional but recommended
- A permitted listing API and API token, if the source requires authentication

## Project structure

```text
app/
  main.py                         FastAPI app, routes, startup sync loop
  models.py                       Pydantic API and listing models
  database.py                     PostgreSQL repository
  services/
    property_service.py           Filtering and sample fallback data
    listing_sync.py                Source API importer and validation
    calculator_service.py         Move-in cost calculations
  static/
    index.html                     Web application markup
    styles.css                     Responsive visual design
    app.js                         Browser API calls and rendering
tests/
  test_api.py                     HTTP endpoint tests
  test_calculator.py               Calculator business-rule tests
docker-compose.yml                 App plus PostgreSQL services
Dockerfile                         Production application image
.env.example                       Environment variable template
```

## Option 1: Run with Docker Compose

Clone the repository and enter its root directory:

```bash
git clone https://github.com/Shekh1995/bengaluru-rental-agent-app-test.git
cd bengaluru-rental-agent-app-test
```

Create the environment file:

```bash
cp .env.example .env
```

On Windows PowerShell, use:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and set the permitted source API:

```env
LISTINGS_API_URL=https://your-domain.example/api/listings
LISTINGS_API_TOKEN=your-source-token
LISTINGS_SYNC_INTERVAL_SECONDS=900
```

Start PostgreSQL and the web application:

```bash
docker compose up --build -d
```

Check the services:

```bash
docker compose ps
docker compose logs -f rental-agent
```

Open the application:

- Local web app: `http://127.0.0.1:8000/`
- API documentation: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/health`
- Readiness: `http://127.0.0.1:8000/ready`

Stop the services without deleting the database volume:

```bash
docker compose down
```

To remove the PostgreSQL data volume as well, use this only when you intentionally want a fresh database:

```bash
docker compose down -v
```

## Option 2: Run directly on a Linux VM

Pull the latest code:

```bash
cd ~/bengaluru-rental-agent-app-test
git pull origin main
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Set the live-data variables. Replace the values with your actual permitted source and PostgreSQL connection:

```bash
export DATABASE_URL='postgresql+psycopg://user:password@127.0.0.1:5432/rental_agent'
export LISTINGS_API_URL='https://your-domain.example/api/listings'
export LISTINGS_API_TOKEN='your-source-token'
export LISTINGS_SYNC_INTERVAL_SECONDS='900'
```

Start the service on all interfaces so it can be reached through the VM public IP:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The terminal must remain open while running this way. For a long-running VM deployment, use Docker Compose or a process manager such as systemd.

Open:

```text
http://YOUR_VM_EXTERNAL_IP:8000/
```

The cloud firewall must allow inbound TCP traffic on port `8000`. Restrict the source IP range in production instead of allowing the whole internet.

## Environment variables

| Variable | Required | Default | Purpose |
| --- | --- | --- | --- |
| `DATABASE_URL` | For live data | Empty | PostgreSQL SQLAlchemy URL. Without it, sample data is used. |
| `LISTINGS_API_URL` | For live sync | Empty | Permitted source endpoint returning listing JSON. |
| `LISTINGS_API_TOKEN` | Source-dependent | Empty | Sent as a Bearer token when set. |
| `LISTINGS_SYNC_INTERVAL_SECONDS` | No | `900` | Background sync interval. `900` equals 15 minutes. |
| `SYNC_TOKEN` | No | Empty | Protects manual sync when set. |
| `APP_ENV` | No | Empty | Deployment environment label. |

Never commit `.env`, database passwords, or API tokens. `.env.example` contains placeholders only.

## Synchronization behavior

When both `DATABASE_URL` and `LISTINGS_API_URL` are configured:

1. The application creates the `rental_listings` table if it does not exist.
2. It attempts an import during startup.
3. It repeats the import every 15 minutes.
4. It validates each record against the `PropertyListing` model.
5. It upserts records by stable listing ID.
6. It marks records absent from the newest successful response inactive.
7. It refuses to replace active data when the source returns an empty response or an invalid response.

Run a manual import:

```bash
curl -X POST http://127.0.0.1:8000/api/sync
```

When `SYNC_TOKEN` is configured:

```bash
curl -X POST http://127.0.0.1:8000/api/sync \
  -H 'X-Sync-Token: your-sync-token'
```

Expected response:

```json
{ "status": "synced", "count": 42 }
```

## API reference

### List properties

```bash
curl 'http://127.0.0.1:8000/api/properties?bhk=2&max_rent=35000'
```

Supported query parameters:

- `min_rent`: minimum monthly rent
- `max_rent`: maximum monthly rent
- `bhk`: number of bedrooms
- `area`: partial locality match
- `furnishing`: partial furnishing match
- `work_location`: commute destination match
- `max_commute_mins`: maximum commute duration

### Get one property

```bash
curl http://127.0.0.1:8000/api/properties/listing-001
```

### Calculate move-in cost

```bash
curl -X POST http://127.0.0.1:8000/api/calculate \
  -H 'Content-Type: application/json' \
  -d '{"rent_monthly":28000,"deposit":120000,"maintenance":2000,"brokerage":0,"agreement_charges":1500}'
```

### Health and readiness

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/ready
```

Readiness reports `database: configured` when PostgreSQL is enabled and `database: sample-data-fallback` otherwise.

## Local development and tests

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
```

Run the complete test suite:

```bash
python -m pytest -q
```

Run Python syntax compilation:

```bash
python -m compileall -q app
```

The default tests run without PostgreSQL and use the sample fallback. Add an integration test database before testing production migrations or real source imports.

## Troubleshooting

### `ERR_CONNECTION_REFUSED`

Start Uvicorn with `--host 0.0.0.0`, not `--host 127.0.0.1`, when accessing the VM public IP. Also confirm the cloud firewall allows TCP port `8000`.

### `Could not import module "app.main"`

Run Uvicorn from the repository root, the directory containing `app`, `requirements.txt`, and `README.md`.

### The app shows sample listings

This means `DATABASE_URL` is missing, or the live source variables are not configured. Set both `DATABASE_URL` and `LISTINGS_API_URL`, restart the service, then call `POST /api/sync`.

### Manual sync returns `502`

Check the application logs. Common causes are an incorrect source URL, expired token, invalid JSON, a response without `listings`, or records that do not match the required model.

### PostgreSQL connection errors

Confirm that PostgreSQL is running, the database exists, the credentials are correct, and the URL uses the installed `psycopg` driver format:

```text
postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE
```

## Security notes

- Use only listing sources you are authorized to access.
- Keep API tokens and database credentials in environment variables or a secret manager.
- Set `SYNC_TOKEN` before exposing the manual sync endpoint publicly.
- Restrict cloud firewall source ranges where possible.
- Put the application behind HTTPS and a reverse proxy for production.
- Replace the default Docker PostgreSQL password before deployment.

## License and data

The repository contains sample listing data for demonstration. Live listing accuracy, availability, pricing, and source permissions remain the responsibility of the configured data provider.

# Eesti Olümpiaadide Andmebaas 

Eesti Olümpiaadide Andmebaas (Estonian Olympiads Database) is a database website that collects all results form Estonian national olympiads.

## Resources

URL for the website is [eoa.ee](https://eoa.ee/).

Some developmental resources are located at [Googel Drive](https://drive.google.com/drive/folders/1rDr4aqyfDYi0hnSqmE-Yxpqh9BMVYtnK).

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

### Example workflow for entering results

1. Download .pdf from [Teaduskool](https://www.teaduskool.ut.ee/et).
2. (*If necessary*) Perform ocr with [OCRmyPDF](https://github.com/jbarlow83/OCRmyPDF).
3. Convert .pdf to .csv with [Tabula](https://tabula.technology/).
4. Make corrections to the .csv with a text editor  (e.g. *Emacs with csv-mode*) and/or spreadsheet (e.g. *Google Sheets*).
5. Upload .csv to the database. 

## Support

For help contact <eoakontakt@gmail.com>.

## License
[MIT](https://choosealicense.com/licenses/mit/)

## Local deployment using Docker Compose

1. Copy `.env.example` to `.env` and add required variables.
2. Run `docker compose up` (or `docker compose up --build -d --remove-orphans`
   to rebuild and run in the background).
3. Open `http://localhost:8080` (or the port set by `WEB_PORT`).

The example environment sets `WEB_PORT=8080` for local convenience. If
`WEB_PORT` is unset, empty, or `0`, Docker assigns an available localhost port;
find it with `docker compose port web 3000`.

The public site runs in `web/` (Next.js). It calls the FastAPI service in `api/`
over the private Docker network. The documented contest, people, and school API
endpoints are exposed through the site at `/api/*`; site and statistics endpoints
stay internal. The web port is published only on `127.0.0.1`; MariaDB and FastAPI
are available only within the Compose network. On a fresh database volume,
MariaDB imports the snapshot from `backups/initdb/` automatically. Subsequent
deployments keep the existing data volume. To roll back a release,
restore the prior images and Compose configuration without replacing that volume.

The same Compose file can be deployed through Dokploy: select
`docker-compose.yaml`, configure the variables from `.env.example`, and attach
the demo domain to service `web` on container port `3000`. Dokploy manages the
proxy network and routing. Omit `WEB_PORT` or set it to `0` in Dokploy to avoid
fixed host-port conflicts between deployments.

For local frontend development, copy `api/.env.example` to `api/.env` and set
its database variables for a MariaDB instance accessible from your host (the
Compose database does not publish a host port). Run `uv run fastapi dev` in
`api/`, then `npm ci && API_INTERNAL_URL=http://localhost:8000 npm run dev` in
`web/`.

## Legacy site migration

The PHP site formerly in `eoa.ee/` has been retired. Its database queries now
live in `api/`, and its public pages are implemented in `web/`:

| Legacy page | Replacement |
| --- | --- |
| Home and contest navigation | `/` and `/contests` |
| `?id=…` result tables, tasks, and descriptions | `/results/[id]` |
| `?name=…` name search | `/search?q=…` |
| `?name_id=…` participation and mentoring profiles | `/people/[id]` |
| `?kool=true` school rankings | `/schools` |
| `?hof=true` honor roll | `/people` |
| `?school_id=…` school students and mentors | `/schools/[id]` |

The home page redirects the old query parameters to their replacements, and
`/index.php` redirects to `/`. Rankings and navigation use the new site's
presentation and scoring. The Google site verification token is retained in
the root layout. The legacy PDF and its metadata reference were removed;
document references will be reworked separately.
The old `esialgsed.php` spreadsheet helpers had no route or callers in the PHP
site and were removed with the unused PHP runtime, CSS, and JavaScript.

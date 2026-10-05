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
2. Run `docker compose up --build -d --remove-orphans`.
3. Open `http://localhost:8080` (or the port set by `WEB_PORT`).

The public site runs in `web/` (Next.js). It calls the FastAPI service in `api/`
over the private Docker network. The documented contest, people, and school API
endpoints are exposed through the site at `/api/*`; site and statistics endpoints
stay internal. MariaDB keeps the existing data volume. To roll back a release,
restore the prior images and Compose configuration without replacing that volume.

For local frontend development, copy `api/.env.example` to `api/.env` and set
its database variables for the local MariaDB port. Run `uv run fastapi dev` in
`api/`, then `npm ci && API_INTERNAL_URL=http://localhost:8000 npm run dev` in
`web/`.

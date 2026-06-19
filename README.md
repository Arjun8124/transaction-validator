# Transaction Data Validator

A small web app for validating transaction data files. Upload a CSV or Excel
file and the app checks each row for required fields, valid phone numbers,
dates, amounts, payment modes, and duplicate order IDs. Valid rows can be
downloaded as a cleaned file, an error report, or split into smaller chunks.

The project has two parts:

- **`backend/`** – a Django + [Django Ninja](https://django-ninja.dev/) API that
  parses the upload, runs the validation rules, and serves the results.
- **`frontend/`** – a React (Vite) single-page app with a drag-and-drop upload,
  a results summary, and download links.

## How it works

1. The user uploads a `.csv` or `.xlsx` file from the frontend.
2. The backend reads it with pandas, validates every row, and writes the
   results to `backend/jobs/<job_id>/` as `cleaned.csv` and `errors.csv`.
3. The response returns a summary (total / valid / invalid) and the first 100
   errors for display.
4. The user can download the cleaned data, the full error report, or a zip of
   the cleaned data split into fixed-size chunks.

## Validation rules

Defined in [`backend/validator/validation.py`](backend/validator/validation.py).

| Check | Rule |
| --- | --- |
| **Required fields** | `order_id`, `order_date`, `customer_name`, `country`, `phone`, `product_id`, `product_name`, `amount`, `payment_mode` must all be present |
| **Phone** | Digit count must match the country: `IN`/`US`/`UK` = 10, `SG` = 8, `AE` = 9 |
| **Date** | Must match one of: `YYYY-MM-DD`, `DD/MM/YYYY`, `DD-MM-YYYY`, `DD Mon YYYY` |
| **Amount** | Must be numeric and non-negative |
| **Payment mode** | Must be one of: `UPI`, `CARD`, `CREDIT CARD`, `DEBIT CARD`, `COD`, `NETBANKING`, `WALLET`, `PAYPAL` |
| **Duplicates** | Repeated `order_id` values are flagged |

A row with any problem is excluded from the cleaned output and listed in the
error report (with the original CSV line number).

## API

The API is served under `/api`.

### `POST /api/validate`

Upload a file as multipart form-data (field name `file`).

```json
{
  "job_id": "09102d4613c34efea70e62d81ccae468",
  "summary": { "total": 1000, "valid": 940, "invalid": 60 },
  "errors": [
    { "row": 7, "order_id": "A123", "problem": "IN phone should be 10 digits; invalid date format" }
  ]
}
```

### `GET /api/download/{job_id}/{kind}`

- `kind=cleaned` – the cleaned CSV (valid rows only)
- `kind=errors` – the error report CSV
- `kind=chunks` – the cleaned data split into multiple CSVs, returned as a zip.
  Pass `?size=N` to set rows per chunk (default `500`).

## Getting started

### Prerequisites

- Python 3.14+ and [uv](https://docs.astral.sh/uv/) (the backend is managed with `uv`)
- Node.js 18+ and npm

### Backend

```bash
cd backend
uv sync                       # install dependencies
uv run python manage.py migrate
uv run python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/api`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The dev server runs at `http://localhost:5173` and talks to the backend at
`http://127.0.0.1:8000` by default. To point it elsewhere, set `VITE_API_BASE`:

```bash
VITE_API_BASE=https://your-backend.example.com npm run dev
```

## Tech stack

- **Backend:** Django 6, Django Ninja, pandas, openpyxl, SQLite, gunicorn
- **Frontend:** React 19, Vite, axios

## Notes

- The shipped Django settings are development defaults (`DEBUG = True`,
  `CORS_ALLOW_ALL_ORIGINS = True`, a checked-in `SECRET_KEY`). Harden these
  before deploying anywhere public.
- Uploads are capped at 20 MB (`DATA_UPLOAD_MAX_MEMORY_SIZE`).
- Job results accumulate under `backend/jobs/`; there is no automatic cleanup.

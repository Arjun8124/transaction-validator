import io
import uuid
import zipfile
from pathlib import Path

import pandas as pd
from django.conf import settings
from django.http import FileResponse, HttpResponse
from ninja import File, NinjaAPI
from ninja.files import UploadedFile

from .validation import validate_dataframe

api = NinjaAPI()

# Folder where we keep each upload's results.
JOBS = Path(settings.BASE_DIR) / "jobs"
JOBS.mkdir(exist_ok=True)


def read_file(upload):
    if upload.name.lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(upload, dtype=str).fillna("")
    return pd.read_csv(upload, dtype=str, keep_default_na=False)


@api.post("/validate")
def validate(request, file: UploadedFile = File(...)):
    df = read_file(file)
    cleaned, errors, summary = validate_dataframe(df)

    job_id = uuid.uuid4().hex
    folder = JOBS / job_id
    folder.mkdir()
    cleaned.to_csv(folder / "cleaned.csv", index=False)
    pd.DataFrame(errors, columns=["row", "order_id", "problem"]).to_csv(
        folder / "errors.csv", index=False
    )

    return {"job_id": job_id, "summary": summary, "errors": errors[:100]}


@api.get("/download/{job_id}/{kind}")
def download(request, job_id: str, kind: str, size: int = 500):
    folder = JOBS / job_id

    # Split the cleaned data into smaller CSVs and send them as a zip.
    if kind == "chunks":
        df = pd.read_csv(folder / "cleaned.csv", dtype=str, keep_default_na=False)
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as zf:
            for n, start in enumerate(range(0, len(df), size), start=1):
                part = df.iloc[start : start + size]
                zf.writestr(f"chunk_{n}.csv", part.to_csv(index=False))
        return HttpResponse(
            buffer.getvalue(),
            content_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=chunks.zip"},
        )

    # Otherwise just serve cleaned.csv or errors.csv.
    return FileResponse(
        open(folder / f"{kind}.csv", "rb"), as_attachment=True, filename=f"{kind}.csv"
    )

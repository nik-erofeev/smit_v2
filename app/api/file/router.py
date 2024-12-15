import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.core.settings import APP_CONFIG

router = APIRouter(tags=["Файлы"])


@router.get("/download/{filename}")
async def download_link(filename: str):
    full_path = os.path.join(APP_CONFIG.download_dir, filename)
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="Файл не найден")

    return FileResponse(
        path=full_path,
        filename=filename,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": "application/octet-stream",
        },
    )

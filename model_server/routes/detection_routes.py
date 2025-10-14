from fastapi import APIRouter, HTTPException
from config import TILES_DIR
from services.ship_detector import detect_ships
from services.oilspill_detector import detect_oilspill
from pathlib import Path

router = APIRouter()

@router.post("/detect/dzi/{type}/{image_id}")
def detect_from_dzi(type: str, image_id: str):
    if type not in {"ship", "oilspill"}:
        raise HTTPException(status_code=400, detail="Invalid type. Use 'ship' or 'oilspill'.")

    dzi_folder = TILES_DIR / type / image_id / f"{image_id}_files"
    if not dzi_folder.exists():
        raise HTTPException(status_code=404, detail=f"Tile folder not found: {dzi_folder}")

    # 🔍 Find the deepest zoom level directory (largest number)
    try:
        zoom_levels = [
            int(folder.name) for folder in dzi_folder.iterdir() if folder.is_dir() and folder.name.isdigit()
        ]
        if not zoom_levels:
            raise HTTPException(status_code=500, detail="No zoom level folders found inside tile folder.")

        max_zoom_level = str(max(zoom_levels))
        deepest_tile_path = dzi_folder / max_zoom_level

        if not deepest_tile_path.exists():
            raise HTTPException(status_code=404, detail=f"Deepest zoom level folder not found: {deepest_tile_path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading zoom levels: {str(e)}")

    try:
        if type == "ship":
            results = detect_ships(str(dzi_folder), max_zoom_level)
        else:
            results = detect_oilspill(str(dzi_folder), max_zoom_level)

        return {
            "message": f"{type.capitalize()} DZI detection complete.",
            "count": len(results),
            "detections": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

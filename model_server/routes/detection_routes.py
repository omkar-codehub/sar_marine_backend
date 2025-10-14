# from fastapi import APIRouter, HTTPException
# from pathlib import Path
# from services.ship_detector import detect_ships
# from services.oilspill_detector import detect_oil_spill
# from config import UPLOADS_DIR, OUTPUTS_DIR

# router = APIRouter()

# ALLOWED_TYPES = {"ship", "oilspill"}

# @router.post("/detect/{type}/{image_id}")
# def run_detection(type: str, image_id: str):
#     if type not in ALLOWED_TYPES:
#         raise HTTPException(status_code=400, detail=f"Invalid detection type '{type}'. Must be 'ship' or 'oilspill'.")

#     input_path = UPLOADS_DIR / type / f"{image_id}.tif"
#     if not input_path.exists():
#         raise HTTPException(status_code=404, detail=f"Image '{input_path}' not found")

#     output_dir = OUTPUTS_DIR / type / image_id
#     output_dir.mkdir(parents=True, exist_ok=True)

#     try:
#         if type == "ship":
#             result = detect_ships(input_path, output_dir, device="cpu", threshold=0.5)
#         else:  # oilspill
#             result = detect_oil_spill(input_path, output_dir, device="cpu", threshold=0.5)

#         return {
#             "message": f"{type.capitalize()} detection completed",
#             "result": result
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

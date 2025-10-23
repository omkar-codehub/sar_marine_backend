# API Documentation for Image Processing Server

This document outlines the API endpoints for the image processing server, including routes, HTTP methods, expected inputs, and outputs. The server handles image uploads, DZI (Deep Zoom Image) generation, and detection tasks for ship and oil spill imagery. The Node.js server proxies certain requests (DZI generation and detection) to a Python backend for processing.

## Base URL
`http://localhost:3000` (or the configured `PORT` environment variable)

## Routes Overview

### 1. Image Upload Routes (`/api/images`)
Handles uploading and listing TIFF images for specific types (`ship` or `oilspill`).

#### POST `/api/images/upload/:type`
Uploads a TIFF image for the specified type (`ship` or `oilspill`).

- **Method**: POST
- **Parameters**:
  - `type` (path parameter): Type of image. Must be `"ship"` or `"oilspill"`.
- **Body** (multipart/form-data):
  - `image`: A TIFF file (`.tif` or `.tiff`). Maximum size: 5GB.
- **Response**:
  - **Success (201)**:
    ```json
    {
      "message": "Image uploaded successfully",
      "type": "ship" | "oilspill",
      "file": {
        "imageId": "<unique-image-id (filename without extension)>",
        "filename": "<generated-filename (e.g., timestamp-originalname)>",
        "originalname": "<original-filename>",
        "mimetype": "image/tiff",
        "size": <file-size-in-bytes>,
        "uploadPath": "/uploads/<type>/<generated-filename>"
      }
    }
    ```
  - **Error (400)**:
    ```json
    {
      "error": "No file uploaded" | "Only TIFF files are allowed!" | "Invalid upload type" | "File size exceeds limit"
    }
    ```
- **Notes**: The `imageId` is derived from the generated filename and is used in subsequent routes like DZI generation and detection.
- **Example**:
  ```bash
  curl -X POST -F "image=@sample.tiff" http://localhost:3000/api/images/upload/ship
  ```

#### GET `/api/images/uploads/:type`
Lists all uploaded TIFF images for the specified type (`ship` or `oilspill`).

- **Method**: GET
- **Parameters**:
  - `type` (path parameter): Type of image. Must be `"ship"` or `"oilspill"`.
- **Body**: None
- **Response**:
  - **Success (200)**:
    ```json
    {
      "images": [
        {
          "imageId": "<unique-image-id>",
          "filename": "<filename>",
          "type": "ship" | "oilspill",
          "uploadUrl": "/uploads/<type>/<filename>"
        },
        ...
      ]
    }
    ```
  - **Error (400)**:
    ```json
    {
      "error": "Invalid image type. Use \"ship\" or \"oilspill\"."
    }
    ```
  - **Error (500)**:
    ```json
    {
      "error": "Unable to list uploads for type: <type>"
    }
    ```
- **Example**:
  ```bash
  curl http://localhost:3000/api/images/uploads/ship
  ```

#### GET `/api/images/outputs/oilspill`
Lists all DZI output files for oil spill detection masks (located in `shared/outputs/oilspill`).

- **Method**: GET
- **Parameters**: None
- **Body**: None
- **Response**:
  - **Success (200)**:
    ```json
    {
      "count": <number-of-dzi-files>,
      "items": [
        {
          "dziFile": "<imageId>.dzi",
          "dziPath": "<absolute-server-path-to-dzi-file>",
          "filesFolder": "<absolute-server-path-to-tiles-folder (e.g., imageId_files)>"
        },
        ...
      ]
    }
    ```
  - **Notes**: The `dziPath` and `filesFolder` are absolute server paths. For frontend access, use URLs like `/outputs/oilspill/<imageId>.dzi` and `/outputs/oilspill/<imageId>_files/<zoom>/<x>_<y>.jpeg`.
- **Example**:
  ```bash
  curl http://localhost:3000/api/images/outputs/oilspill
  ```

### 2. DZI Generation Routes (`/api/dzi`)
Generates DZI files for uploaded images to enable deep zoom functionality. Proxies to Python backend if DZI does not already exist.

#### POST `/api/dzi/generate/:type/:imageId`
Generates a DZI file for the specified image and type.

- **Method**: POST
- **Parameters**:
  - `type` (path parameter): Type of image. Must be `"ship"` or `"oilspill"`.
  - `imageId` (path parameter): Unique ID of the uploaded image (from upload response).
- **Body**: None
- **Response**:
  - **Success (200)**:
    - If DZI already exists:
      ```json
      {
        "message": "DZI already exists",
        "dziUrl": "/tiles/<type>/<imageId>/<imageId>.dzi"
      }
      ```
    - If generated successfully (via Python backend):
      ```json
      {
        "message": "DZI generated successfully",
        "dzi_url": "/tiles/<type>/<imageId>/<imageId>.dzi"
      }
      ```
  - **Error (400)**:
    ```json
    {
      "error": "Invalid type. Must be \"ship\" or \"oilspill\"."
    }
    ```
  - **Error (500)**:
    ```json
    {
      "error": "Failed to generate DZI via Python service" | "<other-error-from-python (e.g., Image not found)>"
    }
    ```
- **Notes**: The Python backend uses a tile size of 512 for `"ship"` and 256 for `"oilspill"`. The DZI file and tiles are stored in `shared/tiles/<type>/<imageId>`.
- **Example**:
  ```bash
  curl -X POST http://localhost:3000/api/dzi/generate/ship/123456789-sample
  ```

### 3. Detection Routes (`/api/detect`)
Performs detection (ship or oil spill) on a specified image using its DZI tiles. Proxies to Python backend. Requires DZI to be generated first.

#### POST `/api/detect/:type/:imageId`
Runs detection for the specified type and image.

- **Method**: POST
- **Parameters**:
  - `type` (path parameter): Type of detection. Must be `"ship"` or `"oilspill"`.
  - `imageId` (path parameter): Unique ID of the uploaded image.
- **Body**: None
- **Response**:
  - **Success (200)**:
    ```json
    {
      "message": "Ship detection completed" | "Oil spill detection completed",
      "data": {
        "message": "Ship DZI detection complete." | "Oilspill DZI detection complete.",
        "count": <number-of-detections-or-keys>,
        "detections": <array-or-object (see notes)>
      }
    }
    ```
  - **Error (400)**:
    ```json
    {
      "error": "Invalid type. Use \"ship\" or \"oilspill\"." | "Image ID required"
    }
    ```
  - **Error (500)**:
    ```json
    {
      "error": "<type> detection failed" | "<other-error-from-python (e.g., Tile folder not found)>"
    }
    ```
- **Notes**:
  - Detection uses the deepest zoom level (e.g., "15") from the DZI tiles.
  - For `"ship"`:
    - `"count"`: Number of detected ships.
    - `"detections"`: Array of objects, each:
      ```json
      {
        "x": <float (global x-coordinate)>,
        "y": <float (global y-coordinate)>,
        "w": <float (width)>,
        "h": <float (height)>,
        "label": "<string (e.g., 'object')>",
        "score": <float (confidence score, >0.5)>
      }
      ```
    - NMS (Non-Maximum Suppression) is applied with IoU threshold 0.5.
  - For `"oilspill"`:
    - `"count"`: 3 (fixed, number of keys in detections).
    - `"detections"`: Object with:
      ```json
      {
        "stitched_mask": "<absolute-path-to-stitched-mask-png>",
        "dzi_path": "<absolute-path-to-dzi-directory (e.g., .../outputs/oilspill/<imageId>)>",
        "dzi_folder": "<absolute-path-to-tiles-folder (e.g., .../outputs/oilspill/<imageId>/<imageId>_files)>"
      }
      ```
    - Generates a stitched mask PNG and its DZI (tile size 256). Access via `/outputs/oilspill/<imageId>.dzi` and tiles via `/outputs/oilspill/<imageId>_files/...`.
- **Example**:
  ```bash
  curl -X POST http://localhost:3000/api/detect/ship/123456789-sample
  ```

### 4. Static File Routes
Serves static files (tiles and outputs) for viewing.

#### GET `/tiles/oilspill/*`
Serves DZI tiles for oil spill images.

- **Method**: GET
- **Path**: `/tiles/oilspill/<imageId>/<imageId>.dzi` or `/tiles/oilspill/<imageId>/<imageId>_files/<zoom>/<x>_<y>.jpeg`
- **Response**: Serves the requested DZI file or tile image (JPEG).

#### GET `/tiles/ship/*`
Serves DZI tiles for ship images.

- **Method**: GET
- **Path**: `/tiles/ship/<imageId>/<imageId>.dzi` or `/tiles/ship/<imageId>/<imageId>_files/<zoom>/<x>_<y>.jpeg`
- **Response**: Serves the requested DZI file or tile image (JPEG).

#### GET `/outputs/oilspill/*`
Serves oil spill detection output files, including stitched masks and mask DZIs.

- **Method**: GET
- **Path**: `/outputs/oilspill/<imageId>_oilspill_mask.png` or `/outputs/oilspill/<imageId>.dzi` or `/outputs/oilspill/<imageId>_files/<zoom>/<x>_<y>.jpeg`
- **Response**: Serves the requested file (PNG for mask, XML for DZI, JPEG for tiles).

## Notes
- **File Size Limit**: Image uploads are limited to 5GB.
- **File Type**: Only TIFF files (`.tif` or `.tiff`) are accepted for uploads.
- **Python Backend**: DZI generation and detection proxy to a Python backend at `http://localhost:8000` (configurable via `PYTHON_API_BASE`). Ensure it's running.
- **CORS**: Enabled for cross-origin requests.
- **File Storage**:
  - Uploaded images: `shared/uploads/<type>/`.
  - DZI tiles: `shared/tiles/<type>/<imageId>/`.
  - Oil spill outputs (masks and DZIs): `shared/outputs/oilspill/<imageId>/` (but files are placed directly under `oilspill/` with `<imageId>` prefix).
- **Prerequisites**: For detection, generate DZI first as it uses the tiles.
- **Models**: Ship uses Deformable DETR; Oil spill uses Vision Transformer. Models loaded from configured paths.
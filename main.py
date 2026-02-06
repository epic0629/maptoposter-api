"""
Map Poster API - FastAPI service for generating city map posters
"""

import io
import os
import tempfile
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse

# Import from the original maptoposter
from create_map_poster import (
    get_coordinates,
    load_theme,
    create_poster,
    get_available_themes,
    THEMES_DIR,
    POSTERS_DIR,
)

app = FastAPI(
    title="Map Poster API",
    description="Generate beautiful minimalist city map posters",
    version="1.0.0",
)

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your Netlify domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure output directory exists
os.makedirs(POSTERS_DIR, exist_ok=True)


@app.get("/")
def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "Map Poster API is running"}


@app.get("/themes")
def list_themes():
    """Get list of available themes"""
    themes = get_available_themes()
    return {"themes": themes}


@app.get("/generate")
def generate_poster(
    city: str = Query(..., description="City name (e.g., Taipei)"),
    country: str = Query(..., description="Country name (e.g., Taiwan)"),
    theme: str = Query("noir", description="Theme name"),
    distance: int = Query(5000, description="Map radius in meters", ge=1000, le=20000),
    display_city: Optional[str] = Query(None, description="Display name for city (for non-Latin scripts)"),
    display_country: Optional[str] = Query(None, description="Display name for country"),
    width: int = Query(12, description="Poster width in inches", ge=6, le=24),
    height: int = Query(16, description="Poster height in inches", ge=8, le=32),
):
    """
    Generate a city map poster

    Returns the poster as a PNG image
    """
    try:
        # Load theme
        theme_data = load_theme(theme)
        if not theme_data:
            raise HTTPException(status_code=400, detail=f"Theme '{theme}' not found")

        # Get coordinates
        print(f"Looking up coordinates for {city}, {country}...")
        coords = get_coordinates(city, country)

        # Create temporary file for output
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            output_path = tmp.name

        # Generate poster
        create_poster(
            city=city,
            country=country,
            point=coords,
            dist=distance,
            output_file=output_path,
            output_format="png",
            width=width,
            height=height,
            display_city=display_city,
            display_country=display_country,
        )

        # Read the generated image
        with open(output_path, "rb") as f:
            image_data = f.read()

        # Clean up temp file
        os.unlink(output_path)

        # Return image as streaming response
        return StreamingResponse(
            io.BytesIO(image_data),
            media_type="image/png",
            headers={
                "Content-Disposition": f"attachment; filename={city.lower()}_{theme}_poster.png"
            }
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating poster: {str(e)}")


@app.get("/preview")
def preview_poster(
    city: str = Query(..., description="City name"),
    country: str = Query(..., description="Country name"),
    theme: str = Query("noir", description="Theme name"),
):
    """
    Get poster preview info without generating the full image

    Returns coordinates and theme info
    """
    try:
        coords = get_coordinates(city, country)
        theme_data = load_theme(theme)

        return {
            "city": city,
            "country": country,
            "coordinates": {
                "latitude": coords[0],
                "longitude": coords[1],
            },
            "theme": {
                "name": theme,
                "description": theme_data.get("description", ""),
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

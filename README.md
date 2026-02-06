# Map Poster API

A FastAPI service that generates beautiful minimalist city map posters.

## API Endpoints

### `GET /`
Health check

### `GET /themes`
List available themes

### `GET /generate`
Generate a map poster

**Parameters:**
- `city` (required): City name (e.g., "Taipei")
- `country` (required): Country name (e.g., "Taiwan")
- `theme` (optional): Theme name (default: "noir")
- `distance` (optional): Map radius in meters (default: 5000)
- `display_city` (optional): Display name for city (for non-Latin scripts)
- `display_country` (optional): Display name for country

**Example:**
```
GET /generate?city=Taipei&country=Taiwan&theme=noir
```

### `GET /preview`
Get poster preview info without generating the image

## Available Themes

- noir
- neon_cyberpunk
- blueprint
- japanese_ink
- midnight_blue
- and more...

## Deployment

This API is designed to be deployed on Railway.

## Local Development

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

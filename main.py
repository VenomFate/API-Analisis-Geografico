from fastapi import FastAPI, HTTPException, Body
import httpx
from typing import List, Optional
from pydantic import BaseModel

app = FastAPI()

REST_COUNTRIES_URL = "https://restcountries.com/v3.1"
VALID_REGIONS = {"Africa", "Americas", "Asia", "Europe", "Oceania"}

class CountrySearchFilters(BaseModel):
    minPopulation: Optional[int]
    maxPopulation: Optional[int]
    languages: Optional[List[str]]
    region: Optional[str]

@app.get("/countries/{code}/neighbors")
async def get_country_neighbors(code: str):
    async with httpx.AsyncClient() as client:
        # Obtener datos del país consultado
        resp = await client.get(f"{REST_COUNTRIES_URL}/alpha/{code}")
        if resp.status_code != 200:
            raise HTTPException(status_code=404, detail="Country not found")
        country = resp.json()[0]

        # Obtener códigos de países vecinos
        borders = country.get("borders", [])
        if not borders:
            return {
                "neighbors": [],
                "total_border_population": country.get("population", 0),
                "shared_language_neighbors": []
            }

        # Obtener datos de los países vecinos
        neighbors_resp = await client.get(f"{REST_COUNTRIES_URL}/alpha?codes={','.join(borders)}")
        neighbors = neighbors_resp.json()

        # Preparar lista de vecinos
        neighbors_list = []
        shared_language_neighbors = []
        country_languages = set(country.get("languages", {}).values())
        total_population = country.get("population", 0)

        for neighbor in neighbors:
            neighbor_languages = set(neighbor.get("languages", {}).values())
            neighbors_list.append({
                "name": neighbor.get("name", {}).get("common"),
                "capital": neighbor.get("capital", [None])[0],
                "population": neighbor.get("population", 0)
            })
            total_population += neighbor.get("population", 0)
            if country_languages & neighbor_languages:
                shared_language_neighbors.append(neighbor.get("name", {}).get("common"))

        return {
            "neighbors": neighbors_list,
            "total_border_population": total_population,
            "shared_language_neighbors": shared_language_neighbors
        }

@app.get("/route")
async def get_land_route(from_: str, to: str):
    from_code = from_.upper()
    to_code = to.upper()
    if from_code == to_code:
        return {
            "connected": True,
            "route": [from_code]
        }

    async with httpx.AsyncClient() as client:
        # Obtener todos los países con sus fronteras
        resp = await client.get(f"{REST_COUNTRIES_URL}/all?fields=cca3,borders")
        if resp.status_code != 200:
            raise HTTPException(status_code=500, detail="Error fetching countries data")
        countries = resp.json()

        # Crear un mapa de fronteras
        borders_map = {c["cca3"]: c.get("borders", []) for c in countries}

        # Verificar que ambos países existan
        if from_code not in borders_map or to_code not in borders_map:
            raise HTTPException(status_code=404, detail="One or both country codes not found")

        # BFS para encontrar la ruta más corta
        from collections import deque

        queue = deque([[from_code]])
        visited = set([from_code])

        while queue:
            path = queue.popleft()
            current = path[-1]
            for neighbor in borders_map.get(current, []):
                if neighbor == to_code:
                    return {
                        "connected": True,
                        "route": path + [neighbor]
                    }
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(path + [neighbor])

        return {
            "connected": False,
            "route": []
        }

@app.get("/regions/{region}/stats")
async def get_region_stats(region: str):
    region = region.capitalize()
    if region and region.capitalize() not in VALID_REGIONS:
        raise HTTPException(status_code=400, detail="Invalid region")
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{REST_COUNTRIES_URL}/region/{region}")
        if resp.status_code != 200:
            raise HTTPException(status_code=404, detail="Region not found")
        countries = resp.json()

        if not countries:
            raise HTTPException(status_code=404, detail="No countries found in this region")

        total_countries = len(countries)
        total_population = sum(c.get("population", 0) for c in countries)
        avg_population = total_population / total_countries if total_countries else 0

        # Recolectar todos los idiomas únicos
        languages = set()
        for c in countries:
            langs = c.get("languages", {})
            for lang in langs.values():
                languages.add(lang)
        total_languages = len(languages)

        # Top 5 países por población
        top5 = sorted(
            [{"name": c.get("name", {}).get("common"), "population": c.get("population", 0)} for c in countries],
            key=lambda x: x["population"],
            reverse=True
        )[:5]

        return {
            "total_countries": total_countries,
            "total_population": total_population,
            "average_population": avg_population,
            "unique_languages": total_languages,
            "top_5_countries_by_population": top5
        }

@app.post("/countries/search")
async def search_countries(filters: CountrySearchFilters = Body(...)):
    min_population = filters.minPopulation
    max_population = filters.maxPopulation
    languages = set(filters.languages or [])
    region = filters.region

    async with httpx.AsyncClient() as client:
        # Obtener todos los países (filtrar por región si se especifica)
        if region:
            resp = await client.get(f"{REST_COUNTRIES_URL}/region/{region}")
        else:
            resp = await client.get(f"{REST_COUNTRIES_URL}/all")
        if resp.status_code != 200:
            raise HTTPException(status_code=500, detail="Error fetching countries data")
        countries = resp.json()

        results = []
        for c in countries:
            pop = c.get("population", 0)
            # Filtro por población mínima
            if min_population is not None and pop < min_population:
                continue
            # Filtro por población máxima
            if max_population is not None and pop > max_population:
                continue
            # Filtro por idiomas
            country_languages = set(c.get("languages", {}).values())
            if languages and not (country_languages & languages):
                continue
            results.append({
                "name": c.get("name", {}).get("common"),
                "code": c.get("cca3")
            })

        return {
            "total": len(results),
            "countries": results
        }
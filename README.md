# API de Análisis Geográfico

Esta API REST, construida con FastAPI, permite consultar información de países y regiones utilizando la REST Countries API como fuente de datos. Proporciona análisis de vecindad, rutas terrestres, estadísticas regionales y búsqueda avanzada de países.

---

## 🚀 Construcción y Ejecución con Docker

### 1. Clona el repositorio

```bash
git clone <URL_DE_TU_REPOSITORIO>
cd API_Analisis_Geografico
```

### 2. Construye la imagen Docker

```bash
docker build -t api-analisis-geografico .
```

### 3. Ejecuta el contenedor

```bash
docker run --name api-analisis-geografico-container -p 8000:8000 api-analisis-geografico
```

La API estará disponible en [http://localhost:8000](http://localhost:8000)

---

## 📚 Documentación de la API

La documentación interactiva está disponible en [http://localhost:8000/docs](http://localhost:8000/docs)

### Endpoints principales

#### 1. **Análisis de Vecindad**
- **GET** `/countries/{code}/neighbors`
- Devuelve los países vecinos, población total de la región fronteriza y vecinos con idiomas oficiales en común.
- **Ejemplo:**  
  `/countries/DEU/neighbors`

#### 2. **Rutas Terrestres**
- **GET** `/route?from={code}&to={code}`
- Determina si existe una ruta terrestre entre dos países y retorna el camino más corto.
- **Ejemplo:**  
  `/route?from=CHL&to=BRA`

#### 3. **Estadísticas Regionales**
- **GET** `/regions/{region}/stats`
- Devuelve estadísticas agregadas de una región: cantidad de países, población total y promedio, idiomas únicos y top 5 países por población.
- **Ejemplo:**  
  `/regions/Americas/stats`

#### 4. **Búsqueda Avanzada**
- **POST** `/countries/search`
- Permite buscar países aplicando filtros combinados (población, idiomas, región).
- **Body de ejemplo:**
    ```json
    {
      "minPopulation": 10000000,
      "maxPopulation": 100000000,
      "languages": ["Spanish", "English"],
      "region": "Americas"
    }
    ```

---

## 📝 Notas

- Los códigos de país deben ser de 3 letras (ej: `USA`, `CHL`, `DEU`).
- La API depende de la disponibilidad de [REST Countries API](https://restcountries.com/).
- Puedes modificar y extender los endpoints según tus necesidades.

---

## 📄
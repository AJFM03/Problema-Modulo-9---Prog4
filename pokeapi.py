import requests
import time

BASE_URL = "https://pokeapi.co/api/v2"

# Función para manejar requests con retry básico
def fetch_url(url):
    for _ in range(3):
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                return r.json()
        except requests.RequestException as e:
            print(f"Error en la petición: {e}, reintentando...")
            time.sleep(1)
    return None

# 1️⃣ Clasificación por Tipos

def fire_pokemon_kanto():
    """
    a) Cuántos Pokémon de tipo fuego existen en la región de Kanto
    """
    type_data = fetch_url(f"{BASE_URL}/type/fire")
    if not type_data:
        return None

    count = 0
    kanto_ids = range(1, 152)  # IDs de Kanto: 1 a 151
    for p in type_data["pokemon"]:
        poke_url = p["pokemon"]["url"]
        poke_data = fetch_url(poke_url)
        if poke_data and poke_data["id"] in kanto_ids:
            count += 1
    return count

def water_pokemon_high_height(min_height=10):
    """
    b) Nombres de Pokémon tipo agua con altura > min_height
    """
    type_data = fetch_url(f"{BASE_URL}/type/water")
    if not type_data:
        return []

    result = []
    for p in type_data["pokemon"]:
        poke_data = fetch_url(p["pokemon"]["url"])
        if poke_data and poke_data["height"] > min_height:
            result.append(poke_data["name"])
    return result

# 2️⃣ Evoluciones

def evolution_chain(pokemon_name):
    """
    a) Cadena evolutiva de un Pokémon
    """
    poke_data = fetch_url(f"{BASE_URL}/pokemon-species/{pokemon_name.lower()}")
    if not poke_data or not poke_data.get("evolution_chain"):
        return []
    
    chain_url = poke_data["evolution_chain"]["url"]
    chain_data = fetch_url(chain_url)
    
    evolutions = []
    def traverse(chain):
        evolutions.append(chain["species"]["name"])
        for evo in chain.get("evolves_to", []):
            traverse(evo)
    
    traverse(chain_data["chain"])
    return evolutions

def electric_no_evolutions():
    """
    b) Pokémon de tipo eléctrico sin evoluciones
    """
    type_data = fetch_url(f"{BASE_URL}/type/electric")
    if not type_data:
        return []

    result = []
    for p in type_data["pokemon"]:
        species_data = fetch_url(p["pokemon"]["url"].replace("/pokemon/", "/pokemon-species/"))
        if species_data and not species_data.get("evolves_from_species") and not species_data.get("evolution_chain")["chain"].get("evolves_to"):
            result.append(species_data["name"])
    return result

# 3️⃣ Estadísticas de Batalla

def strongest_attack_johto():
    """
    a) Pokémon con mayor ataque base en Johto (ID 152-251)
    """
    max_attack = 0
    best_pokemon = None
    for poke_id in range(152, 252):
        poke_data = fetch_url(f"{BASE_URL}/pokemon/{poke_id}")
        if not poke_data:
            continue
        for stat in poke_data["stats"]:
            if stat["stat"]["name"] == "attack":
                if stat["base_stat"] > max_attack:
                    max_attack = stat["base_stat"]
                    best_pokemon = poke_data["name"]
    return best_pokemon, max_attack

def fastest_non_legendary():
    """
    b) Pokémon con la velocidad más alta que no sea legendario
    """
    max_speed = 0
    fastest_pokemon = None
    # IDs hasta 1010 (aprox hasta la última generación)
    for poke_id in range(1, 1011):
        poke_data = fetch_url(f"{BASE_URL}/pokemon/{poke_id}")
        if not poke_data:
            continue
        species_data = fetch_url(f"{BASE_URL}/pokemon-species/{poke_id}")
        if not species_data or species_data.get("is_legendary"):
            continue
        for stat in poke_data["stats"]:
            if stat["stat"]["name"] == "speed" and stat["base_stat"] > max_speed:
                max_speed = stat["base_stat"]
                fastest_pokemon = poke_data["name"]
    return fastest_pokemon, max_speed

# 4️⃣ Extras

def common_plant_habitat():
    """
    a) Hábitat más común entre Pokémon de tipo planta
    """
    type_data = fetch_url(f"{BASE_URL}/type/grass")
    habitat_count = {}
    for p in type_data["pokemon"]:
        species_data = fetch_url(p["pokemon"]["url"].replace("/pokemon/", "/pokemon-species/"))
        if not species_data:
            continue
        habitat = species_data["habitat"]["name"] if species_data.get("habitat") else "unknown"
        habitat_count[habitat] = habitat_count.get(habitat, 0) + 1
    sorted_habitat = sorted(habitat_count.items(), key=lambda x: x[1], reverse=True)
    return sorted_habitat[0] if sorted_habitat else ("unknown", 0)

def lightest_pokemon():
    """
    b) Pokémon con menor peso registrado
    """
    min_weight = float('inf')
    lightest = None
    for poke_id in range(1, 1011):
        poke_data = fetch_url(f"{BASE_URL}/pokemon/{poke_id}")
        if not poke_data:
            continue
        if poke_data["weight"] < min_weight:
            min_weight = poke_data["weight"]
            lightest = poke_data["name"]
    return lightest, min_weight

# Ejemplo de ejecución

if __name__ == "__main__":
    print("🔥 Pokémon tipo fuego en Kanto:", fire_pokemon_kanto())
    print("💧 Pokémon tipo agua con altura >10:", water_pokemon_high_height())
    print("🌱 Cadena evolutiva de Bulbasaur:", evolution_chain("bulbasaur"))
    print("⚡ Pokémon eléctrico sin evoluciones:", electric_no_evolutions())
    print("💪 Pokémon con mayor ataque en Johto:", strongest_attack_johto())
    print("⚡ Pokémon más rápido no legendario:", fastest_non_legendary())
    print("🌿 Hábitat más común de tipo planta:", common_plant_habitat())
    print("🏋️ Pokémon más ligero:", lightest_pokemon())

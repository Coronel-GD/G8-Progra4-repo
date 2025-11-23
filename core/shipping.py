from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.conf import settings

# Ubicación del depósito central (Ejemplo: Obelisco, Buenos Aires)
WAREHOUSE_LOCATION = Point(-58.3816, -34.6037)

from math import radians, cos, sin, asin, sqrt

def calculate_distance(user_location):
    """
    Calcula la distancia en km desde el depósito hasta el usuario usando Haversine.
    """
    if not user_location:
        return None
    
    # Coordenadas del depósito
    lon1, lat1 = WAREHOUSE_LOCATION.x, WAREHOUSE_LOCATION.y
    # Coordenadas del usuario
    lon2, lat2 = user_location.x, user_location.y
    
    # Convertir a radianes
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    
    # Fórmula Haversine
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radio de la Tierra en km
    
    return round(c * r, 2) 

def calculate_shipping_cost(distance_km):
    """
    Calcula el costo de envío basado en distancia.
    Lógica propia simple.
    """
    if distance_km is None:
        return 0
    
    base_cost = 500  # Costo base
    cost_per_km = 50 # Costo por km
    
    total = base_cost + (distance_km * cost_per_km)
    return round(total, 2)

class ShippingProvider:
    """
    Clase base para proveedores de envío (Andreani, Correo Argentino, OCA)
    """
    def get_quote(self, weight, volume, destination):
        raise NotImplementedError

class AndreaniProvider(ShippingProvider):
    def get_quote(self, weight, volume, destination):
        # Implementar API de Andreani
        pass

class CorreoArgentinoProvider(ShippingProvider):
    def get_quote(self, weight, volume, destination):
        # Implementar API de Correo Argentino
        pass

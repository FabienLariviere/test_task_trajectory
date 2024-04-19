from math import sin, cos, radians, atan2, sqrt
from typing import Literal, Iterable

import requests


class Vehicle:
    id: int
    name: str
    model: str
    year: int
    color: str
    price: int
    latitude: float
    longitude: float

    def __init__(
            self, id: int | None, name: str, model: str, year: int, color: str, price: int, latitude: float, longitude: float
    ):
        self.id = id
        self.name = name
        self.model = model
        self.year = year
        self.color = color
        self.price = price
        self.latitude = latitude
        self.longitude = longitude

    def model_dump(self) -> dict:
        return self.__dict__

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}: {self.name} {self.model} {self.year} {self.color} {self.price}>'


class VehicleManager:
    def __init__(self, url: str, session: requests.Session = None):
        self._session = session if session is not None else requests.Session()

        self.url = url.rstrip('/')

    def _request(self, method: Literal['GET', 'POST', 'PUT', 'DELETE'], endpoint: str,
                 **kwargs) -> dict | None:

        with self._session.request(method, self.url+endpoint, **kwargs) as r:
            if 200 > r.status_code >= 400:
                # можно сделать кастомный эксепшен
                raise ConnectionError(r.status_code, r.content)
            if r.status_code in [200, 201]:
                return r.json()
        return None

    def _parse_obj(self, obj: dict | Iterable) -> Vehicle | list[Vehicle]:
        if isinstance(obj, list | tuple):
            return list(map(self._parse_obj, obj))
        elif isinstance(obj, dict):
            try:
                return Vehicle(**obj)
            except TypeError:
                raise TypeError(type(obj), obj)
        else:
            raise TypeError(type(obj), obj)

    def add_vehicle(self, vehicle: Vehicle) -> Vehicle:
        return self._parse_obj(self._request('POST', '/vehicles', data=vehicle.model_dump()))

    def get_vehicles(self) -> list[Vehicle]:
        return self._parse_obj(self._request('GET', '/vehicles'))

    def filter_vehicles(self, params: dict) -> list[Vehicle]:
        vehicles = self.get_vehicles()
        if not params:
            return vehicles

        for vehicle in tuple(vehicles):
            for key, value in params.items():
                attr_value = getattr(vehicle, key)
                if attr_value != value:
                    vehicles.remove(vehicle)

        return vehicles

    def get_vehicle(self, vehicle_id: int) -> Vehicle:
        return self._parse_obj(self._request('GET', f'/vehicles/{vehicle_id}'))

    def update_vehicle(self, vehicle: Vehicle) -> Vehicle:
        upd_vehicle = self.get_vehicle(vehicle.id)
        for key, value in vehicle.model_dump().items():
            setattr(upd_vehicle, key, value)

        return self._parse_obj(
            self._request('PUT', f'/vehicles/{vehicle.id}', data=upd_vehicle.model_dump())
        )

    def delete_vehicle(self, id: int) -> None:
        return self._request('DELETE', f'/vehicles/{id}')

    def get_distance(self, id1, id2) -> float:
        vehicle1, vehicle2 = self.get_vehicle(id1), self.get_vehicle(id2)
        return calculate_distance(
            (radians(vehicle1.latitude), radians(vehicle1.longitude)),
            (radians(vehicle2.latitude), radians(vehicle2.longitude))
        )

    def get_nearest_vehicle(self, id: int) -> Vehicle:
        point_vehicle = self.get_vehicle(id)
        vehicles = self.get_vehicles()

        vehicle_with_distance = {
            vehicle: calculate_distance(
                (radians(point_vehicle.latitude), radians(point_vehicle.longitude)),
                (radians(vehicle.latitude), radians(vehicle.longitude))
            ) for vehicle in vehicles if vehicle.id != point_vehicle.id
        }

        return tuple(sorted(vehicle_with_distance.items(), key=lambda v: v[1]))[0][0]


def calculate_distance(pos1: tuple[float, float], pos2: tuple[float, float]) -> float:
    """
    Calculate the distance between two points

    :param pos1: tuple[radians(float, float)]
    :param pos2: tuple[radians(float, float)]
    :return: meters
    """

    R = 6371.0

    lat1, lon1 = pos1
    lat2, lon2 = pos2

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) * sin(dlat / 2) + cos(lat1) * cos(lat2) * sin(dlon / 2) * sin(dlon / 2)
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c * 1000

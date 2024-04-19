from src.models import VehicleManager, Vehicle

if __name__ == '__main__':
    manager = VehicleManager("https://test.tspb.su/test-task")
    manager.get_vehicles()
    manager.filter_vehicles({"name": "Toyota"})
    manager.get_vehicle(1)
    manager.add_vehicle(
        Vehicle(
            name='Toyota',
            model='Camry',
            year=2021,
            color='red',
            price=21000,
            latitude=55.753215,
            longitude=37.620393
        )
    )
    manager.update_vehicle(
        Vehicle(
            id=1,
            name='Toyota',
            model='Camry',
            year=2021,
            color='red',
            price=21000,
            latitude=55.753215,
            longitude=37.620393
        )
    )
    manager.delete_vehicle(1)
    manager.get_distance(1, 2)
    manager.get_nearest_vehicle(1)

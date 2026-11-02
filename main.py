from pydantic import BaseModel
from typing import Dict, List

import json


class Parameters(BaseModel):
    apartments_json_path: str = 'data/apartments.json'
    tenants_json_path: str = 'data/tenants.json'
    transfers_json_path: str = 'data/transfers.json'
    bills_json_path: str = 'data/bills.json'


class Room(BaseModel):
    name: str
    area_m2: float


class Apartment(BaseModel):
    key: str
    name: str
    location: str
    area_m2: float
    rooms: Dict[str, Room]

    @staticmethod
    def from_json_file(file_path: str) -> Dict[str,'Apartment']:
        data = None
        with open(file_path, 'r') as file:
            data = json.load(file)
        assert isinstance(data, dict), "Expected a dictionary of apartments"
        return {key: Apartment(**apartment) for key, apartment in data.items()}

    
class Tenant(BaseModel):
    name: str
    apartment: str
    room: str
    rent_pln: float
    deposit_pln: float
    date_agreement_from: str
    date_agreement_to: str

    @staticmethod
    def from_json_file(file_path: str) -> Dict[str,'Tenant']:
        data = None
        with open(file_path, 'r') as file:
            data = json.load(file)
        assert isinstance(data, dict), "Expected a dictionary of tenants"
        return {key: Tenant(**tenant) for key, tenant in data.items()}
    

class Transfer(BaseModel):
    amount_pln: float
    date: str
    settlement_year: int | None
    settlement_month: int | None
    tenant: str

    @staticmethod
    def from_json_file(file_path: str) -> List['Transfer']:
        data = None
        with open(file_path, 'r') as file:
            data = json.load(file)
        assert isinstance(data, list), "Expected a list of transfers"
        return [Transfer(**transfer) for transfer in data]


class Bill(BaseModel):
    amount_pln: float
    date_due: str
    apartment: str
    settlement_year: int
    settlement_month: int
    type: str

    @staticmethod
    def from_json_file(file_path: str) -> List['Bill']:
        data = None
        with open(file_path, 'r') as file:
            data = json.load(file)
        assert isinstance(data, list), "Expected a list of bills"
        return [Bill(**bill) for bill in data]


class ApartmentSettlement(BaseModel):
    apartment: str
    settlement_year: int
    settlement_month: int
    bills_total_pln: float
    rent_total_pln: float
    amount_due_pln: float


class Manager:
    def __init__(self, parameters: Parameters):
        self.parameters = parameters 

        self.apartments = {}
        self.tenants = {}
        self.transfers = []
        self.bills = []
       
        self.load_data()

    def load_data(self):
        self.apartments = Apartment.from_json_file(self.parameters.apartments_json_path)
        self.tenants = Tenant.from_json_file(self.parameters.tenants_json_path)
        self.transfers = Transfer.from_json_file(self.parameters.transfers_json_path)
        self.bills = Bill.from_json_file(self.parameters.bills_json_path)


if __name__ == '__main__':
    parameters = Parameters()
    manager = Manager(parameters)

    print("=" * 50)
    print("APARTMENTS")
    print("=" * 50)

    for apartment in manager.apartments.values():
        print(f"\n[{apartment.key}] {apartment.name} — {apartment.location} ({apartment.area_m2:.0f} m2)")

        print("  Rooms:")
        for room in apartment.rooms.values():
            print(f"    - {room.name} ({room.area_m2:.0f} m2)")

        print("  Bills:")
        for bill in manager.bills:
            if bill.apartment == apartment.key:
                print(f"    - {bill.type:<10} {bill.amount_pln:>8,.2f} zł  due {bill.date_due}  [{bill.settlement_year}-{bill.settlement_month:02d}]")

    print("\n" + "=" * 50)
    print("TENANTS")
    print("=" * 50)

    for tenant in manager.tenants.values():
        print(f"\n{tenant.name}  ->  {tenant.apartment} / {tenant.room}")
        print(f"  Rent: {tenant.rent_pln:,.2f} zł   Deposit: {tenant.deposit_pln:,.2f} zł")
        print(f"  Agreement: {tenant.date_agreement_from} -> {tenant.date_agreement_to}")

        print("  Transfers:")
        for transfer in manager.transfers:
            if transfer.tenant == tenant.name:
                print(f"    - {transfer.amount_pln:>8,.2f} zł  on {transfer.date}  [{transfer.settlement_year}-{transfer.settlement_month:02d}]")
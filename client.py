# client.py
"""
Simple client program that uses the Requests library to interact with the Flask
RESTful API for banks.

Make sure the Flask app is running (e.g., `python app.py`) before using this.
"""

import requests

BASE_URL = "http://localhost:5000/api/banks"


def list_banks():
    """Fetch and print all banks from the API."""
    response = requests.get(BASE_URL)
    response.raise_for_status()  # Raise an error if the response is not 2xx

    banks = response.json()
    print("Banks from API:")
    for bank in banks:
        print(f"- {bank['id']}: {bank['name']} ({bank['location']})")


def create_bank(name, location):
    """Create a new bank via the API."""
    payload = {"name": name, "location": location}
    response = requests.post(BASE_URL, json=payload)
    response.raise_for_status()
    bank = response.json()
    print("Created bank:", bank)
    return bank["id"]


def update_bank(bank_id, name=None, location=None):
    """
    Update an existing bank via the API.

    Only the fields provided (name/location) will be updated.
    """
    payload = {}
    if name is not None:
        payload["name"] = name
    if location is not None:
        payload["location"] = location

    response = requests.put(f"{BASE_URL}/{bank_id}", json=payload)
    response.raise_for_status()
    print("Updated bank:", response.json())


def delete_bank(bank_id):
    """Delete a bank via the API."""
    response = requests.delete(f"{BASE_URL}/{bank_id}")
    response.raise_for_status()
    print(f"Deleted bank with id {bank_id}")


if __name__ == "__main__":
    # Example usage for manual testing of the API.
    # In a real application, you might parse command-line arguments instead.
    print("=== API Client Demo ===")

    # 1. Create a new bank
    new_id = create_bank("Demo Bank", "Athens")

    # 2. List all banks
    list_banks()

    # 3. Update that bank
    update_bank(new_id, location="Thessaloniki")

    # 4. List again to see the change
    list_banks()

    # 5. Delete the bank
    delete_bank(new_id)

    # 6. List again to confirm deletion
    list_banks()

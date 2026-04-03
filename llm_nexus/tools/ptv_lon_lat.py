import logging
from os import getenv
from typing import List
from langchain_core.tools import tool
from pydantic import BaseModel, Field
import requests
import math
 
PTV_XLOCATE_URL = getenv("PTV_XLOCATE_URL")


PTV_EARTH_RADIUS = 6371000.785  # PTV's fixed sphere radius in meters

class AddressClass(BaseModel):
    country_code: str = Field(description="Country code (e.g., 'GB')")
    postal_code: str = Field(description="Postal code (e.g., 'ST5 7RB')")
    city: str = Field(description="City name (e.g., 'Newcastle-under-Lyme')")
    street: str = Field(description="Street name (e.g., 'Parkhouse Rd E')")
    house_number: str = Field(description="House number (e.g., '5')")

def ptv_mercator_to_wgs84(x: float, y: float) -> List[float, float]:
    """
    Convert PTV Mercator coordinates to WGS84 decimal degrees.
    
    Args:
        x: PTV Mercator X (easting)  → longitude
        y: PTV Mercator Y (northing) → latitude
    
    Returns:
        [longitude, latitude] in decimal degrees
    """
    lon = math.degrees(x / PTV_EARTH_RADIUS)
    lat = math.degrees(2 * math.atan(math.exp(y / PTV_EARTH_RADIUS)) - math.pi / 2)
    
    return [lon, lat]

@tool
def find_latitude_longitude(
    country_code = None, postal_code = None, city = None, street = None, house_number = None, **kwargs) -> str:
    """
    Call PTV xLocate API for a single OD pair. Returns (km, minutes, cost) or None.
    If user asks to find an address, but doesn't provide all the details, call basic_llm to extract missing details from the query
    and then call this function again with all the details.

    Args:
        country_code (str): Country code (e.g., "GB").
        postal_code (str): Postal code (e.g., "ST5 7RB").
        city (str): City name (e.g., "Newcastle-under-Lyme").
        street (str): Street name (e.g., "Parkhouse Rd E").
        house_number (str): House number (e.g., "5").
    """
    logging.info(f"find_latitude_longitude called with: country_code={country_code}, postal_code={postal_code}, city={city}, street={street}, house_number={house_number}")
    build_adrs = {}
    if not all([country_code, postal_code, city, street, house_number]):

        from llm_nexus import llm_basic
        response: AddressClass = llm_basic.with_structured_output(AddressClass).invoke(
            f"Extract the following address details from the query: country code, postal code, city, street, house number. "
            f"Only return the details that are missing. If a detail is already provided, do not return it. "
            f"Query: {kwargs.get('query', '')}"
        )

        if country_code or response.country_code:
            build_adrs['country'] = country_code or response.country_code
        
        if postal_code or response.postal_code:
            build_adrs['postCode'] = postal_code or response.postal_code

        if city or response.city:
            build_adrs['city'] = city or response.city or ''

        if street or response.street:
            build_adrs['street'] = street or response.street or ''
            
        if house_number or response.house_number:
            build_adrs['houseNumber'] = house_number or response.house_number or ''

    if not all([postal_code, country_code]):
        return 'Not enough address details provided. Please provide at least a postal code and country code, or ensure they can be extracted from the query.'

    dct_address = {
        "addr": {
            "country": build_adrs.get("country"),
            "postCode": build_adrs.get("postCode"),
            "city": build_adrs.get("city", ""),
            "city2": "",
            "street": build_adrs.get("street", ""),
            "houseNumber": build_adrs.get("houseNumber", "")
        },
        "options": [],
        "sorting": [],
        "additionalFields": [],
        "callerContext": {
            "properties": [
            {
                "key": "CoordFormat",
                "value": "PTV_MERCATOR"
            },
            {
                "key": "Profile",
                "value": "default"
            }
            ]
        }
        }
    
    try:
        response = requests.post(
            PTV_XLOCATE_URL,
            json=dct_address,
            headers={"Content-Type": "application/json"},
            timeout=60
        )

        response.raise_for_status()
        data = response.json()

        point = data['resultList'][0]['coordinates']['point']
        return f"{','.join(ptv_mercator_to_wgs84(point['x'], point['y']))}"
    
    except requests.exceptions.RequestException as e:
        print("---------------------------")
        print(f"PTV API error: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Response body: {e.response.text[:500]}")
        print("---------------------------")
        return str(e)

    except Exception as e:
        print("---------------------------")
        print(f"Unexpected error: {e}")
        print("---------------------------")
        return str(e)

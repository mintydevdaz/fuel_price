import sys

import pandas as pd
import requests
from links import stations, urls


def main():
    items = []
    for url in urls:

        # Get HTML and JSON response
        r = get_html_response(url)
        json = get_json(r)

        # Append if JSON returns single station
        if len(json) == 1:
            items.append(json[0])
        else:
            # Append specific stations if JSON contains multiple stations
            items.extend(
                j for j in json if j.get("ServiceStationID") in stations.values()
            )

    # Extracts prices and fuel types from JSON
    for item in items:
        prices = clean(current_prices(item))
        print(station_address(item))
        print(table(prices))
        print("-" * 40)


def get_html_response(url: str) -> requests.models.Response:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        }
        r = requests.get(url, headers=headers, timeout=5)
        r.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        sys.exit(f"HTTP error occurred: \n'{http_err}'")
    except requests.exceptions.Timeout as timeout_err:
        sys.exit(f"Timeout error occurred: \n'{timeout_err}'")
    except Exception as err:
        sys.exit(f"Error occurred: \n'{err}'")
    return r


def get_json(response: requests.models.Response) -> list:
    try:
        r = response.json()
    except requests.exceptions.JSONDecodeError as err:
        sys.exit(f"Unable to grab JSON file: \n'{err}'")
    return r


def current_prices(json: dict) -> list[str]:
    prices = json["Prices"]
    r = []
    for price in prices:
        r.extend(iter(price.values()))
    return r


def clean(data: list[str]) -> list:
    """Joins fuel type with it's current price"""
    fuel_type = data[::4]
    price = data[1::4]
    return list(zip(fuel_type, price))


def station_address(json: dict) -> str:
    return (
        f"ID: {json['ServiceStationID']}\n{json['Name']} | {json['Address']}"  # noqa
    )


def table(prices: list) -> pd.DataFrame:
    return pd.DataFrame(prices, columns=["Fuel Type", "Price/L"])


if __name__ == "__main__":
    main()

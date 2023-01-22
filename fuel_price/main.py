import pandas as pd
import requests

from links import urls, stations


def main():
    items = []
    # Get JSON from multiple URLs
    for url in urls:

        # Request HTML
        r = get_request(url)

        # Get JSON
        json = get_json(response=r)

        # Append if JSON returns single station
        if len(json) == 1:
            items.append(json[0])
        else:
            # Append specific stations if JSON contains multiple stations
            items.extend(j for j in json if j.get('ServiceStationID') in stations.values())  # noqa

    # Extracts prices and fuel types from JSON
    for item in items:
        prices = clean(current_prices(item))
        print(location(item))
        print(table(prices))
        print('-'*40)


def get_request(url: str):
    '''Get request from Fuel Check NSW API'''
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"}  # noqa
        r = requests.get(url, headers=headers, timeout=6)
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f'Error loading webpage: {e}')
    except requests.exceptions.Timeout as e:
        print(f'Request Timeout: {e}')
    return r


def get_json(response: requests.models.Response) -> list:
    '''Parse JSON'''
    try:
        r = response.json()
    except requests.exceptions.JSONDecodeError as e:
        print(f'Unable to grab JSON file: {e}')
    return r


def current_prices(json: dict) -> list[str]:
    '''Get fuel prices from JSON'''
    prices = json['Prices']
    r = []
    for price in prices:
        r.extend(iter(price.values()))
    return r


def clean(data: list[str]) -> list:
    '''Joins fuel type with it's current price'''
    fuel_type = data[::4]
    price = data[1::4]
    return list(zip(fuel_type, price))


def location(json: dict) -> str:
    '''Show address of fuel station'''
    return f"{json['Name']} | {json['Address']} | ID: {json['ServiceStationID']}"  # noqa


def table(prices: list) -> pd.DataFrame:
    '''Convert fuel types and prices into a Pandas Dataframe'''
    return pd.DataFrame(prices, columns=['Fuel Type', 'Price/L'])


if __name__ == '__main__':
    main()

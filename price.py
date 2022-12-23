import requests
import pandas as pd


url = "https://api.onegov.nsw.gov.au/FuelCheckApp/v1/fuel/prices/bylocation?bottomLeftLatitude=-33.75340696086609&bottomLeftLongitude=151.1616313779297&topRightLatitude=-33.68887075066809&topRightLongitude=151.26188162207032&fueltype=E10-U91&brands=EG%20Ampol"  # noqa


def main():
    # Request HTML
    r = get_request()

    # Get JSON
    json = get_json(response=r)

    # Get fuel types and their current price
    prices = clean(current_prices(json))

    # Show fuel station location and its daily prices
    print(location(json))
    print(table(prices))
    print('--------------------------------')


def get_request():
    '''Get request from Fuel Check NSW API'''
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"}  # noqa
        r = requests.get(url, headers=headers, timeout=3)
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f'Error loading webpage: {e}')
    except requests.exceptions.Timeout as e:
        print(f'Request Timeout: {e}')
    return r


def get_json(response: requests.models.Response) -> list[dict]:
    '''Parse JSON'''
    try:
        r = response.json()
    except requests.exceptions.JSONDecodeError as e:
        print(f'Unable to grab JSON file: {e}')
    return r


def current_prices(json: list[dict]) -> list[str]:
    '''Get fuel prices from JSON'''
    prices = json[0]['Prices']
    r = []
    for price in prices:
        r.extend(iter(price.values()))
    return r


def clean(data: list[str]) -> list:
    '''Joins fuel type with it's current price'''
    fuel_type = data[::4]
    price = data[1::4]
    return list(zip(fuel_type, price))


def location(json: list[dict]) -> str:
    '''Show address of fuel station'''
    return f"{json[0]['Name']} | {json[0]['Address']}"


def table(prices: list) -> pd.DataFrame:
    return pd.DataFrame(prices, columns=['Fuel Type', 'Price/L'])


if __name__ == '__main__':
    main()

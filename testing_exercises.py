import requests
import json


def get_countries():
    headers = {'Content-Type': 'application/json'}
    api_url = "https://restcountries.eu/rest/v2/all"

    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        return json.loads(response.content.decode('utf-8'))
    else:
        return None


def get_country_code(countries: list, country_name: str):
    for country in countries:
        if country['name'] == country_name:
            return country['alpha3Code']
    return None


def get_country_currency(countries: list, country_name: str):
    for country in countries:
        if country['name'] == country_name:
            return country['currencies'][0]['code']
    return None


def transform(name: str, get_countries=get_countries):
    countries = get_countries()
    code = get_country_code(countries, name)
    currency = get_country_currency(countries, name)

    return {"name": name, "country_code": code, "currency_code": currency}


def show_country_info(get_countries=get_countries, input=input):
    idx = 0
    countries = get_countries()

    for country in countries:
        print(idx, country['name'])
        idx += 1

    print()

    selected_country_idx = int(input("Please choose a country: "))
    name = countries[selected_country_idx]['name']
    result = transform(name)
    return result


def should_return_correct_country_info():
    def mock_get_countries():
        return [{
            'name': 'United Kingdom of Great Britain and Northern Ireland',
            'currencies': [{'code': 'GBP'}],
            'alpha3Code': 'GBR'
        }]

    def mock_input(prompt):
        return 0

    expected = {'name': 'United Kingdom of Great Britain and Northern Ireland',
                'country_code': 'GBR', 'currency_code': 'GBP'}
    actual = show_country_info(mock_get_countries, mock_input)

    assert expected == actual
    print('Test should_return_correct_country_info Passed')


def should_return_correct_country_code():
    countries = [{
        'name': 'United Kingdom of Great Britain and Northern Ireland',
        'alpha3Code': 'GBR'
    }]
    name = 'United Kingdom of Great Britain and Northern Ireland'

    expected = 'GBR'
    actual = get_country_code(countries, name)
    assert expected == actual
    print("Test country code passed")


def should_return_correct_country_currency():
    countries = [{
        'name': 'United Kingdom of Great Britain and Northern Ireland',
        'currencies': [{'code': 'GBP'}]
    }]
    name = 'United Kingdom of Great Britain and Northern Ireland'

    expected = 'GBP'
    acctual = get_country_currency(countries, name)
    assert expected == acctual
    print("Test country currency passed")


def should_transform_response_to_dictionary():
    def mock_get_country():
        return [{
            'name': 'United Kingdom of Great Britain and Northern Ireland',
            'currencies': [{'code': 'GBP'}],
            'alpha3Code': 'GBR'
        }]
    name = 'United Kingdom of Great Britain and Northern Ireland'
    expected = {"name": 'United Kingdom of Great Britain and Northern Ireland',
                "country_code": "GBR", "currency_code": "GBP"}
    acctual = transform(name, mock_get_country)
    assert expected == acctual
    print("Test country to dictionary passed")


should_return_correct_country_info()
should_return_correct_country_code()
should_return_correct_country_currency()
should_transform_response_to_dictionary()

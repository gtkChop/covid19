from covid.lib import helper as h, errors
from dateutil.parser import parse


def get_all_records_by_country(instance, show_geometry=False):
    """
    Collect all confirmed, recovered and deaths for all the countries
    :param instance: class instance
    :param show_geometry: boolean (if true show a multi polygon coordinates)
    :return: dict
    """
    result = dict()

    for _action in instance._actions_files.keys():
        reader = getattr(instance, _action)
        # Dict reader of the respective action
        for row in reader:
            # Country id
            _country = h.convert_label_to_id(row.get('Country/Region'))
            # Latest value i.e. last column of the ordered dict
            _key = list(row.keys())[-1]
            _val = int(row.get(_key))

            # Aggregation
            if _country in result:
                _cnty_data = result.get(_country)
                if _action in _cnty_data:
                    _cnty_data[_action] += _val
                else:
                    _cnty_data[_action] = _val
            else:
                # Data model for the new record
                result[_country] = dict()
                result[_country][_action] = _val
                result[_country]['label'] = row.get('Country/Region')
                result[_country]['last_updated'] = str(parse(_key))
                result[_country]['lat'] = row.get('Lat')
                result[_country]['long'] = row.get('Long')
                if show_geometry:
                    result[_country]['geometry'] = instance.get_polygon_for_country(row.get('Country/Region'))
    return result


def get_all_records_by_provinces(instance):
    """
    Collect all the data if the province column is not null and get corresponding latitude and longitude data
    :param instance: class instance
    :return: dict
    """

    result = dict()

    for _action in instance._actions_files.keys():
        reader = getattr(instance, _action)
        for row in reader:
            _province_label = row.get('Province/State')
            if _province_label:
                _province = h.convert_label_to_id(_province_label)
                _key = list(row.keys())[-1]
                _val = int(row.get(_key))
                # Aggregation
                if _province in result:
                    _province_data = result.get(_province)
                    if _action in _province_data:
                        _province_data[_action] += _val
                    else:
                        _province_data[_action] = _val
                else:
                    # Data model for the new record
                    result[_province] = dict()
                    result[_province][_action] = _val
                    result[_province]['label'] = _province_label
                    result[_province]['country'] = row.get('Country/Region')
                    result[_province]['lat'] = row.get('Lat')
                    result[_province]['long'] = row.get('Long')
                    result[_province]['last_updated'] = str(parse(_key))

    return result


def show_available_countries(instance):
    """
    Show all the available countries
    :param instance: class instance
    :return: dict
    """

    countries = []

    for _item in instance._actions_files.keys():
        reader = getattr(instance, _item)
        for row in reader:
            _ctry = dict(row).get("Country/Region")
            if _ctry not in countries:
                countries.append(_ctry)
    return countries


def show_available_province(instance):
    """
    Show all the available provinces/state
    :param instance: class instance
    :return: dict
    """
    regions = []

    for _item in instance._actions_files.keys():
        reader = getattr(instance, _item)
        for row in reader:
            province = dict(row).get("Province/State")
            if province and (province not in regions):
                regions.append(province)
    return regions


def filter_by_country(instance, country, show_geometry=False):
    """
    Show the record given country name
    :param instance: instance of the class
    :param country: str
    :param show_geometry: boolean
    :return: dict
    """
    if not country:
        raise errors.ValidationError("Missing parameter country")

    _countries = get_all_records_by_country(instance)
    country_id = h.convert_label_to_id(country)

    for _country in _countries:
        if country_id == _country:
            res = _countries.get(_country)
            if show_geometry:
                res['geometry'] = instance.get_polygon_for_country(country)
                return res
            else:
                return res
    raise errors.CountryNotFound("Given country not found. "
                                 "Run available countries method to see all available countries")


def filter_by_province(instance, province):
    """
    Show record for the given province.
    :param instance: instance of the class
    :param province: str
    :return: dict
    """
    if not province:
        raise errors.ValidationError("Missing value province")

    _provinces = get_all_records_by_provinces(instance)
    province_id = h.convert_label_to_id(province)

    for _province in _provinces:
        if province_id == _province:
            res = _provinces.get(province_id)
            return res

    raise errors.ProvinceNotFound("Given province not found. "
                                  "Run available provinces method to see all available provinces")


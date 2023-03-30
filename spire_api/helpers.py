from datetime import datetime
from loguru import logger
import json
from nested_lookup import nested_lookup as nl
from gql import Client
from gql.transport.requests import RequestsHTTPTransport
from requests import exceptions
from collections.abc import MutableMapping


def get_gql_client(settings):
    """ Establishes a gql client
    Returns:
        gql.client
    Raises:
        ConnectionTimeout
    """
    endpoint = settings['endpoint']
    token = settings['token']

    headers = dict()
    headers['Authorization'] = f'Bearer {token}'
    transport = RequestsHTTPTransport(
        url=endpoint,
        headers=headers,
        verify=True,
        retries=3,
        timeout=30)
    try:
        client = Client(transport=transport, fetch_schema_from_transport=True)
    except exceptions.ConnectTimeout as e:
        logger.error(e)
        raise
    return client


def get_vessels_v2_members():
    """ Get a list of column names and the data types
    Returns:
        A list of column names and BigQuery data types
    These are added to support saving data that might be captured by a test
        'test_execute_start_time'
        'test_name'
    They can be null / empty string
    """

    return (
        ('node_updateTimestamp', "STRING"),
        ('node_id', "STRING"),
        ('staticData_updateTimestamp', "STRING"),
        ('staticData_timestamp', "STRING"),
        ('mmsi', "string"),
        ('imo', 'string'),
        ('name', 'string'),
        ('callsign', 'string'),
        ('shipType', 'string'),
        ('shipSubType', 'STRING'),
        ('aisClass', 'string'),
        ('flag', 'string'),
        ('length', 'string'),
        ('width', 'string'),
        ('a', 'string'),
        ('b', 'string'),
        ('c', 'string'),
        ('d', 'string'),
        ('lastPositionUpdate_updateTimestamp', "STRING"),
        ('lastPositionUpdate_timestamp', "STRING"),
        ('latitude', 'string'),
        ('longitude', 'string'),
        ('heading', 'string'),
        ('speed', 'string'),
        ('rot', 'string'),
        ('accuracy', 'string'),
        ('maneuver', 'string'),
        ('course', 'string'),
        ('navigationalStatus', 'string'),
        ('collectionType', 'string'),
        ('currentVoyage_updateTimestamp', "STRING"),
        ('currentVoyage_timestamp', "STRING"),
        ('matchedPort_matchScore', 'STRING'),
        ('port_name', 'STRING'),
        ('port_unlocode', 'STRING'),
        ('port_latitude','STRING'),
        ('port_longitude', 'STRING'),
        ('draught', 'string'),
        ('eta', 'string'),
        ('destination', 'string'),
    )


def transform_response_for_loading(response, schema, test_execute_start_time=None):
    """Flattens complex response dictionary
    Args:
        response(dict) - response from GQL Query
        schema(list) - a list of keys and BQ datatypes, can be derived from get_vessels_v2_members
        test_execute_start_time(datetime) - optional
    Returns:
        list of flattend dictionaries
    """
    if not test_execute_start_time:
        test_execute_start_time = datetime.utcnow()

    # flatten the dictionaries and add to flats list
    flats: list = list()
    nodes: list = nl('nodes', response)
    node_list: list = nodes[0]
    for unique_node in node_list:

        flat: dict = dict()
        v2_schema = [i[0] for i in schema]
        for key in v2_schema:
            flat.setdefault(key, '')
        flat['node_updateTimestamp'] = unique_node['updateTimestamp']
        flat['node_id'] = unique_node['id']

        dimensions: dict = dict()
        try:
            dimensions = unique_node['staticData']['dimensions']
        except KeyError:
            pass  # handle with check for value below

        if dimensions:
            for key, value in dimensions.items():
                if not value:
                    value = ''
                flat[key] = value

        # vessel in node
        vessel: dict = unique_node['staticData']
        for k, v in vessel.items():
            if k == "updateTimestamp":
                flat["staticData_updateTimestamp"] = v
            elif k == 'timestamp':
                flat['staticData_timestamp'] = v
            else:
                if not k == 'dimensions':
                    if not v:
                        v = ''
                    flat[k] = v

        # lastPositionUpdate in node
        lastPositionUpdate: dict = dict()
        try:
            lastPositionUpdate: dict = unique_node['lastPositionUpdate']
        except BaseException as e:
            logger.error(e)
            logger.error("Could be there is no lastPositionUpdate")

        if lastPositionUpdate:
            for k, v in lastPositionUpdate.items():
                if k == "updateTimestamp":
                    flat["lastPositionUpdate_updateTimestamp"] = v
                elif k == 'timestamp':
                    flat['lastPositionUpdate_timestamp'] = v
                else:
                    if not v:
                        v = ''
                    flat[k] = v

        # currentVoyage in node
        currentVoyage: dict = dict()
        try:
            currentVoyage = unique_node['currentVoyage']
        except BaseException as e:
            logger.error(e)
            logger.error("Could be there is no currentVoyage")
        if currentVoyage:
            for k, v in currentVoyage.items():
                if k == "updateTimestamp":
                    flat['currentVoyage_updateTimestamp'] = v
                elif k == 'timestamp':
                    flat['currentVoyage_timestamp'] = v
                elif k == 'matchedPort':
                    try:
                        flat['matchedPort_matchScore'] = currentVoyage['matchedPort']['matchScore']
                    except (KeyError, TypeError):
                        continue

                    port: dict = dict()
                    try:
                        port = currentVoyage['port']
                    except (KeyError, TypeError):
                        continue
                    centerPoint: dict = dict()
                    try:
                        centerPoint = port['centerPoint']

                    except (KeyError, TypeError):
                        continue
                    if centerPoint:
                        flat['port_name'] = centerPoint['matchedPort']['name']
                        flat['port_unlocode'] = centerPoint['matchedPort']['unlocode']
                        latitude = centerPoint['latitude']
                        longitude = centerPoint['longitude']
                        flat['matchedPort_latitude'] = latitude
                        flat['matchedPort_long'] = longitude
                else:
                    if not v:
                        v = ''
                    flat[k] = v
        try:
            # in case somehow these got into the dictionary
            del flat['dimensions']
            del flat['currentVoyage']
            del flat['matchedPort']
        except KeyError:
            pass
        flats.append(flat)
    return flats


def insert_into_query_header(query, insert_text=''):
    """Insert text into query header
    Args:
        query(str) - query string
        insert_text(str) - text to insert
    Returns
        new_query(str) - text with insert
    """
    if ')' in query:
        loc = query.find(')')
        # remove the existing )
        tmp: str = query.replace(')', '')
        # add paging elements where the ) once was .. + 1 for some spacing in case
        beginning: str = tmp[:loc]
        end: str = tmp[loc:]
        new_query = beginning + ' ' + insert_text + ' ) ' + end
    else:
        return query
    return new_query


def pretty_string_dict(dictionary, with_empties=True):
    result: str = ''
    if not dictionary:
        return result
    if type(dictionary) != dict:
        return dictionary
    if with_empties:
        result = json.dumps(dictionary, indent=2)
    else:
        tmp_dict: dict = dict()
        for k, v in dictionary.items():
            if v:
                tmp_dict[k] = v
        result = json.dumps(tmp_dict, indent=2)
    return result


def flatten(dictionary, parent_key=False, separator='.'):
    """
    Turn a nested dictionary into a flattened dictionary
    :param dictionary: The dictionary to flatten
    :param parent_key: The string to prepend to dictionary's keys
    :param separator: The string used to separate flattened keys
    :return: A flattened dictionary
    """
    crumbs = True
    items = []
    for key, value in dictionary.items():
        if crumbs: #print('checking:',key)
            new_key = str(parent_key) + separator + key if parent_key else key
            if isinstance(value, MutableMapping):
                if crumbs: #print(new_key,': dict found')
                    if not value.items():
                        if crumbs: #print('Adding key-value pair:',new_key,None)
                            items.append((new_key,None))
                    else:
                        items.extend(flatten(value, new_key, separator).items())
            elif isinstance(value, list):
                if crumbs: #print(new_key,': list found')
                    if len(value):
                        for k, v in enumerate(value):
                            items.extend(flatten({str(k): v}, new_key).items())
                    else:
                        if crumbs: #print('Adding key-value pair:',new_key,None)
                            items.append((new_key,None))
            else:
                if crumbs: #print('Adding key-value pair:',new_key,value)
                    items.append((new_key, value))
    return dict(items)

def get_all_keys(dictionary):
    """
    Get all keys of non-null values from a dictionary
    :param dictionary: The dictionary
    :return: An array of keys
    """
    keys = []
    for k,v in dictionary.items():
        if v:
            keys.append(k)
    return keys
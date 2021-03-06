import sqlite3 as sqlite
import time

from collections import namedtuple

import requests
import yaml


Response = namedtuple('Response', ['url', 'status', 'time'])
Slo = namedtuple('Slo', ['url', 'successful_responses', 'fast_responses'])


def get_configurations(filename):
    """ Function that reads the configurations file and invokes the parser
        function

    Args:
        filename: Name of the configurations file

    Returns:
        A list of parsed SLOs. Check parse_into_slo_list for more details

    """
    with open(filename, 'r') as stream:
        return parse_into_slo_list(stream)


def parse_into_slo_list(buffer):
    """ Function that parses a buffer into a list of SLOs

    Args:
        buffer: Buffer which will be parsed

    Returns:
        A list of SLOs. Each SLO has a URL, and SLIs for both successful
        and fast responses.

    """
    slos = []
    for slo in yaml.load(buffer)['SLOs']:
        slos.append(
                    Slo(slo['url'],
                        float(slo['successful-responses-SLO']),
                        float(slo['fast-responses-SLO'])
                        )
                    )
    return slos


def do_requests(urls):
    """ Function that do requests to the specified URLs

    Args:
        urls: List of URLs

    Returns:
        A list of responses. Each response has its URL, a status code and
        a response time
    """
    responses = []
    for url in urls:
        start = time.time()
        r = requests.get(url)
        roundtrip = (time.time() - start)*1000
        responses.append(Response(url, r.status_code, roundtrip))
    return responses


def get_slo_urls(slos):
    """ Function that gets the URLs from a list of SLOs

    Args:
        urls: List of SLOs

    Returns:
        A list of urls
    """
    return map(lambda slo: slo.url, slos)


def parse_response(response):
    """ Function that parses the response and checks whether it was
        successful and fast

    Args:
        response: A response object

    Returns:
        A tuple containing the url, and elements that confirm if the
        response was succesful and fast
    """
    url = response.url
    is_successful = 200 <= response.status <= 499
    is_fast = response.time <= 100
    return url, is_successful, is_fast


def recalculate_slis(db_connection, responses):
    """ Function that recalculates the SLIs

    Args:
        db_connection: Database connection
        responses: List of responses to update the database
    """
    c = db_connection.cursor()

    for response in responses:
        url, is_fast, is_successful = parse_response(response)
        c.execute("""
                   INSERT
                       OR IGNORE
                   INTO
                       slis (url, successful_responses,
                             fast_responses, total_responses
                             )
                   VALUES
                       (?,0,0,0)
                  """,
                  (url,)
                  )
        c.execute("""
                  UPDATE slis
                  SET
                      successful_responses=successful_responses+?,
                      fast_responses=fast_responses+?,
                      total_responses=total_responses+1
                  WHERE
                      url=?
                  """,
                  (is_successful, is_fast, url)
                  )
    db_connection.commit()


def get_slos_from_db(db_connection):
    """ Function that gets SLOs from database

    Returns:
        List of SLOs
    """
    c = db_connection.cursor()
    c.execute("SELECT url, successful_responses/total_responses, fast_responses/total_responses FROM slis")

    return c.fetchall()


def get_db_connection():
    """ Function that gets a database connection

    Returns:
        A database connection
    """
    conn = sqlite.connect('slis.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS slis
                         (url text primary key not null, successful_responses int, fast_responses int, total_responses int)''')
    conn.commit()
    return conn


def is_fast_enough(url, rate, config_file='config.yaml'):
    """ Checks whether the SLO matches the SLI for speed

    Returns:
        A boolean
    """
    slos = get_configurations(config_file)

    for slo in slos:
        if slo.url == url and rate >= slo.fast_responses:
            return True
    return False


def is_successful_enough(url, rate, config_file='config.yaml'):
    """ Checks whether the SLO matches the SLI for speed

    Returns:
        A boolean
    """
    slos = get_configurations(config_file)

    for slo in slos:
        if slo.url == url and rate >= slo.successful_responses:
            return True
    return False

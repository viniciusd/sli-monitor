import argparse
import os
import sqlite3 as sqlite
import time

from collections import namedtuple
from datetime import datetime

import requests
import yaml


def get_parser():
    parser = argparse.ArgumentParser(description="SLO worker")
    parser.add_argument('--daemon', dest='daemon',
                        default=False, action='store_true',
                        help='Daemonize the process')

    return parser


Response = namedtuple('Response', ['url', 'status', 'time'])
Slo = namedtuple('Slo', ['url', 'successful_responses', 'fast_responses'])


class SloWorker:
    """SloWorker periodically pools URLs to calculate their SLIs
    This class is more of a namespace, given its methods are mostly static.
    These static methods may move to a utils module in the future

    Args:
        refresh_time (int): The refreshing time after which the worker
                            will redo the requests
    """
    def __init__(self, *, refresh_time=None):

        # It checks for None in case os.getenv was used to pass the argument
        # That's why it is not default to 5 already in the definition
        self.refresh_time = 5 if refresh_time is None else refresh_time

    @classmethod
    def get_configurations(cls, filename):
        """ Function that reads the configurations file and invokes the parser
            function

        Args:
            filename: Name of the configurations file

        Returns:
            A list of parsed SLOs. Check parse_into_slo_list for more details

        """
        with open(filename, 'r') as stream:
            return cls.parse_into_slo_list(stream)

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def get_slo_urls(slos):
        """ Function that gets the URLs from a list of SLOs

        Args:
            urls: List of SLOs

        Returns:
            A list of urls
        """
        return map(lambda slo: slo.url, slos)

    @staticmethod
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

    @classmethod
    def recalculate_slis(cls, db_connection, responses):
        """ Function that recalculates the SLIs

        Args:
            db_connection: Database connection
            responses: List of responses to update the database
        """
        c = db_connection.cursor()

        for response in responses:
            url, is_fast, is_successful = cls.parse_response(response)
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

    @staticmethod
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

    def daemonize(self):
        """ Function that daemonizes the worker

        Returns:
            PID of the process

        """
        raise NotImplementedError('Daemon behavior yet not implemented')

    def start(self, config_file='config.yaml'):
        """ Application loop
        It will call the other methods, doing requests peridocally and updating
        the SLIs

        Args:
            config_file: Name of the configuration file
        """
        conn = self.get_db_connection()

        last_read_config = datetime.utcfromtimestamp(0)

        while True:
            last_modified_config = datetime.utcfromtimestamp(
                                                             os.path.getmtime(config_file
                                                                              )
                                                             ) 
            if last_read_config < last_modified_config:
                slos = self.get_configurations(config_file)
                last_read_config = datetime.now()

            self.recalculate_slis(conn,
                                  self.do_requests(self.get_slo_urls(slos))
                                  )

            time.sleep(self.refresh_time)

    def stop(self):
        """ Function that stops the worker

        """
        pass

if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()

    worker = SloWorker(refresh_time=os.getenv('SLI_REFRESH_TIME'))

    if args.daemon:
        pid = worker.daemonize()

    try:
        worker.start()
    except KeyboardInterrupt:
        worker.stop()

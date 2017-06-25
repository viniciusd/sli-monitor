import argparse
import os
import time

from collections import namedtuple

import requests

def get_parser():
    parser = argparse.ArgumentParser(description="SLO worker")
    parser.add_argument('--daemon', dest='daemon',
                        default=False, action='store_true',
                        help='Daemonize the process')

    return parser


Response = namedtuple('Response', ['url', 'status', 'time'])


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

    @staticmethod
    def get_configurations(filename):
        """ Function that reads the configurations file and invokes the parser
            function

        Args:
            filename: Name of the configurations file

        Returns:
            A list of parsed SLOs. Check parse_into_slo_list for more details

        """
        pass

    @staticmethod
    def parse_into_slo_list(buffer):
        """ Function that parses a buffer into a list of SLOs

        Args:
            buffer: Buffer which will be parsed

        Returns:
            A list of SLOs. Each SLO has a URL, and SLIs for both successful
            and fast responses.

        """
        pass

    @staticmethod
    def do_requests(urls):
        """ Function that do requests to the specified URLs

        Args:
            urls: List of URLs

        Returns:
            A list of respones. Each response has its URL, a status code and
            a response time
        """
        responses = []
        for url in urls:
            start = time.time()
            r = requests.get(url)
            roundtrip = time.time() - start
            responses.append(Response(url, r.status_code, roundtrip))
        return responses

    @staticmethod
    def recalculate_slis(db_connection):
        """ Function that recalculates the SLIs

        Args:
            db_connection: Database connection
        """
        pass

    def daemonize(self):
        """ Function that daemonizes the worker

        Returns:
            PID of the process

        """
        raise NotImplementedError('Daemon behavior yet not implemented')

    def start(self):
        """ Application loop
        It will call the other methods, doing requests peridocally and updating
        the SLIs

        """
        pass

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

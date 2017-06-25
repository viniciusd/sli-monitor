import argparse
import os
import time

from datetime import datetime

import utils

def get_parser():
    parser = argparse.ArgumentParser(description="SLO worker")
    parser.add_argument('--daemon', dest='daemon',
                        default=False, action='store_true',
                        help='Daemonize the process')

    return parser


class SloWorker:
    """SloWorker periodically polls URLs to calculate their SLIs

    Args:
        refresh_time (int): The refreshing time after which the worker
                            will redo the requests
    """
    def __init__(self, *, refresh_time=None):

        # It checks for None in case os.getenv was used to pass the argument
        # That's why it is not default to 5 already in the definition
        self.refresh_time = 5 if refresh_time is None else refresh_time

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
        self.conn = utils.get_db_connection()

        last_read_config = datetime.utcfromtimestamp(0)

        while True:
            last_modified_config = datetime.utcfromtimestamp(
                                                             os.path.getmtime(config_file
                                                                              )
                                                             ) 
            if last_read_config < last_modified_config:
                slos = utils.get_configurations(config_file)
                last_read_config = datetime.now()

            utils.recalculate_slis(self.conn,
                                  utils.do_requests(utils.get_slo_urls(slos))
                                  )

            time.sleep(self.refresh_time)

    def stop(self):
        """ Function that stops the worker

        """
        self.conn.close()

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

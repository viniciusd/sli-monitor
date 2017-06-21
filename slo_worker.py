import os


class SloWorker:
    """SloWorker periodically pools URLs to calculate their SLIs

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
        pass

    @staticmethod
    def recalculate_slis(db_connection):
        """ Function that recalculates the SLIs

        Args:
            db_connection: Database connection
        """
        pass

    def run(self):
        """ Application loop
        It will call the other methods, doing requests peridocally and updating
        the SLIs

        """
        pass

if __name__ == '__main__':
    worker = SloWorker(refresh_time=os.getenv('SLI_REFRESH_TIME'))

    worker.run()

import unittest

from slo_worker import SloWorker

class SloWorkerTest(unittest.TestCase):
   
    def setUp(self):
        self.worker = SloWorker()

    def test_do_request_returns_a_sequence(self):
        urls = [
                'http://www.fakeresponse.com/api?status=400',
                ]

        slos = self.worker.do_requests(urls)

        self.assertNotIsInstance(slos, str)

        with self.assertDoesNotRaise(TypeError):
           _ = (e for e in slos)

    def test_do_request_when_no_urls_given(self):
        urls = []
        
        slos = self.worker.do_requests(urls)

        self.assertFalse(slos)
        self.assertIsInstance(slos, list)

    def test_do_request_when_status_code_is_429(self):
        urls = [
                'http://www.fakeresponse.com/api?status=429',
                ]

        slos = self.worker.do_requests(urls)

        self.assertEqual(1, len(slos))
        self.assertEqual(429, slos[0].status)


    def test_parse_into_slo_list(self):
        config = """SLOs:
                         - url: "www.example.com"
                           successful-responses-SLO: 0.9
                           fast-responses-SLO: 0.9
                 """
        slos = self.worker.parse_into_slo_list(config)
        
        slo = slos.pop()

        self.assertEqual("www.example.com", slo.url)
        self.assertEqual(0.9, slo.successful_responses)
        self.assertEqual(0.9, slo.fast_responses)


    class _AssertDoesNotRaiseContext(unittest.case._AssertRaisesBaseContext):
        """A context manager used to implement TestCase.assertRaises* methods.
        """

        _base_type = BaseException
        _base_type_str = 'an exception type or tuple of exception types'

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, tb):
            if exc_type is None:
                return True
            if exc_type and issubclass(exc_type, self.expected):
                try:
                    exc_name = self.expected.__name__
                except AttributeError:
                    exc_name = str(self.expected)
                if self.obj_name:
                    self._raiseFailure("{} raised by {}".format(exc_name,
                                                                self.obj_name))
                else:
                    self._raiseFailure("{} raised".format(exc_name))
            else:
                traceback.clear_frames(tb)
            if not issubclass(exc_type, self.expected):
                # let unexpected exceptions pass through
                return False
            # store exception, without traceback, for later retrieval
            self.exception = exc_value.with_traceback(None)
            return False

    def assertDoesNotRaise(self, expected_exception, *args, **kwargs):
        context = self._AssertDoesNotRaiseContext(expected_exception, self)
        return context.handle('assertDoesNotRaise', args, kwargs) 

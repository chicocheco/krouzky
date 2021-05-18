import unittest
from time import time, sleep

from helium import S, Config
from helium import start_firefox, go_to
from selenium.webdriver.remote.webelement import WebElement


def is_present(sel: str, limit: int = 10) -> bool:
    """
    Checks whether an element is present. If so, returns True once found, otherwise returns False
    when the time runs out. Must be used with precaution because it does not throw an exception.

    :param sel: universal selector
    :param limit: time limit for returning False
    :return: True or False
    """

    if limit < 10 and Config.implicit_wait_secs == 10:
        Config.implicit_wait_secs = 0  # override helium's default
    helium_sel = S(sel)
    start = time()
    while time() - start < limit:
        try:
            if isinstance(helium_sel.web_element, WebElement):
                return True
        except LookupError:
            pass
        sleep(.5)
    return False


def get_element(sel: str, limit: int = 10) -> WebElement:
    """
    Wait a certain amount of time for an element to get loaded and return it, otherwise raise a LookupError

    :param sel: universal selector
    :param limit: time limit for raising LookupError
    """
    if limit < 10 and Config.implicit_wait_secs == 10:
        Config.implicit_wait_secs = 0  # override helium's default
    helium_selector = S(sel)
    start = time()
    while True:
        try:
            return helium_selector.web_element
        except LookupError as e:
            if time() - start > limit:
                raise e
            sleep(.5)


# run with a local interpreter, not within docker
class NewVisitorTest(unittest.TestCase):

    def setUp(self) -> None:
        self.browser = start_firefox()

    def tearDown(self) -> None:
        self.browser.quit()

    def test_can_open_homepage_and_see_header(self):
        go_to('http://0.0.0.0:8000/')
        self.assertIn('Vyber online aktivitu', self.browser.title)
        # self.fail('Finish the test!')


if __name__ == '__main__':
    unittest.main()

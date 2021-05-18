import unittest
from time import time, sleep

from helium import S, Config
from helium import start_firefox, go_to, get_driver, scroll_down, kill_browser
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
    """Test whether a new user with no account can open any page that does not require an account."""

    def setUp(self) -> None:
        start_firefox(headless=True)
        go_to('http://0.0.0.0:8000/')
        get_element('//a[@id="djHideToolBarButton"]').click()

    def tearDown(self) -> None:
        get_driver().quit()
        kill_browser()

    def test_can_open_homepage_and_see_header_and_lead_text(self):
        self.assertIn('Vyber online aktivitu', get_driver().title)
        lead_text = get_element('h1.display-1').text
        self.assertIn('Vyhledávač online aktivit', lead_text)

    def test_can_open_search_page_via_btn_homepage(self):
        get_element('//a[@class="btn btn-lg btn-primary"]').click()
        lead_text = get_element('h1').text
        self.assertIn('Vybrat', lead_text)

    def test_can_open_search_page_via_navbar_homepage(self):
        get_element('//a[@href="/hledani/"]').click()
        lead_text = get_element('h1').text
        self.assertIn('Vybrat', lead_text)

    def test_can_open_catalog_page_via_homepage(self):
        get_element('//a[@href="/aktivity/"]').click()
        lead_text = get_element('h1').text
        self.assertIn('Katalog', lead_text)

    def test_can_open_conditions_page_via_homepage(self):
        scroll_down(3000)
        get_element('//a[@href="/podminky-uzivani/"]').click()
        lead_text = get_element('h1').text
        self.assertIn('Podmínky užívání', lead_text)

    def test_can_open_gdpr_page_via_homepage(self):
        scroll_down(3000)
        get_element('//a[@href="/gdpr/"]').click()
        lead_text = get_element('h1').text
        self.assertIn('Zásady ochrany osobních údajů', lead_text)

    def test_can_open_about_page_via_homepage(self):
        get_element('//a[@href="/o-nas/"]').click()
        lead_text = get_element('h1').text
        self.assertIn('O nás', lead_text)

    def test_can_open_cooperation_page_via_homepage(self):
        get_element('//a[@href="/spoluprace/"]').click()
        lead_text = get_element('h1').text
        self.assertIn('Spolupráce', lead_text)


if __name__ == '__main__':
    unittest.main()

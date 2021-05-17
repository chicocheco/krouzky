from helium import start_firefox

browser = start_firefox('http://localhost:8000')

assert 'Vyber' in browser.title

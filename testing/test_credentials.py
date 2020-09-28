import pytest
from scraper import Scraper

def test_credentials_valid():
    s = Scraper()
    assert s.verify_chinesepod_credentials()

def test_credentials_invalid():
    s = Scraper(credentials=('a', 'b'))
    assert not s.verify_chinesepod_credentials()

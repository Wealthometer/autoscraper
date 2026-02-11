import pytest
from autoscraper import AutoScraper

HTML = "<ul><li>Banana</li><li>Apple</li><li>Orange</li></ul>"


def test_build_requires_targets():
    scraper = AutoScraper()
    with pytest.raises(ValueError):
        scraper.build(html=HTML)


def test_build_and_get_result_similar():
    scraper = AutoScraper()
    result = scraper.build(html=HTML, wanted_list=["Banana"])
    assert result == ["Banana"]
    similar = scraper.get_result_similar(html=HTML, contain_sibling_leaves=True)
    assert similar == ["Banana", "Apple", "Orange"]

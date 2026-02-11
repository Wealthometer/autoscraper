import pytest

from autoscraper import AutoScraper

HTML = "<ul><li>Banana</li><li>Apple</li><li>Orange</li></ul>"
HTML_COMPLEX_ORDER = """
<div class='products'>
  <h2>Banana</h2>
  <p class='price'>$1</p>
  <h2>Apple</h2>
  <p class='price'>$2</p>
</div>
"""


def test_get_result_exact_order():
    scraper = AutoScraper()
    scraper.build(html=HTML_COMPLEX_ORDER, wanted_list=["Banana", "$2"])
    assert scraper.get_result_exact(html=HTML_COMPLEX_ORDER) == ["Banana", "$2"]


def test_group_by_alias():
    scraper = AutoScraper()
    scraper.build(html=HTML, wanted_dict={"fruit": ["Banana"]})
    similar = scraper.get_result_similar(
        html=HTML, group_by_alias=True, contain_sibling_leaves=True, unique=True
    )
    assert similar == {"fruit": ["Banana", "Apple", "Orange"]}


def test_save_and_load(tmp_path):
    scraper = AutoScraper()
    scraper.build(html=HTML, wanted_list=["Banana"])
    file_path = tmp_path / "model.json"
    scraper.save(file_path)
    new_scraper = AutoScraper()
    new_scraper.load(file_path)
    assert new_scraper.get_result_exact(html=HTML) == scraper.get_result_exact(html=HTML)


def test_keep_rules():
    scraper = AutoScraper()
    scraper.build(html=HTML, wanted_list=["Banana"])
    first_rule = scraper.stack_list[0]["stack_id"]
    scraper.build(html=HTML, wanted_list=["Apple"], update=True)
    second_rule = scraper.stack_list[1]["stack_id"]
    scraper.keep_rules([second_rule])
    assert len(scraper.stack_list) == 1
    assert scraper.stack_list[0]["stack_id"] == second_rule


def test_get_result_combined():
    scraper = AutoScraper()
    scraper.build(html=HTML, wanted_list=["Banana"])
    similar, exact = scraper.get_result(html=HTML)
    assert exact == ["Banana"]
    assert similar == ["Banana"]

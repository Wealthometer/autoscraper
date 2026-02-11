import pytest
import re
from autoscraper import AutoScraper

HTML_COMPLEX = """
<div id="main">
  <ul class="fruits">
    <li class="item"><span class="name">Banana</span><a href="/banana" class="link">More</a></li>
    <li class="item"><span class="name">Apple</span><a href="/apple" class="link">More</a></li>
    <li class="item"><span class="name">Orange</span><a href="/orange" class="link">More</a></li>
    <li class="item"><span class="name">Banana</span></li>
  </ul>
  <p class="info">Fresh fruits</p>
  <a class="external" href="/shop">Shop Now</a>
</div>
"""


def test_extract_relative_link():
    scraper = AutoScraper()
    url = "https://example.com/index.html"
    result = scraper.build(url=url, html=HTML_COMPLEX, wanted_list=["https://example.com/apple"])
    assert "https://example.com/apple" in result
    similar = scraper.get_result_similar(
        url=url, html=HTML_COMPLEX, contain_sibling_leaves=True, unique=True
    )
    assert set(similar) == {
        "https://example.com/banana",
        "https://example.com/apple",
        "https://example.com/orange",
    }
    exact = scraper.get_result_exact(url=url, html=HTML_COMPLEX)
    assert exact == ["https://example.com/apple"]


def test_build_with_regex():
    scraper = AutoScraper()
    scraper.build(html=HTML_COMPLEX, wanted_list=[re.compile("Ban.*")])
    result = scraper.get_result_exact(html=HTML_COMPLEX)
    assert "Banana" in result[0]


def test_update_appends_rules():
    scraper = AutoScraper()
    scraper.build(html=HTML_COMPLEX, wanted_list=["Banana"])
    count = len(scraper.stack_list)
    scraper.build(html=HTML_COMPLEX, wanted_list=["Apple"], update=True)
    assert len(scraper.stack_list) == count + 1


def test_remove_rules():
    scraper = AutoScraper()
    scraper.build(html=HTML_COMPLEX, wanted_list=["Banana"])
    scraper.build(html=HTML_COMPLEX, wanted_list=["Apple"], update=True)
    rule_ids = [s["stack_id"] for s in scraper.stack_list]
    to_remove = rule_ids[0]
    scraper.remove_rules([to_remove])
    remaining = [s["stack_id"] for s in scraper.stack_list]
    assert to_remove not in remaining
    assert len(remaining) == len(rule_ids) - 1


def test_keep_blank_returns_empty():
    scraper = AutoScraper()
    scraper.build(html=HTML_COMPLEX, wanted_list=["/shop"])
    html_blank = HTML_COMPLEX.replace('href="/shop"', 'href=""')
    result = scraper.get_result_exact(html=html_blank, keep_blank=True)
    assert result == [""]


def test_attr_fuzz_ratio():
    html_base = '<div><a class="btn-primary" href="/item">Buy</a></div>'
    html_variant = '<div><a class="btn-prime" href="/item">Buy</a></div>'
    scraper = AutoScraper()
    scraper.build(html=html_base, wanted_list=["Buy"])
    res = scraper.get_result_exact(html=html_variant, attr_fuzz_ratio=0.8)
    assert res == ["Buy"]

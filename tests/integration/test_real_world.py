import re
from autoscraper import AutoScraper

HTML_PAGE_1 = """
<div id='product'>
  <h1 class='title'>Sony PlayStation 4 PS4 Pro 1TB 4K Console - Black</h1>
  <span class='price'>US $349.99</span>
  <div class='rating'><span class='value'>4.8</span></div>
  <div class='note'>See details</div>
</div>
"""

HTML_PAGE_2 = """
<div id='product'>
  <h1 class='title'>Acer Predator Helios 300 15.6'' 144Hz FHD Laptop i7-9750H 16GB 512GB GTX 1660 Ti</h1>
  <span class='price'>US $1,229.49</span>
  <div class='rating'><span class='value'>5.0</span></div>
  <div class='note'>See details</div>
</div>
"""

HTML_WALMART_1 = "<div class='price'>$8.95</div>"
HTML_WALMART_2 = "<div class='price'>$7.00</div>"
HTML_ETSY_1 = "<span class='amount'>$12.50+</span>"
HTML_ETSY_2 = "<span class='amount'>$60.00</span>"


def test_grouping_and_rule_removal():
    scraper = AutoScraper()
    wanted = [
        "Sony PlayStation 4 PS4 Pro 1TB 4K Console - Black",
        "US $349.99",
        "4.8",
        "See details",
    ]
    scraper.build(html=HTML_PAGE_1, wanted_list=wanted)
    grouped = scraper.get_result_exact(html=HTML_PAGE_2, grouped=True)
    unwanted = [r for r, v in grouped.items() if v == ["See details"]]
    scraper.remove_rules(unwanted)
    result = scraper.get_result_exact(html=HTML_PAGE_2)
    assert result == [
        "Acer Predator Helios 300 15.6'' 144Hz FHD Laptop i7-9750H 16GB 512GB GTX 1660 Ti",
        "US $1,229.49",
        "5.0",
    ]


def test_incremental_learning_multiple_sites():
    scraper = AutoScraper()
    data = [
        (HTML_PAGE_1, ["US $349.99"]),
        (HTML_WALMART_1, ["$8.95"]),
        (HTML_ETSY_1, ["$12.50+"]),
    ]
    for html, wanted in data:
        scraper.build(html=html, wanted_list=wanted, update=True)
    assert "US $1,229.49" in scraper.get_result_exact(html=HTML_PAGE_2)
    assert "$7.00" in scraper.get_result_exact(html=HTML_WALMART_2)
    assert "$60.00" in scraper.get_result_exact(html=HTML_ETSY_2)


def test_attr_fuzz_ratio_realistic():
    base = "<div><a class='btn-primary-action' href='/buy'>Buy</a></div>"
    variant = "<div><a class='btn-prim-action' href='/buy'>Buy</a></div>"
    scraper = AutoScraper()
    scraper.build(html=base, wanted_list=["Buy"])
    assert scraper.get_result_exact(html=variant, attr_fuzz_ratio=0.8) == ["Buy"]


def test_regex_name_extraction():
    scraper = AutoScraper()
    scraper.build(html=HTML_PAGE_1, wanted_list=[re.compile(r".*PlayStation.*Console.*")])
    result = scraper.get_result_exact(html=HTML_PAGE_1)
    assert any("PlayStation" in r for r in result)


def test_keep_blank_for_missing_rating():
    scraper = AutoScraper()
    scraper.build(html=HTML_PAGE_1, wanted_list=["4.8"])
    html_no_rating = HTML_PAGE_2.replace("5.0", "")
    res = scraper.get_result_exact(html=html_no_rating, keep_blank=True)
    assert res == [""]


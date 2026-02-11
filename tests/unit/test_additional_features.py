from autoscraper import AutoScraper

HTML = "<ul><li>Banana</li><li>Apple</li><li>Orange</li></ul>"
HTML_DUP = "<ul><li>Banana</li><li>Banana</li></ul>"


def test_text_fuzz_ratio_partial():
    scraper = AutoScraper()
    scraper.build(html="<ul><li>Banana</li></ul>", wanted_list=["Banan"], text_fuzz_ratio=0.8)
    assert scraper.get_result_exact(html="<ul><li>Banana</li></ul>") == ["Banana"]


def test_set_rule_aliases():
    scraper = AutoScraper()
    scraper.build(html=HTML, wanted_list=["Banana"])
    rule_id = scraper.stack_list[0]["stack_id"]
    scraper.set_rule_aliases({rule_id: "fruit"})
    result = scraper.get_result_similar(html=HTML, group_by_alias=True, contain_sibling_leaves=True)
    assert result == {"fruit": ["Banana", "Apple", "Orange"]}


def test_grouped_results_by_rule():
    scraper = AutoScraper()
    scraper.build(html=HTML, wanted_list=["Banana"])
    rule_id = scraper.stack_list[0]["stack_id"]
    result = scraper.get_result_similar(html=HTML, grouped=True, contain_sibling_leaves=True)
    assert result == {rule_id: ["Banana", "Apple", "Orange"]}


def test_similar_unique_false():
    scraper = AutoScraper()
    scraper.build(html=HTML_DUP, wanted_list=["Banana"])
    result = scraper.get_result_similar(html=HTML_DUP, unique=False)
    assert result == ["Banana", "Banana"]


def test_similar_keep_order():
    scraper = AutoScraper()
    scraper.build(html=HTML, wanted_list=["Banana"])
    result = scraper.get_result_similar(html=HTML, contain_sibling_leaves=True, keep_order=True)
    assert result == ["Banana", "Apple", "Orange"]

import sys
from types import ModuleType
from html.parser import HTMLParser

class _Node:
    def __init__(self, name, attrs, parent=None):
        self.name = name
        self.attrs = dict(attrs)
        self.parent = parent
        self.children = []
        self.text = ""

    def append_child(self, child):
        self.children.append(child)
        child.parent = self

    def getText(self):
        return self.text + "".join(c.getText() for c in self.children)

    def findChildren(self, recursive=True):
        result = []
        for child in self.children:
            result.append(child)
            if recursive:
                result.extend(child.findChildren(recursive))
        return result

    def findParent(self):
        return self.parent

    def _attr_match(self, child, attrs):
        from autoscraper.utils import FuzzyText

        for key, val in (attrs or {}).items():
            actual = child.attrs.get(key, "")
            if isinstance(actual, list):
                actual = " ".join(actual)

            if isinstance(val, FuzzyText):
                if not val.search(actual):
                    return False
            elif actual != val:
                return False
        return True

    def findAll(self, name=None, attrs=None, recursive=True):
        result = []
        for child in self.children:
            if (name is None or child.name == name) and self._attr_match(child, attrs):
                result.append(child)
            if recursive:
                result.extend(child.findAll(name, attrs, recursive))
        return result

    def find_all(self, name=None, attrs=None, text=None, recursive=True):
        if text:
            res = []
            if self.text.strip():
                res.append(self.text)
            for child in self.children:
                if recursive:
                    res.extend(child.find_all(text=True, recursive=True))
                elif child.text.strip():
                    res.append(child.text)
            return res
        return self.findAll(name, attrs, recursive)

class _Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.root = _Node("[document]", {})
        self.current = self.root

    def handle_starttag(self, tag, attrs):
        node = _Node(tag, attrs)
        self.current.append_child(node)
        self.current = node

    def handle_endtag(self, tag):
        if self.current.parent:
            self.current = self.current.parent

    def handle_data(self, data):
        self.current.text += data

class BeautifulSoup(_Node):
    def __init__(self, html, parser):
        p = _Parser()
        p.feed(html)
        super().__init__(p.root.name, p.root.attrs)
        self.children = p.root.children
        for c in self.children:
            c.parent = self

bs4_mod = ModuleType("bs4")
bs4_mod.BeautifulSoup = BeautifulSoup
sys.modules.setdefault("bs4", bs4_mod)

class _Response:
    def __init__(self, text=""):
        self.encoding = "utf-8"
        self.headers = {"Content-Type": "text/html"}
        self.text = text

requests_mod = ModuleType("requests")
requests_mod.get = lambda url, headers=None, **kw: _Response()
sys.modules.setdefault("requests", requests_mod)

import importlib
import json
import logging
import re
from html.parser import HTMLParser

import requests

HAS_MARKUP_PARSE = False
try:
    import marko

    HAS_MARKUP_PARSE = True
except ModuleNotFoundError:
    logging.warning(
        "joplin-snipptets: You don't have marko installed. This way markdown will not be parsed! You can fix this with: pip install marko"
    )


TOKEN = "XXXXXX"
NOTEBOOK = "snippets"

logger = logging.getLogger(__name__)

class CodeParser(HTMLParser):
    def __init__(self):
        self.code = ""
        self._on_code = False
        super().__init__()

    def handle_starttag(self, tag, attrs):
        if tag == "code":
            self._on_code = True

    def handle_endtag(self, tag):
        if tag == "code":
            self._on_code = False

    def handle_data(self, data):
        if self._on_code:
            self.code += data


class JoplinNotebookClient:
    def __init__(self, token, notebook, modules):
        self.port = "41184"
        self.reload(token, notebook, modules)
        self._routes = ["notes", "folders", "folders/%s/notes", "notes/%s"]

    def reload(self, token=None, notebook=None, modules=None):
        if token:
            self.token = token
        if notebook:
            self.notebook = notebook
        if modules:
            self.modules = [n.strip() for n in modules.split(",")]

        self.port = "41184"
        if token is None:
            return
        self._url = f"http://localhost:{self.port}/%s?token=" + token
        for _ in range(10):  # Try 10 ports
            if self.ping():
                self.connected = True
                break
            self.port = str(int(self.port) + 1)
        else:
            self.connected = False
        self._url = f"http://localhost:{self.port}/%s?token=" + token

    def _gen_url(self, route, args=[]):
        end_url = self._url % route + ("&" + "&".join(args) if args else "")
        return end_url

    def _get(self, route, args=[]):
        resp = requests.get(url=self._gen_url(route, args))
        return resp.json()  # Check the JSON Response Content document

    def _get_with_params(self, route, args=[], params=None):
        resp = requests.get(url=self._gen_url(route, args), params=params)
        return resp.json()  # Check the JSON Response Content document

    def ping(self):
        resp = requests.get(url=self._gen_url("ping"))
        return resp.text == "JoplinClipperServer"

    def _get_all(self, route):
        has_more = True
        result = []
        page = 1
        while has_more:
            resp = self._get(route, args=[f"page={page}"])
            if resp.get("error"):
                break
            for r in resp["items"]:
                result.append(r)
            has_more = resp.get("has_more")
            page += 1
        return result

    def find_notebook(self):
        notebooks = self._get_all(self._routes[1])
        notebook = None
        for notebook in notebooks:
            if notebook["title"] == self.notebook:
                return notebook
        if notebook is not None:
            logger.error("jopling-snippets: Notebook not found")
            return

    def find_note(self, title):
        notebook = self.find_notebook()
        notes_id = {
            note["title"]: note["id"]
            for note in self._get_all(self._routes[2] % notebook["id"])
        }
        results = []
        for t in notes_id:
            if title.casefold() in t.casefold():
                results.append(notes_id[t])
        return [
            self._get(self._routes[3] % n, args=["fields=id,title,body"])
            for n in results
        ]

    def get_note(self, note_id):
        return self._get(self._routes[3] % note_id, args=["fields=id,title,body"])

    def create(self, title, body):
        notebook = self.find_notebook()
        data = json.dumps({"title": title, "body": body, "parent_id": notebook["id"]})
        resp = requests.post(self._gen_url("notes"), data=data)
        return resp.json()


def expand(text, modules=[]):
    match = r"\$\{\{(.+)\}\}"
    codes = re.findall(match, text)
    if not codes:
        return text
    for name in modules:
        try:
            globals()[name] = importlib.import_module(name)
        except ModuleNotFoundError:
            return f"ERROR: {name} cannot be imported"
    for code in codes:
        try:
            text = re.sub(match, str(eval(code)), text, 1)
        except Exception as e:
            logger.error("\nError on joplin-snippets!")
            logger.error(e)
            logger.error("Maybe you forgot to add a module to the extension settings?")
            logger.error(f"{modules=}")
            logger.error("-" * 80)
    return text


def parse(text, modules=[], use_expand=True):
    if not HAS_MARKUP_PARSE:
        return text
    html = marko.convert(text)
    parser = CodeParser()
    parser.feed(html)
    text = text if not parser.code else parser.code
    return expand(text, modules) if use_expand else text


# Basic test
if __name__ == "__main__":
    code = """
```cobol
       date-written. ${{1+1}}
       identification division.
       program-id. coboltut.
       author. matheus.
       date-written. ${{datetime.date.today().strftime('%B %-dth %Y')}}
       environment division.
       configuration section.
       data division.
       file section.
       working-storage section.
       procedure division.
           display "START"
           stop run.
```
    """
    print(parse(code, ['datetime']))

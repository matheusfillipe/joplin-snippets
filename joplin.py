import json
from html.parser import HTMLParser

import requests

HAS_MARKUP_PARSE = False
try:
    import marko

    HAS_MARKUP_PARSE = True
except ModuleNotFoundError:
    print(
            "joplin-snipptets: You don't have marko installed. This way markdown will not be parsed! You can fix this with: pip install marko"
    )


TOKEN = "XXXXXX"
NOTEBOOK = "snippets"


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
    def __init__(self, token, notebook):
        self.port = "41184"
        self.reload(token, notebook)
        self._routes = ["notes", "folders", "folders/%s/notes", "notes/%s"]

    def reload(self, token=None, notebook=None):
        self.token = token
        self.notebook = notebook
        self.port = "41184"
        if token is None:
            return
        self._url = f"http://localhost:{self.port}/%s?token=" + token
        for _ in range(10): # Try 10 ports
            if self.ping():
                self.connected = True
                break
            self.port = str(int(self.port) + 1)
        else:
            self.connected = False
        self._url = f"http://localhost:{self.port}/%s?token=" + token

    def _gen_url(self, route, args=[]):
        endUrl = self._url % route + ("&" + "&".join(args) if args else "")
        return endUrl

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
        if not notebook is None:
            print("jopling-snippets: Notebook not found")
            return


    def find_note(self, title):
        notebook = self.find_notebook()
        notes_id = {
            note["title"]: note["id"] for note in self._get_all(self._routes[2] % notebook["id"])
        }
        results = []
        for t in notes_id:
            if title.casefold() in t.casefold():
                results.append(notes_id[t])
        return [self._get(self._routes[3] % n, args=["fields=id,title,body"]) for n in results]


    def get_note(self, note_id):
        return get(self._routes[3] % note_id, args=["fields=id,title,body"])


    def create(self, title, body):
        notebook = self.find_notebook()
        data = json.dumps({"title": title, "body": body, "parent_id": notebook["id"]})
        resp = requests.post(self._gen_url("notes"), data=data)
        return resp.json()


def parse(text):
    if not HAS_MARKUP_PARSE:
        return text
    html = marko.convert(text)
    parser = CodeParser()
    parser.feed(html)
    return parser.code if parser.code else text


# Basic test
if __name__ == "__main__":
    note = find_note("python")[-1]
    print(parse(note["body"]))
    create("test", "some note\n ```python\nc='a'\nprint(c)\n```")

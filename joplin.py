import requests
from html.parser import HTMLParser
HAS_MARKUP_PARSE = False
try:
    import marko
    HAS_MARKUP_PARSE = True
except:
    print("You don't have marko installed. This way markdown will not be parsed! You can fix this with: pip install marko")


TOKEN = "XXXXXX"
NOTEBOOK = 'snippets'

class CodeParser(HTMLParser):
    def __init__(self):
        self.code = ""
        self._on_code = False
        super().__init__()

    def handle_starttag(self, tag, attrs):
        if tag == 'code':
            self._on_code = True

    def handle_endtag(self, tag):
        if tag == 'code':
            self._on_code = False

    def handle_data(self, data):
        if self._on_code:
            self.code += data



url = 'http://localhost:41184/%s?token='+TOKEN
endpoints = ['notes', 'folders', 'folders/%s/notes', 'notes/%s']

def reload(token, notebook):
    global url, TOKEN, NOTEBOOK
    TOKEN = token
    NOTEBOOK = notebook
    url = 'http://localhost:41184/%s?token='+token

def genUrl(endpoint, args):
    endUrl = url%endpoint + ("&" + "&".join(args) if args else "")
    return endUrl

def get(endpoint, args=[]):
    resp = requests.get(url=genUrl(endpoint, args))
    return resp.json() # Check the JSON Response Content document

def post(endpoint, args=[], params=None):
    resp = requests.get(url=genUrl(endpoint, args), params=params)
    return resp.json() # Check the JSON Response Content document

def get_all(endpoint):
    has_more = True
    result = []
    page = 1
    while has_more:
        resp = get(endpoint, args=[f"page={page}"])
        if resp.get('error'):
            break
        for r in resp['items']:
            result.append(r)
        has_more = resp.get('has_more')
        page+=1
    return result

def find_notebook():
    notebooks = get_all(endpoints[1])
    notebook = None
    for notebook in notebooks:
        if notebook['title'] == NOTEBOOK:
            return notebook
    if not notebook is None:
        print("Notebook not found")
        return

def find_note(title):
    notebook = find_notebook()
    notes_id = {note['title']: note['id'] for note in  get_all(endpoints[2]%notebook['id'])}
    results = []
    for t in notes_id:
        if title.casefold() in t.casefold():
            results.append(notes_id[t])
    return [get(endpoints[3]%n, args=['fields=id,title,body']) for n in results]

def parse(text):
    if not HAS_MARKUP_PARSE:
        return text
    html = marko.convert(text)
    parser = CodeParser()
    parser.feed(html)
    return parser.code if parser.code else text

# Basic test
if __name__ == "__main__":
    note = find_note('python')[-1]
    print(parse(note['body']))

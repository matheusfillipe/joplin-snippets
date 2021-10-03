import json
import re
import subprocess
import traceback

from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.CopyToClipboardAction import \
    CopyToClipboardAction
from ulauncher.api.shared.action.ExtensionCustomAction import \
    ExtensionCustomAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.RenderResultListAction import \
    RenderResultListAction
from ulauncher.api.shared.action.SetUserQueryAction import SetUserQueryAction
from ulauncher.api.shared.event import ItemEnterEvent, KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

from joplin import JoplinNotebookClient, parse


def jsonlist(body):
    if "```json" not in body:
        return None

    incode = False
    lines = []
    for line in body.split("\n"):
        if "```" in line and incode:
            lines.append(line.replace("```", ""))
            break
        if re.match(r"^```json\s+search\s*$", line):
            incode = True
            continue
        if incode:
            lines.append(line)

    if len(lines) == 0:
        return None

    obj = " ".join(lines)
    try:
        return json.loads(obj)
    except:
        return {"error": "You have a json syntax problem"}


class JoplinExtension(Extension):
    def __init__(self):
        super().__init__()
        self.joplin = None
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())


class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        try:
            paste = subprocess.check_output("xclip -o", shell=True).decode()
        except Exception as e:
            print(traceback.format_exc())
            return RenderResultListAction(
                [
                    ExtensionResultItem(
                        icon="images/icon.png",
                        name="You don't have xlip installed",
                        on_enter=HideWindowAction(),
                    )
                ]
            )

        title = event.get_data()
        error = RenderResultListAction(
            [
                ExtensionResultItem(
                    icon="images/icon.png",
                    name="Something went wrong :(",
                    on_enter=HideWindowAction(),
                )
            ]
        )
        try:
            res = extension.joplin.create(title, paste)
        except Exception as e:
            print(traceback.format_exc())
            return error

        if "error" in res:
            return error
        return RenderResultListAction(
            [
                ExtensionResultItem(
                    icon="images/icon.png",
                    name="Note created!",
                    on_enter=HideWindowAction(),
                )
            ]
        )

class PreferencesEventListener(EventListener):
    """ Handles preferences initialization event """
    def on_event(self, event, extension):
        extension.joplin = JoplinNotebookClient(event.preferences["token"], event.preferences["notebook"])

class PreferencesUpdateEventListener(EventListener):
    """ Handles Preferences Update event """
    def on_event(self, event, extension):
        """ Event handler """
        if extension.joplin is None:
            extension.joplin = JoplinNotebookClient(extension.preferences["token"], extension.preferences["notebook"])
        if event.id == 'token':
            extension.joplin.reload(token=event.new_value)
        if event.id == 'notebook':
            extension.joplin.reload(notebook=event.new_value)

class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        if extension.joplin is None:
            extension.joplin = JoplinNotebookClient(extension.preferences["token"], extension.preferences["notebook"])
        if not extension.joplin.connected:
            return RenderResultListAction([ExtensionResultItem("Can't connect to Joplin Clipper Server")])

        keyword = event.get_keyword()
        query = event.get_argument() or None

        if query is None:
            return RenderResultListAction(
                [
                    ExtensionResultItem(
                        icon="images/icon.png",
                        name="No input",
                        on_enter=HideWindowAction(),
                    )
                ]
            )

        if keyword == extension.preferences["copy-key"]:
            return RenderResultListAction(
                [
                   ExtensionResultItem(
                        icon="images/icon.png",
                        name="Note from Clipboard: " + query,
                        on_enter=ExtensionCustomAction(query, keep_app_open=True),
                    )
                ]
            )

        args = query.split()
        if args[0] == "jsonsearch" and len(args) >= 2:
            try:
                n = extension.joplin.get_note(args[1])
                obj = jsonlist(n["body"])
                query = " ".join(args[2:])
                keys = [key for key in obj if key.casefold().startswith(query.casefold())]
                if len(keys) == 0:
                    return RenderResultListAction([ExtensionResultItem("No search results!")])
                return RenderResultListAction(
                    [
                        ExtensionResultItem(
                            icon="images/icon.png",
                            name=key,
                            description=obj[key],
                            on_enter=CopyToClipboardAction(obj[key]),
                        )
                        for key in keys
                    ]
                )
            except:
                return RenderResultListAction(
                    [
                        ExtensionResultItem(
                            icon="images/icon.png",
                            name="invalid notebook",
                            description="Don't delete the notebook id",
                        )
                    ]
                )

        notes = extension.joplin.find_note(query)
        if len(notes) == 0:
            return RenderResultListAction([ExtensionResultItem("No search results!")])
        return RenderResultListAction(
            [
                ExtensionResultItem(
                    icon="images/icon.png",
                    name=n["title"],
                    description="".join(parse(n["body"])[:96]),
                    on_enter=CopyToClipboardAction(parse(n["body"]))
                    if jsonlist(n["body"]) is None
                    else SetUserQueryAction(f"{keyword} jsonsearch {n['id']} "),
                )
                for n in notes
            ]
        )


if __name__ == "__main__":
    JoplinExtension().run()

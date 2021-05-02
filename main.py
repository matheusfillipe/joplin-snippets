import json
import re

from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.CopyToClipboardAction import \
    CopyToClipboardAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
from ulauncher.api.shared.action.RenderResultListAction import \
    RenderResultListAction
from ulauncher.api.shared.action.SetUserQueryAction import SetUserQueryAction
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

import joplin


def jsonlist(body):
    if not "```json" in body:
        return None

    incode = False
    lines = []
    for line in body.split("\n"):
        if "```" in line and incode:
            lines.append(line.replace("```", ""))
            break
        if re.match(r"^```json\s+search\s+$", line):
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
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        keyword = event.get_keyword()
        joplin.reload(extension.preferences["token"], extension.preferences["notebook"])
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
        args = query.split()
        if args[0] == "jsonsearch" and len(args) >= 2:
            try:
                n = joplin.get_note(args[1])
                obj = jsonlist(n["body"])
                query = " ".join(args[2:])
                return RenderResultListAction(
                    [
                        ExtensionResultItem(
                            icon="images/icon.png",
                            name=key,
                            description=obj[key],
                            on_enter=CopyToClipboardAction(obj[key]),
                        )
                        for key in obj
                        if key.casefold().startswith(query.casefold())
                    ]
                )
            except:
                return RenderResultListAction(
                    [
                        ExtensionResultItem(
                            icon="images/icon.png",
                            name="invalid notebook",
                            description="You shouldn't delete the notebook id",
                        )
                    ]
                )

        notes = joplin.find_note(query)
        return RenderResultListAction(
            [
                ExtensionResultItem(
                    icon="images/icon.png",
                    name=n["title"],
                    description="".join(joplin.parse(n["body"])[:96]),
                    on_enter=CopyToClipboardAction(joplin.parse(n["body"]))
                    if jsonlist(n["body"]) is None
                    else SetUserQueryAction(f"{keyword} jsonsearch {n['id']} "),
                )
                for n in notes
            ]
        )


if __name__ == "__main__":
    JoplinExtension().run()

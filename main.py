from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction
import joplin


class JoplinExtension(Extension):
    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())

class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        joplin.reload(extension.preferences["token"], extension.preferences["notebook"])
        query = event.get_argument() if event.get_argument() else None
        notes = joplin.find_note(query)
        items = [
                ExtensionResultItem(
                    icon="images/icon.png",
                    name=n['title'],
                    description="".join(joplin.parse(n['body'])[:96]),
                    on_enter=CopyToClipboardAction(joplin.parse(n['body'])),
                )
                for n in notes
        ]
        return RenderResultListAction(items)

if __name__ == "__main__":
    JoplinExtension().run()


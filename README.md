# Joplin Explorer

Copy or create snippets of code from joplin right from or to your clipboard.
<p align="center">
<img width=100% src="https://github.com/matheusfillipe/joplin-snippets/raw/main/joplin_snippets.gif" />
</p>

### Commands

Type `n` and the name of a note to search for. Choose it and it will be copied to
your clipboard.

If a note has code all the code will be copied to the clipboard without the markup tags. 

You can also have a subsearch for a json code block if you have a code block that is marked with
`json search` instead of simply 'json'. This way each key of the json code
block will become searchable. This way you can have an easy selector for
multiple data in a single note. 

You can use `nc` (note copy) to convert the current clipboard into a note, using
the provided title from the launcher. This is the way you can create notes from
the clipboard.

### Requirements

```
pip3 install marko     # for markup parsing functinalities
apt-get install xclip  # for creating notes from clipboard
```

### Configuration

* You must configure a API token for joplin that you cant get on the desktop app's Option -> Web Clipper.

* Notebook to search (Default is snippet) which is optional.

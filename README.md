# Joplin snippets

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
pip3 install thefuzz   # for fuzzy searching
apt-get install xclip  # for creating notes from clipboard
```

### Configuration

* You must configure a API **token** for joplin that you cant get on the desktop app's Option -> Web Clipper.

* **Notebook** to search (Default is snippet) which is optional.

* **Python evaluation** and **Modules** list to use on expansions, evaluating python code (see bellow and this is optional)


### Evaluating python code

**Take care with this option as it can run arbitrary python code!**

First make sure you set "Enable python evaluation" to "yes".

You can configure evaluate python code directly from your notes. Anything inside `${{}}` will attempt to run with python, for example, if you create a note with `${{1+2}}` inside, that will copy to your clipboard as `2`. If the code fails to evaluate it will be copied as it is.

If your expansion needs modules you can add them to the `modules` field of the extension. They must be comma separated. Examples:

``` text
pi=${{math.pi}}
```
Will display:
`pi=3.141592653589793`
``` text
Arch Linux: ${{f"{platform.system()} {platform.release()} {platform.machine()}"}}
```
Will display:
`Arch Linux: Linux 5.15.5-arch1-1 x86_64`

```cobol
       IDENTIFICATION DIVISION.
       PROGRAM-ID. COBOLTUT.
       AUTHOR. MATHEUS.
       DATE-WRITTEN. ${{datetime.date.today().strftime('%B %-dth %Y')}}
       ENVIRONMENT DIVISION.
       CONFIGURATION SECTION.
       DATA DIVISION.
       FILE SECTION.
       WORKING-STORAGE SECTION.
       PROCEDURE DIVISION.
           DISPLAY "START"
           STOP RUN.
```
And that will display the current date inside the code block.

All of those together would require `modules` set to: `math,platform,datetime`

# pymates
Pythonic Markdown Text System

## Development Instructions

First of all, create a virtual environment to run the development version.

```
python3 -m venv .venv
```

You can also use `py -m venv .venv` on Windows.

Second, activate the virtual environent.
On Windows, run:

```
.venv\Scripts\activate.bat
```

On Unix or MacOS, run:

```
source .venv/bin/activate
```

Launch the viewer with

```
python3 -m pymates.viewer test/example1.md
```

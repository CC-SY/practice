from __future__ import print_function
import sys
import json
import csv
from os import linesep


if sys.version_info >= (3, 0):
    from io import BytesIO as _StringIO
else:
    # noinspection PyCompatibility
    from StringIO import StringIO as _StringIO

try:
    # noinspection PyUnresolvedReferences
    import requests
except ImportError:
    print("Python Editing Terminal requires the Requests module to be installed. Please install it using"
          " 'pip install requests'.",
          file=sys.stderr)
    exit()


class _Editor(object):
    """
    Represents a Visual Studio Code editor.
    """
    def __init__(self):
        self._text = ""
        self.etag = None
        self.port = None

        self.session = requests.Session()

    @property
    def text(self):
        """
        Get the text of the active Visual Studio Code document.
        """
        if self.port is None:
            raise RuntimeError("Module not initialized. Wait a few seconds and retry; report a bug"
                               " if this doesn't work.")

        prepared = requests.Request("GET", "http://127.0.0.1:{}/text".format(self.port)).prepare()

        if self.etag is not None:
            prepared.headers["If-None-Match"] = self.etag

        response = self.session.send(prepared)

        if response.status_code == 200:
            self._text = response.content
            self.etag = response.headers.get("etag", None)
        elif response.status_code == 204:
            self._text = None
        elif response.status_code == 304:
            pass
        else:
            raise RuntimeError("Server-side error: {} {}".format(response.status_code, response.content))

        return self._text

    @text.setter
    def text(self, value):
        """
        Set the text of the active Visual Studio Code document.
        """
        if self.port is None:
            raise RuntimeError("Module not initialized. Wait a few seconds and retry; report a bug"
                               " if this doesn't work.")

        response = requests.put("http://127.0.0.1:{}/text".format(self.port), value)

        if response.status_code == 200:
            pass  # Success!
        else:
            raise RuntimeError("Server-side error: {} {}".format(response.status_code, response.content))

        self._text = value

    @property
    def lines(self):
        """
        Get the active Visual Studio Code document as a list of lines (newlines not included)
        """
        return self.text.splitlines(False)

    @lines.setter
    def lines(self, value):
        """
        Set the active Visual Studio Code document text from a list of lines (newlines not included)
        Newline style ('\n', '\r' or '\r\n') will match the OS style.
        """
        self.text = linesep.join((str(l) for l in value))

    @property
    def json(self):
        """
        Get an object by parsing the active Visual Studio Code document as JSON.
        """
        text = self.text

        if not text:
            return None
        else:
            return json.loads(text)

    @json.setter
    def json(self, value):
        """
        Set the Visual Studio Code document text by converting an object to JSON.
        """
        self.text = json.dumps(value, indent=True)

    @property
    def csv(self):
        """
        Get a list of lists by parsing the active Visual Studio Code document as CSV.
        """
        reader = csv.reader(self.text.splitlines())
        return [l for l in reader]

    @csv.setter
    def csv(self, value):
        """
        Set the Visual Studio Code document text by converting a list of lists to CSV.
        """
        output = _StringIO()

        writer = csv.writer(output)
        for row in value:
            writer.writerow(row)

        self.text = output.getvalue()

        output.close()

    def set_port(self, port):
        self.port = port

    # noinspection PyShadowingNames
    def new(self, filename=None, text=None, lines=None, json=None, csv=None):
        """
        Opens a new VS Code tab, optionally saving the new file.
        """
        if self.port is None:
            raise RuntimeError("Module not initialized. Wait a few seconds and retry; report a bug"
                               " if this doesn't work.")

        response = requests.post("http://127.0.0.1:{}/new".format(self.port), data={"filename": filename or ""})

        if response.status_code == 200:
            pass  # Success!
        else:
            raise RuntimeError("Server-side error: {} {}".format(response.status_code, response.content))

        if text is not None:
            self.text = text
        if lines is not None:
            self.lines = lines
        if json is not None:
            self.json = json
        if csv is not None:
            self.csv = csv


editor = _Editor()
"""An object used to access the Visual Studio Code editor."""
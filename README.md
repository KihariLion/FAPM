# FurAffinity Private Message Downloader

Downloads private messages from FurAffinity, splits them into conversations
with individual users, and generates an HTML document for each conversation
that can be viewed in a web browser.

Suggestions and improvements are welcome!

## Setup Instructions for Windows

### Requirements

`Python 3.6` (or higher)

### Setup

These instructions assume that `python.exe`'s directory is in your `%PATH%`,
and that the version of Python it launches meets the requirement shown above.

With `FAPM` as the current working directory, enter the following commands:

$ `python -m venv venv`  
$ `venv\Scripts\activate`  
$ `pip install -r requirements.txt`

## Setup Instructions for Linux

### Requirements

`python3.6` (or higher)  
`python3-venv`

### Setup

With `FAPM` as the current working directory, enter the following commands:

$ `python3 -m venv venv`  
$ `source venv/bin/activate`  
$ `pip install -r requirements.txt`

## First Run

You can now run the script for the first time:

$ `python -m fapm --update`

If you have a lot of private messages, it will take a long time for the script
to complete. However, when you run the script again at a later time, it will
only need to download new messages that have been sent or received in the
meantime.

The script will create an `index.html` file in the `FAPM` directory, which will
include links to all of your conversations. Individual conversations are saved
in the `html` directory, but you will find it more convenient to use the index
rather than opening them one by one.

## Subsequent Runs

When you wish to download new messages at a later time, remember to `cd` into
the `FAPM` directory and activate the virtual environment (as you did during
setup) before running the script.

If you simply want to try the various formatting options with messages you have
already downloaded, do not include the `--update` option; this will save you a
lot of time.

## Color Text

If your terminal emulator supports ANSI escape codes, you can set `$FAPM_ANSI`
to `1` for more colorful and readable text output.

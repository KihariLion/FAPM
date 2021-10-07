FurAffinity Private Message Downloader
======================================

Downloads private messages from FurAffinity, splits them into conversations
with individual users, and generates an HTML document for each conversation
that can be viewed in a web browser.

Note that this script will mark all messages sent to you as having been read,
even if you have not viewed them on FurAffinity itself.

Suggestions and improvements are welcome!

Requirements
------------

`python3.6` (or higher)  
`virtualenv`

Running on Linux
----------------

With FAPM as the current working directory, enter the following commands:

$ `virtualenv -p python3.6 venv`  
$ `source venv/bin/activate`  
$ `pip install -r requirements.txt`

You can now run the script for the first time:

$ `python fapm.py --update`

If you have a lot of private messages, it will take a long time for the script
to complete. However, once your messages have been downloaded, you can run the
command again at a later time, and it will only download new messages that have
been sent or received in the meantime.

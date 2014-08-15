Personal Nissan Leaf Dashboard
==============================

A simple python script to query Nissan Leaf's CarWings server for the battery & charging status of the car and generate a simple web dashboard.

## Prerequisites

- A webserver to run the script & serve the dashboard HTML.
- The following python modules should be installed
 - [python-requests](https://pypi.python.org/pypi/requests)
 - [pytz](https://pypi.python.org/pypi/pytz)

## Setting up your instance
Checkout a copy of this repo in some directory on your webserver.

1. Edit the file .leafpasswd and put your Nissan Leaf Owner's portal username & password. Save the file and ensure that only the user that will execute the python script can read it.
2. Copy www/index.html to a directory from where the Web/HTTP server can serve the file externally. 
3. Run a test to check if everything is working

        python monitor_leaf.py /path/to/www/info.json

       Here ```/path/to/www``` should be the same directory where you copied ```index.html```. ```info.json``` is the filename to which the python script will write a summary of the data it queried from Carwings. If you change the filename, be sure to edit index.html too.
4. In your browser, try to load index.html. You should see a dashboard like this ![](https://raw.githubusercontent.com/wrecker/leafdashboard/master/www/screenshot.png)
5. To run this periodically add it to cron. Here is a sample cron line to run every 20 mins, Monday-Friday from 10am to 6pm.

        # m    h   dom mon dow command
        */20 10-17  *   *  1-5 cd /home/user/leafdashboard && pyton monitor_leaf.py /path/to/www/info.json > /dev/null

## Contributing

- Fork & Pull requests.

## License

The MIT License

Copyright (c) 2014 Mahesh Raju coder@mahesh.net

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

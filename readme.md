CONTENT QUALITY ANALYTICS
=========================
This is a service for analyzing the quality of courses of the Moodle distant learning system at the faculty of distance learning TUSUR.

LOCAL INSTALLATION
------------------
1. Download and install [docker toolbox](https://github.com/docker/toolbox/releases).
2. Download files from repository: `git clone https://git.2i.tusur.ru/lismo/content_quality_analytics`.
3. Run docker toolbox, go to the directory with the project and type the command: `sh runme.sh`.
4. Open the service:
    > <div>For linux: open browser and type "127.0.0.1:8000"</div>
    > <div>For windows: type `docker-machine ip default` into docker toolbox and copy returned IP into your browser with port 8000.</div>

DEPLOYMENT TO SERVER
--------------------
1. Login as superuser: `sudo su`
2. Upgrade apt: `apt update`
3. Install the necessary packages: `apt install git python3.6 python3-pip libmysqlclient-dev build-essential libssl-dev libffi-dev libxml2-dev libxslt1-dev zlib1g-dev`
4. Go to home directory: `cd /home`
5. Download files from repository: `git clone https://git.2i.tusur.ru/lismo/content_quality_analytics`
6. Go to content_quality_analytics directory: `cd /home/content_quality_analytics`
7. Install virtual environment: `pip3 install virtualenv`
8. Create virtual environment: `virtualenv venv`
9. Activate virtual environment: `source ./venv/bin/activate`
10. Install project requirements: `pip3 install -r requirements`
11. Install the necessary dictionaries: `python3.6 -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')"`
12. Prepare django migrations: `python3.6 manage.py makemigrations`
13. Make django migrations: `python3.6 manage.py migrate`
14. Run the project: `python3.6 manage.py runserver 0.0.0.0:8000`

USAGE
-----

1. Choose distance learning systems [online](https://online.tusur.ru/) or [new-online](https://new-online.tusur.ru/).
2. Enter course IDs, separated by commas.
3. Press the "Get" button and in the table below new lines with data and keywords of the entered courses will appear.  
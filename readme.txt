Local:
1. Download and install docker toolbox: https://github.com/docker/toolbox/releases.
2. Run docker toolbox and type the command "sh runme.sh".
3. - For linux: open browser and type "127.0.0.1:8000"
   - For windows: type "docker-machine ip default" into docker toolbox and copy returned IP into your browser with port 8000.
4. Load input.zip file for example.

Deployment:
1. Download files from repository: git clone https://github.com/ioaksenenko/content_quality_analytics
2. Upgrade apt: sudo apt update
3. Install python: sudo apt install python3.6
4. Install pip: sudo apt install python3-pip
5. Install virtual environment: sudo pip install virtualenv
6. Create virtual environment: virtualenv venv
7. Activate virtual environment: source {/path/to/venv}/bin/activate
8. Upgrade pip: pip3 install --upgrade pip
9. Install project requirements: pip3 install -r requirements.txt
10. Install install the necessary dictionaries: python3 -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')"
11. Prepare django migrations: python3 manage.py makemigrations
12. Make django migrations: python3 manage.py migrate
13. Run the project: python3 manage.py runserver 0.0.0.0:8000
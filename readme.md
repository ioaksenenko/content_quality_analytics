Local:
1. Download and install docker toolbox: https://github.com/docker/toolbox/releases.
2. Run docker toolbox and type the command "sh runme.sh".
3. - For linux: open browser and type "127.0.0.1:8000"
   - For windows: type "docker-machine ip default" into docker toolbox and copy returned IP into your browser with port 8000.
4. Load input.zip file for example.

Deployment:
1. Upgrade apt: `sudo apt update`
2. Install software properties common: `sudo apt install software-properties-common` 
3. Add python repository: `sudo add-apt-repository ppa:jonathonf/python-3.6`
4. Upgrade apt: `sudo apt update`
5. Install git: `sudo apt install git`
6. Download files from repository: `sudo git clone https://github.com/ioaksenenko/content_quality_analytics`
7. Install python: `sudo apt install python3.6`
8. Install pip: `sudo apt install python3-pip`
9. Install virtual environment: `sudo pip3 install virtualenv`
10. Create virtual environment: `sudo virtualenv venv`
11. Activate virtual environment: `sudo source {path_to_venv}/bin/activate`
12. Upgrade pip: `pip3 install --upgrade pip`
13. Install project requirements: `pip3 install -r requirements.txt`
14. Install the necessary dictionaries: `python3.6 -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')"`
15. Prepare django migrations: `python3.6 manage.py makemigrations`
16. Make django migrations: `python3.6 manage.py migrate`
17. Run the project: `python3.6 manage.py runserver 0.0.0.0:8000`

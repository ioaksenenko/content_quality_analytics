Local:
1. Download and install docker toolbox: https://github.com/docker/toolbox/releases.
1. Run docker toolbox and type the command "sh runme.sh".
1. - For linux: open browser and type "127.0.0.1:8000"
   - For windows: type "docker-machine ip default" into docker toolbox and copy returned IP into your browser with port 8000.
1. Load input.zip file for example.

Deployment:
1. Upgrade apt: `sudo apt update`
1. Install git: `sudo apt install git`
1. Download files from repository: `sudo git clone https://github.com/ioaksenenko/content_quality_analytics`
1. Install python: `sudo apt install python3.6`
    * If you have the message:        
        "E: Unable to locate package python3.6"        
        "E: Couldn't find any package by glob 'python3.6'"        
        "E: Couldn't find any package by regex 'python3.6'"        
       Run the commands:        
        1. Install software properties common: `sudo apt install software-properties-common`
        1. Add python repository: `sudo add-apt-repository ppa:jonathonf/python-3.6`
        1. Upgrade apt: `sudo apt update`
1. Install pip: `sudo apt install python3-pip`
1. Install virtual environment: `sudo pip3 install virtualenv`
1. Create virtual environment: `sudo virtualenv venv`
1. Activate virtual environment: `sudo source {path_to_venv}/bin/activate`
1. Upgrade pip: `python3.6 -m pip install --upgrade pip`
1. Install project requirements: `python3.6 -m pip install -r requirements.txt`
1. Install the necessary dictionaries: `python3.6 -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')"`
1. Prepare django migrations: `python3.6 manage.py makemigrations`
1. Make django migrations: `python3.6 manage.py migrate`
1. Run the project: `python3.6 manage.py runserver 0.0.0.0:8000`

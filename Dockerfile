FROM python:3
RUN mkdir /home/django
RUN mkdir /home/django/content_quality_analytics
WORKDIR /home/django/content_quality_analytics
ADD . /home/django/content_quality_analytics
RUN pip3 install --upgrade pip
RUN pip3 install -r /home/django/content_quality_analytics/requirements.txt
RUN python3 -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')"
RUN python3 manage.py makemigrations
RUN python3 manage.py migrate
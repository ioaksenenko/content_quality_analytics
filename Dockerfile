FROM python:3
RUN mkdir /home/content_quality_analytics
WORKDIR /home/content_quality_analytics
ADD . /home/content_quality_analytics
RUN pip3 install --upgrade pip
RUN pip3 install -r /home/content_quality_analytics/requirements
RUN python3 -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')"
RUN python3 manage.py makemigrations
RUN python3 manage.py migrate
RUN python3 manage.py loaddata content_quality_analytics_indicator.json
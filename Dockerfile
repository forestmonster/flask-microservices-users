FROM python:3.6.1

# Set working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# Leverage Docker cache somehow
ADD ./requirements.txt /usr/src/app/requirements.txt

# Install all the requirements
RUN pip install -r requirements.txt

# Now add the application
ADD . /usr/src/app

# And run the server
# (Overridden by command: gunicorn -b... in docker-compose-prod.yaml)
CMD python manage.py runserver -h 0.0.0.0

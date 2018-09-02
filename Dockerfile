FROM python:3

WORKDIR /app 
# Copy our current directory.
ADD . /app

# This will be shown on docker build
RUN python --version
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# This means that you can access the cointainer's port 80, not that our actual
# machine will have the port 5000 accessible.
EXPOSE 5000


# Run app.
#CMD FLASK_APP=main.py flask run
CMD gunicorn --bind 0.0.0.0:5000 main:app

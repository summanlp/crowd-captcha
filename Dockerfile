FROM python:3

WORKDIR /app 

# Copy only the requirements so we can have an image with full dependencies.
ADD requirements.txt /app
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Now we can copy the rest of the code. 
ADD . /app


# This means that you can access the cointainer's port 80, not that our actual
# machine will have the port 5000 accessible.
EXPOSE 5000


# Run app.
#CMD FLASK_APP=main.py flask run
CMD gunicorn --bind 0.0.0.0:5000 main:app

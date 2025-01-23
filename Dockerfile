FROM python:3.12.4

# Create a user to run the app
RUN useradd -m -s /bin/bash app-user

# Create the directory for the SQLite database to ensure it exists
RUN mkdir -p /src/apps/database

# Set working directory and copy requirements.txt
COPY requirements.txt /src/requirements.txt
WORKDIR /src/

# Install dependencies from requirements.txt
RUN pip install -r requirements.txt

# Optionally install gunicorn if not in requirements.txt
RUN pip install gunicorn

# Copy application files into the container
COPY apps /src/apps
COPY config.py /src/config.py
COPY main.py /src/main.py
COPY Dockerfile /src/Dockerfile

# Set permissions for the app directory to the user
RUN chown -R app-user:app-user /src

# Switch to the created user
USER app-user

# Expose the port the app runs on
EXPOSE 5000

# Set the entry point for the container to run the app with gunicorn
ENTRYPOINT [ "gunicorn", "main:app", "-w", "5", "--bind", "0.0.0.0:5000", "--log-level", "debug" ]

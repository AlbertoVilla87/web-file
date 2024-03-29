# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.9

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

ENV SKLEARN_ALLOW_DEPRECATED_SKLEARN_PACKAGE_INSTALL=True

# Install git
RUN apt-get update && apt-get install -y git

WORKDIR /app

# Copy code
COPY . .

# Install pip requirements
COPY requirements.txt .
RUN pip3 install -r requirements.txt 
RUN [ "python3", "-c", "import nltk; nltk.download('stopwords')" ]
RUN [ "python3", "-c", "import nltk; nltk.download('punkt')" ]
RUN cp -r /root/nltk_data /usr/local/share/nltk_data

# Install PostgreSQL, CMake, Rust
RUN apt-get update && apt-get install -y postgresql cmake rustc

ENV GRPC_PYTHON_BUILD_SYSTEM_ZLIB=true 
RUN pip install haystack==0.42
RUN pip install lxml --compile --no-cache-dir

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers

ENV HAYSTACK_SIGNAL_PROCESSOR=django.haystack.signal.RealtimeSignalProcessor
ENV HAYSTACK_CONNECTIONS=default
ENV HAYSTACK_DEFAULT_OPERATOR=AND
ENV ELASTICSEARCH_HOST=elasticsearch
ENV ELASTICSEARCH_PORT=9200

RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

EXPOSE 8050

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
#["python", "ask_candidates.py"]
CMD ["python", "test.py"]

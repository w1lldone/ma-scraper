# Microsoft Academic Scrapper

## Install on an Isolated Container
### Prerequisites:
- `docker` installed
- `docker-compose` installed
### Build and run
- copy `example.conf` to `apikey.conf` and fill the required API Key
- on the project root, run `docker-compose up -d`
- to stop the service run `docker-compose down`


## Install Using Python

Prerequisites:

* Python 3.5.x
* Python Virtualenv
* Python3 pip
* copy `example.conf` to `apikey.conf` and fill the required API Key

Before install engine dependencies, make sure you've created virtualenv

To install this engine dependencies:
```bash
    $ pip3 install -r requirements.txt
```
To run this service type:

```bash
    $ python3 app.py
```


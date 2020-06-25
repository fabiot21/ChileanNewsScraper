
# Web Scraper Prensa

Python 3 App to extract chilean digital newspapers from different locations

## Getting Started

### System Prerequisites

```
Python 3.8.x
Chrome Browser
Chrome Driver (compatible with Chrome Browser)
```
### Python Prerequisites

```
Pillow 7.0.0
requestium 0.1.9
requests 2.22.0
selenium 3.141.0
pdf2image==1.11.0
```
*This requirements are inside requirements.txt*


### Building Docker Image
Create Dockerfile
```
FROM python:3.8.2-buster

# install google chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable

# install chromedriver
RUN apt-get install -yqq unzip
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/bin/

# set display port to avoid crash
ENV DISPLAY=:99

# upgrade pip
RUN pip install --upgrade pip

WORKDIR /App
COPY App/ /App

# install dependencies
RUN pip install -r requirements.txt

```
Build docker image

```
docker build -t scraper path/to/Dockerfile
```
### Running With Docker
```
cd ScraperPrensa/
docker run -v "$(pwd)/App:/App" scraper python main.py [Newspaper Name --optional]
```
*If no argument was received, then the app will try to scrape all newspapers*

### Running In Production

For production purpose, execute `run_scraper_target.sh` or `run_scraper.sh`

#### Newspapers Names

* hoyxhoy
* publimetro
* diariofinanciero
* elmercurio
* regiones
* lun
* lasegunda
* latercera
* lacuarta

## Code

###  scraper .py

This class initialize a chrome driver with selenium and contains all the logic to scrape the necessary data from the target links.

Has one method for each type of logic, which receives a link and return a tuple that contains the `published date` and a list variable `src_images` with the sources of the images.

### main .py

This main file contains many methods to handle the whole process of the app; receives the name of the newspaper, reads the txt files inside `srclinks`, sends the destination links to Scraper Class to then receive the image links, and saves these files inside a folder.

### srclinks folder

This folder contains different txt files, one for each newspaper (or logic), with the format `code;destinationlink` for each line.

### run_scraper_target .sh

```
#!/bin/bash
cd /home/megatime/ScraperPrensa

mkdir -p logs

docker run -v "$(pwd)/App:/App" scraper python main.py $1 > logs/$1_$(date +"%H").log

find App/Results -type f -mtime +2 -name '*.jpg' -execdir rm -- '{}' +
find App/Results -type d -mtime +2 -execdir rm -rf {} +
```

This script receives a newspaper name as argument, run the app using the docker image and store the output inside the `logs` folder. Finally, removes files and folder older than 2 days inside App/Results folder.

### run_scraper .sh

```
#!/bin/bash
cd /home/megatime/ScraperPrensa/

./run_scraper_target.sh hoyxhoy
./run_scraper_target.sh publimetro
./run_scraper_target.sh diariofinanciero
./run_scraper_target.sh elmercurio
./run_scraper_target.sh regiones
./run_scraper_target.sh lun
./run_scraper_target.sh lasegunda
./run_scraper_target.sh latercera
./run_scraper_target.sh lacuarta
```

This script executes `run_scraper_target.sh` for every newspaper.
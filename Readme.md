# About
Server application and simple web-client for assessing aluminum ingot defects.

# Installation
## Prerequisites
- Python 3.9

## Prepare to run
### Windows
```bash
cd Prototype/server
pip install -r requirements.txt
```
### Linux/MacOS
```bash
cd Prototype/server
python3 -m venv .venv
source .venv/bin/activate   # only once in new terminal session
pip3 install -r requirements.txt
```
## Run
### Windows
```bash
cd Prototype/server
python flask_server.py
```
And then open `../client/index.html` in browser from the Explore.
### Linux/MacOS
```bash
cd Prototype/server
source .venv/bin/activate   # only once in new terminal session
python flask_server.py
open ../client/index.html   # in another terminal session
```
# Configuration
The server configuration is placed in the `config.ini` file inside the `server` directory.
Currently it contains only paths to the database, logs, and images. You are free to use relative or absolute paths for those directories, but be sure that the user who runs the server will have access to the specified directories. Otherwise the server will fail to run.
# Database
Csv file is a simulation of a database for storing server data.
The file is generated on the basis of images in the output folder (now there are images for demo). 

The file looks as follows:
![img.png](Documentation/images/img.png)

There are 4 columns in this file:
1) id_camera - Camera from which the image was received (so far, always 1, because there is only one camera)
2) id_img - generated image id
3) source_img - absolute path to the image files from aidd/Prototype/client/output
4) text - operator's verdict in text form
# Development
To update pip packages after installing them to the local development environment, run the following commands:
```bash
cd Prototype/server
pip freeze > requirements.txt
```
Then don't forget to make a Merge Request with your changes :)

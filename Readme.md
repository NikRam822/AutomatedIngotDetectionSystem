# Ingot Surface Defect Detection

## Project Description
Server application and simple web-client for assessing aluminum ingot defects.

## Demo 
![demo.jpg](Documentation/images/demo.jpg)

## Feature list
- Camera detection
- Camera settings
- Shortcuts
- Data storage
- Verdict of user
- Image processing
## Frameworks and Technologies used
- Python
- HTML & CSS
- Flask Framework
- CV2

## Usage instructions
### I Taking a photo
Given: No ingot is in the capture of camera; the view from camera view is displayed; the image frame displays "no image"
1. Tap 'Take a photo'
2. Photo processing
3. ml estimating
Expected result: the cropped image is displayed in GUI in the image frame; the estimated decision is displayed

### II Assessing
Given the cropped image is displayed in GUI in the image frame; the estimated decision is displayed
1. User taps one of 5 options (OK/...)
Expected result: 
1. the comment about submission is displayed for 5 sec.; the image is disappeared 5 sec after the action is performed; 
2. after the image disappeared the 'no image' blank is displayed

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
waitress-serve --host=127.0.0.1 --port=5000 flask_server:app
```
And then open `http://localhost:5000/` in browser.
### Linux/MacOS
```bash
cd Prototype/server
source .venv/bin/activate   # only once in new terminal session
waitress-serve --host=127.0.0.1 --port=5000 flask_server:app
```
open `http://localhost:5000/` in browser

# Configuration
The server configuration is placed in the config.ini file inside the server directory.
It contains: 
1. paths to the database, logs, raw and marked images and events; 
You are free to use relative or absolute paths for those directories, but be sure that the user who runs the server will have access to the specified directories. Otherwise the server will fail to run.

2. parameters for enabling (1) or disabling (0) experiments: events collection and hotkeys usage.
# Database
Csv file is a simulation of a database for storing server data.
Csv is generated after the first photo is received

The file looks as follows:
![img.png](Documentation/images/img.png)

There are 4 columns in this file:
1. ingot_id - From the factory (always 0, because there is no implementation of interaction with the factory)
2. camera_id - Camera from which the image was received (so far, always 1, because there is only one camera)
3. image_id - Generated image id
4. image_name - File name in the destination folder
5. processing_mark - Photo preprocessing output
6. ml_mark - Decision from AI
7. final_mark - Decision from operator
# Development
To update pip packages after installing them to the local development environment, run the following commands:
```bash
cd Prototype/server
pip freeze > requirements.txt
```
Then don't forget to make a Merge Request with your changes :)
## Start the server in dev mode
```bash
cd Prototype/server
source .venv/bin/activate   # (Linux/macOS) run only once in new terminal session
pip install -r requirements.txt
pip install -r requirements-dev.txt
flask --app flask_server run
```
open `http://localhost:5000/` in browser
# CI/CD
## Prerequisites
Install `pylint` and `pylint-flask`:
```bash
pip install pylint
pip install pylint_flask
```
## Run Flask lint
```bash
pylint --rc-file .pylint.rc Prototype/server/*.py
```
## Run tests
```bash
cd Prototype/server
python -m pytest -v tests
```
# Parking-lot-entry-decisions

## General info
Simple service which gets an image (or images) of an Israeli license plate and returns a decision whether the vehicle may enter a parking lot, according to some rules.
	
## Setup
To run this project, install the python's Requests library :

```
$ pip install requests
```
## How to use
Download or clone the project.

Run the program with the images path as command line arguments.

For example: 

```
$ python main.py 1.jpg 4.jpg 5.jpg 13.png

```
This command will run the program with 4 example images that already exists in the project directory: 2 negative and 2 positive expected results.

The decision will be written to a local SQL database called "parking_lot".

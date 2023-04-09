# Motivation

Applying for an intenship and practical training position at `Medikea Company`

# DawaFasta-API
Dawa Fasta connects customers with multiple pharmacies to buy medicine online, while allowing pharmacies to expand their reach and sell or buy in bulk orders Online.

# Documentation && Live at:
   
  https://dawafasta-project-238r.onrender.com
  
# Database Mockup

![Database Mockup](https://github.com/fierylion/DawaFasta-API/blob/main/Database%20Mockup.png)
     
# Features

	Use of django-rest-framework
	
	User authentication and authorization
	
	Company/Phamarcies authentication and authorization
	
	CRUD operations for medicines, orders, users
	
	Search and filter functionality for products and pharmacies
	
	I will also do Integration with external payment gateway with stripe for payment confirmation,
	
	I have added alot of error handling functionalities
	
# Getting Started

# Prerequisites

	-Python 3.6 or later
	
	-Used MySQL as my database, You can the change the database in:  settings.py  file

# Installation

Clone the repository: git clone `https://github.com/fierylion/DawaFasta-API.git`

Create a virtual environment and activate it use command: python -m venv env 

Install the requirements: `pip install -r requirements.txt`

Create a .env file on the folder on your project in the folder with `settings.py` file

Decide a database your going to use and set the environment variables involved, Modify the variables in settings.py

Together with,

Add the following on the .env file
	`-JWT_TOKEN = YOUR_SECRET_TOKEN_FOR_JWT_AUTHENTICATION`
	`-SECRET_KEY = YOUR_SECRET_TOKEN_TO_OVERCOME_CROSS_SITE_ATTACKS(CSRF)`

Run database migrations: python manage.py migrate

	Start the development server: python manage.py runserver
	
# Usage

On your project directory(the directory with manage.py file) run 

 `python3 manage.py runserver`
 
Will run on 

`localhost:8000`
	
	
	
	
	

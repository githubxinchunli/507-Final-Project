# 507-Final-Project

final_project.py includes the major programs that this project includes.


What is this program about?
Users can learn about the max, min and ave ratings of restaurants by their type/category in major cities of America. 


What files are needed to run the program?
1. secret_data_sample.py (Using the yelp fusion API key as the form: api_key = XXX).
  You can get Yelp fusion API key from here: https://www.yelp.com/developers/v3/manage_app
  
2. help.txt
  This text file gives you an idea of how to use command to get the data/info/visualization you want.


Data sources?
Yelp--API key is needed to run this program


Unittest?
Test Databases YelpRestaurants and Categories
Test Command setup


Modules included?
requests, json, sqlite3, and plotly


Presentation/Visualization:
a list and three plot forms: bar chart, pie chart and donut chart


Functions:
user_search_bar: user put in a number that represents a city to search for the restaurants info.

build_restaurant_table: Create database and main table YelpRestaurants.

insert_data: Insert data in the table YelpRestaurants.

create_categories_table: Create the Categories table and insert categories into it.

update_category_id: Update the category in the main tables as user input changes.

update_average_rating: caculate the average of the rating of restaurants of different categories and update the averating column in the Categories tables as user input changes.

set_interactive_command: Set of interactive commands such as list, plot, new, help, and exit.


User Guide: A guide for how to use commmand to get the data needed. See help.txt for details 

** Note that the database keeps changing every time the user puts in a new command as the scope and content of data changes. The database in the file is just one example.**

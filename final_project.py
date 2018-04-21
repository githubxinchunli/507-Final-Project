import requests
import json
import sqlite3
from secret_data_sample import api_key
import plotly.plotly as py 
import plotly.graph_objs as go


yelp_url = 'https://api.yelp.com/v3/businesses/search'
header_yelp = {'authorization':'Bearer '+ api_key}
CACHE_FNAME = 'cache_yelp.json'

### Set up cache
### Refer to Twitter Caching example in class
try:
    cache_file = open(CACHE_FNAME, "r")
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    CACHE_DICTION = {}

def make_request_using_cache(url):
    if url in CACHE_DICTION:
        print("Retrieving cached data...")
        return CACHE_DICTION[url]
    else:
        print("Retrieving new data...")
        resp = requests.get(url, headers = header_yelp)
        CACHE_DICTION[url] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close()
        return CACHE_DICTION[url]

### Grab the restaurant information from Yelp: 
### A default parameter term restaurants
### A parameter that needs to be defined search_city
### Offset 
### Limit is set to be 50: the number of business results to return
def grab_restaurant_from_yelp(search_city, offset):
    baseurl = 'https://api.yelp.com/v3/businesses/search'
    parameters = {}
    parameters['term'] = 'restaurants'
    parameters['location'] = search_city
    parameters['offset'] = offset
    parameters['limit'] = 50
    responseurl = requests.get(yelp_url, params = parameters).url
    response = make_request_using_cache(responseurl)
    py_obj = json.loads(response)
    return py_obj

### Create Database YelpRestaurants: 
### Primary key Id
### CategoryID, CategoryName, Rating
### CategoryID is a foreign key that builds upon Id in the Database Categories

DBNAME = 'restaurant.db'
def build_restaurant_table():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    statement = 'DROP TABLE IF EXISTS "YelpRestaurants";'
    cur.execute(statement)
    conn.commit()

    statement = '''
        CREATE TABLE 'YelpRestaurants' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Name' TEXT,
            'CategoryID' TEXT,
            'CategoryName' TEXT,
            'Rating' REAL,
            FOREIGN KEY ('CategoryID') REFERENCES Categories('Id')
            );
        '''
    cur.execute(statement)
    conn.commit()
    conn.close()


### Inserte data into table
def insert_data():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

### Grab restaurants using the grab_restaurant_from_yelp function and put them into a list 
    yelp_lis_hund_rec = []
    for i in range (1,100,50):
        yelp_lis_hund_rec.append(grab_restaurant_from_yelp(city_inp, i)['businesses'])

### Iterate through the list and grab the parameter data we need (name, CategoryName, Rating)
### Id and CategoryID are generated automatically
### Insert them into Database YelpRestaurants 
    for each in yelp_lis_hund_rec:
        for ea in each:
            yelp_ins = (None, ea['name'],'', ea['categories'][0]['title'], ea['rating'])
            statement ='''
                INSERT INTO 'YelpRestaurants'
                VALUES (?, ?, ?, ?, ?);
                '''
            cur.execute(statement,yelp_ins)
    conn.commit()
    conn.close()


### Create Database Categories: 
### Id, CategoryName, AveRating
### Id is the primary key to which the CategoryID in the Database YelpRestaurants is referenced
def create_categories_table():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    statement = 'DROP TABLE IF EXISTS "Categories";'
    cur.execute(statement)
    conn.commit()

    statement = '''
        CREATE TABLE 'Categories' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'CategoryName' TEXT,
            'AveRating' REAL
            );
        '''
    cur.execute(statement)
    conn.commit()

### Grab the data from Database YelpRestaurants and insert the parameter value Category_Name
    statement = 'SELECT Distinct (CategoryName) FROM YelpRestaurants ORDER BY CategoryName ASC'
    cur.execute(statement)
    categ_l = cur.fetchall()

    for each in categ_l:
        ea_categ = each[0]
        categ_ins = (None, ea_categ, '')
        statement ='INSERT INTO "Categories" VALUES (?, ?, ?);'
        cur.execute(statement, categ_ins)
    conn.commit()
    conn.close()

### Update CategoryId in the Database YelpRestaurants every time the user puts in a new request (using UPDATE)
### Under the condition that CategoryName value remains consistent in the Database YelpRestaurants and Categories
def update_category_id():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    statement = 'SELECT c.Id, c.CategoryName FROM Categories AS c, YelpRestaurants as y WHERE c.CategoryName = y.CategoryName;'
    cur.execute(statement)
    cat_l = cur.fetchall()

    for each in cat_l:
        cat_tup = (each[0], each[1])   
        yelp_id_update = 'UPDATE YelpRestaurants SET CategoryID=? WHERE CategoryName=?;'
        cur.execute(yelp_id_update, cat_tup)

    conn.commit()
    conn.close()

### Update the average rating (AVG(Rating) every time the user puts in a new request (using UPDATE)
def update_average_rating():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    statement = '''
        SELECT CategoryID, ROUND(AVG(Rating),1) FROM YelpRestaurants
        GROUP BY CategoryID
        '''
    cur.execute(statement)
    for each in cur.fetchall():
        ave_tup = (each[1], each[0])
        cat_ave = 'UPDATE Categories SET AveRating = ? WHERE Id=?;'
        cur.execute(cat_ave, ave_tup)
    conn.commit()
    conn.close()


### Set up command for user to put in a request and get the result they need
### Build up MAX, MIN and AVG, top/bottom, limit
def set_up_command(command):
    inp_command = command.split()
    
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
   
    st_yelp = '''
        SELECT c.CategoryName, c.AveRating, T1.Highest, T1.Lowest
        FROM Categories as c
        JOIN
        (SELECT y.CategoryID, y.CategoryName, MAX(y.Rating) AS Highest, MIN(y.Rating) as Lowest
        FROM YelpRestaurants as y GROUP BY y.CategoryID) as T1 on c.ID = t1.Categoryid
        ORDER BY AveRating DESC
        '''
    cur.execute(st_yelp)
    yelp_results = cur.fetchall()

    valid_tot_yelp = len(yelp_results)

    if inp_command[1] == 'yelp':
        ordby = 'DESC'
        lim = ''
        limby = ''
        ret_error = False

        try:
            if inp_command[2] is not None:
                if inp_command[2] != 'top' and inp_command[2] != 'bottom':
                    ret_error = True
                    print('Check that third command is either "top" or "bottom".')

                if inp_command[2] == 'top':
                    ordby = 'DESC'

                if inp_command[2] == 'bottom':
                    ordby = 'ASC'
        except:
            pass

        try:
            if inp_command[3] is not None:
                try:
                    lim = 'LIMIT'
                    limby_int = int(inp_command[3])

                    if inp_command[1] == 'yelp':
                        if limby_int <= valid_tot_yelp:
                            limby = limby_int
                        else:
                            lim = ''
                            ret_error = True
                            print('Number entered is greater than total number of records.')
                except:
                    lim = ''
                    ret_error = True
                    print('Check that fourth command is valid.')
        except:
            pass

        global yelp_count

        yelp_count = 0

        if inp_command[1] == 'yelp' and ret_error is False:
            st_yelp2 = '''
                SELECT c.CategoryName, c.AveRating, T1.Highest, T1.Lowest
                FROM Categories as c
                JOIN
                (SELECT y.CategoryID, y.CategoryName, MAX(y.Rating) AS Highest, MIN(y.Rating) as Lowest FROM YelpRestaurants as y GROUP BY y.CategoryID) as T1 on c.ID = t1.Categoryid
                ORDER BY AveRating {}
                {} {}
                '''.format(ordby, lim, limby)

            cur.execute(st_yelp2)
            yelp_results2 = cur.fetchall()
            yelp_count += 1

            return yelp_results2
        
        else:
            return []

    conn.close()


### Build a Class for data processing
class ResultList():
    def __init__(self, init_tuple):
        self.category = init_tuple[0]
        self.averate = init_tuple[1]
        self.maxrate = init_tuple[2]
        self.minrate = init_tuple[3]


### Load help text for command guidance
def load_help_text():
    with open('help.txt') as f:
        return f.read()


### Set up interactive commands 
### Navigate the user with a set of interactive commands: list, plot, new, help, exit. 
def set_interactive_command():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()

    global yelp_ret_val

    yelp_ret_val = []
    
    while True:
        inputcommand = input('\nEnter command (type "help" to view list of commands or "exit" to quit): ').lower()
        inp_command_lis = inputcommand.split()
        valid_start = ['list', 'plot', 'new', 'help', 'exit']

        try:
            if inp_command_lis[0] in valid_start:
                go_on = True
            else:
                go_on = False
                print('Invalid command.')
        except:
            go_on = False
            print('Invalid command.')

        if go_on == True:
            if inp_command_lis[0] == 'exit':
                print('Bye!\n')
                break

            if inp_command_lis[0] == 'new':
                user_search_bar()
                yelp_ret_val= []
                break

            if inp_command_lis[0] == 'help':
                help_text = load_help_text()
                print(help_text)

            if inp_command_lis[0] == 'list':

                try:
                    if inp_command_lis[1] is not None and inp_command_lis[1] == 'yelp' and inp_command_lis[2] is not None:
                        yelp_ret_val = set_up_command(inputcommand)

                        if yelp_ret_val != []:

                            print('\nRESTAURANT CATEGORIES AND RATINGS FROM ' + inp_command_lis[1].upper())
                            print('{:25} {:^10} {:^10} {:^10}'.format('\nCATEGORY', ' AVE', ' MAX', ' MIN'))

                            my_objects = []
                            for each_tup in yelp_ret_val:
                                my_objects.append(ResultList(each_tup))

                            for obj in my_objects:
                                print('{:25} {:^10} {:^10} {:^10}'.format(obj.category, obj.averate, obj.maxrate, obj.minrate))

                    else:
                        print('Check source input.')
                
                except:
                    print('Invalid command.')                
        
            if inp_command_lis[0] == 'plot':
                valid_charts = ['bar', 'pie', 'donut']

                st_group = '''
                    SELECT ca.CategoryName, ca.AveRating
                    FROM Categories as ca;
                '''
                cur.execute(st_group)
                group_results = cur.fetchall()

                st_pie_yelp = '''
                    SELECT CategoryName, COUNT(Id) from YelpRestaurants
                    GROUP BY CategoryName
                    ORDER BY COUNT(Id) DESC
                    '''
                cur.execute(st_pie_yelp)
                pie_yelp = cur.fetchall()

                st_donut = '''
                    SELECT CategoryName, COUNT(Id) 
                    FROM YelpRestaurants 
                    GROUP BY CategoryName 
                '''
                cur.execute(st_donut)
                donut_results = cur.fetchall()

                try:
                    if inp_command_lis[1] is not None and inp_command_lis[1] in valid_charts:
                        cont = True

                    elif inp_command_lis[1] is not None and inp_command_lis[1] not in valid_charts:
                        cont = False
                        print('Invalid chart type.')
                    else:
                        pass
                except:
                    cont = False
                    print('Invalid chart type.')
    
                if cont == True:
                    if inp_command_lis[1] == 'bar' and len(inp_command_lis) == 2:
                        if yelp_ret_val != []:
                            x_names = []
                            y_averate = []
                            for each in yelp_ret_val:
                                x_names.append(each[0])
                                y_averate.append(each[1])
                            data = [go.Bar(x = x_names,y = y_averate)]
                            py.plot(data, filename='yelp-bar', auto_open=True)

                        else:
                            print('No result set to map. Use the "list" command to generate a result set.')

                    elif inp_command_lis[1] == 'pie' and len(inp_command_lis) == 2:

                        yelp_labels = []
                        yelp_values = []
                        for each in pie_yelp:
                            yelp_labels.append(each[0])
                            yelp_values.append(each[1])

                        labels = yelp_labels
                        values = yelp_values

                        trace = go.Pie(labels=labels, values=values)

                        py.plot([trace], filename='basic_pie_chart_yelp', auto_open=True)

                        
                    elif inp_command_lis[1] == 'donut' and len(inp_command_lis) == 2:

                        yelp_labels = []
                        yelp_values = []
                        for each in donut_results:
                            yelp_labels.append(each[0])
                            yelp_values.append(each[1])

                        fig = {
                            "data":
                            [{
                              "values": yelp_values,
                              "labels": yelp_labels,
                              "domain": {"x": [0, .48]},
                              "name": "Yelp",
                              "hoverinfo":"label+percent+name",
                              "hole": .4,
                              "type": "pie"
                            }],
                          "layout": {
                                "title":"Yelp Restaurant Count",
                                "annotations": [
                                    {
                                        "font": {
                                            "size": 40
                                        },
                                        "showarrow": False,
                                        "text": "Yelp",
                                        "x": 0.20,
                                        "y": 0.5
                                    }
                                ]
                            }
                        }
                        py.plot(fig, filename='donut_chart_yelp', auto_open = True, validate=False)

                    else:
                        print('Invalid command.')

### User Search bar to select a number that represents a city 
### Beginning of the program
def user_search_bar():
    global city_inp
    terminate = False

    places = ['Atlanta, GA', 'Austin, TX', 'Boston, MA', 'Charleston, SC', 'Chicago, IL', 'Columbus, OH', 'Dallas, TX', 'Denver, CO', 'Detroit, MI', 'Houston, TX', 'Las Vegas, NV', 'Los Angeles, CA', 'Miami, FL', 'Nashville, TN', 'New Orleans, LA', 'New York, NY', 'Orlando, FL', 'Portland, OR', 'San Antonio, TX', 'San Diego, CA', 'San Francisco, CA', 'Savannah, GA', 'Seattle, WA', 'St. Louis, MO', 'Washington, DC']
    
    print('\nMajor cities in America:')
    for number, each in enumerate(places, start = 1):
        print(number, each)

    while True:
        place_index = input('\nEnter number to search or type "exit" to quit: ').lower()

        if place_index == 'exit':
            print('Program terminated.\n')
            terminate = True
            break
        
        else:
            try:
                city_inp = places[int(place_index) -1].split(',')[0]
                if int(place_index) < 26:
                    print('\nSearching Yelp for restaurants in ' + city_inp + '... (max no. of records per source = 100)\n')
                    break
                else:
                    print('Enter a valid number.')
            except:
                print('Enter a valid number.')

    if terminate == False:
        build_restaurant_table()
        insert_data()
        create_categories_table()
        update_category_id()
        update_average_rating()
        set_interactive_command()


### RUN PROGRAM ###
if __name__=="__main__":
    user_search_bar()

import unittest
from final_project import *

### Test based on DETROIT search ###

class TestDatabase(unittest.TestCase):

    def test1_restaurants_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = 'SELECT Name FROM YelpRestaurants'
        results = cur.execute(sql)
        result_list = results.fetchall()

        # self.assertIn(('Bakersfield',), result_list, 'testing Bakersfield in list')
        self.assertTrue(len(result_list)<=100, 'testing record count not exceeds 100')

        sql = '''
            SELECT Name, CategoryName, Rating
            FROM YelpRestaurants
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        # print(result_list)
        self.assertEqual(type(result_list[0][1]), str, 'restaurant name is a string')
        self.assertEqual(type(result_list[0][2]), float, 'restaurant rating is a float')

        # self.assertEqual(result_list[0][1], 'Breakfast & Brunch', 'testing category is Breakfast & Brunch')
        # self.assertEqual(result_list[0][2], 4.0, 'testing rating is 4.0')

        sql = 'SELECT * FROM YelpRestaurants'
        
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertEqual(len(result_list[0]), 5, 'testing record is a 5-value tuple')

        conn.close()


    def test2_categories_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = 'SELECT * FROM Categories'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertEqual(result_list[10][0], 11, "Autoincrement is correct")
        # self.assertIn(('Burgers',), result_list, 'testing Burgers in list')
        # self.assertIn(('Chinese',), result_list, 'testing Chinese in list')

        conn.close()


class TestYelpSearch(unittest.TestCase):

    def test3_yelp_list_command(self):
        results = set_up_command('list yelp top 10')
        self.assertEqual(len(results), 10, 'testing limit works' )
        self.assertEqual(len(results[0]), 4, 'testing record is a 4-value tuple')


### RUN TEST CASE ###
unittest.main(verbosity = 2)
import csv
import sys
import MySQLdb

def main() :
	#Establishing connection with the database server. 
	mydb = MySQLdb.connect(host="localhost",port=3306,user="root",passwd="8687",db="imdb") 
	
	#Creating a cursor for query execution
	cursor = mydb.cursor()

	csv.field_size_limit(sys.maxsize)
	#reading data from dataset file data.tsv
	csv_data = csv.reader(file('data.tsv'), delimiter='\t')
	next(csv_data)

	#Execution query
	cursor.execute('CREATE TABLE IF NOT EXISTS imdb.basic (\
												  titleId LONGTEXT NULL,\
												  ordering LONGTEXT NULL,\
												  title LONGTEXT NULL,\
												  region LONGTEXT NULL,\
												  language LONGTEXT NULL,\
												  types LONGTEXT NULL,\
												  attributes LONGTEXT NULL,\
												  isOriginalTitle LONGTEXT NULL);')
	for row in csv_data:
		#Executing query
		cursor.execute('INSERT INTO imdb.akas(titleId, ordering, title, region, language\
	    	, types, attributes, isOriginalTitle)' \
	          'VALUES(%s,%s,%s,%s,%s,%s,%s,%s)', row)
	
	#Commiting the transaction to the database
	mydb.commit()
	
	#close the connection to the database.
	cursor.close()
	print("Done")

if __name__ == '__main__':
	main()
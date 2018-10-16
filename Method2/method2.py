import MySQLdb
from bs4 import BeautifulSoup
import requests
import pandas as pd
import datetime
import calendar
import json
from warnings import filterwarnings
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
try: 
	from googlesearch import search 
except ImportError:  
	print("No module named 'google' found") 

filterwarnings('ignore', category = MySQLdb.Warning)

def add_user_data(Email, Tv_series) :
	"""This method stores the Email and subscription of opted TV series in MySqlDB database.
	:param Email : The email address of the subscriber.
	:param Tv_series: String of Subscribed TV series separated by comma(, ).
	:return: returns nothing"""

	try: 
		#Establishing connection with the database server. 
		db_connection= MySQLdb.connect(host="localhost",port=3306,user="root",passwd="8687",db="imdb")
	except: 
		print("Can't connect to database") 
		return 0

	#Creating a cursor
	cursor=db_connection.cursor()

	# cursor.execute('DROP TABLE IF EXISTS imdb.user_table;') 
	cursor.execute('CREATE TABLE IF NOT EXISTS imdb.user_table(\
						email LONGTEXT NOT NULL,\
						tv_series LONGTEXT NOT NULL);') 
	
	#query execution
	cursor.execute("INSERT INTO imdb.user_table( email, tv_series)" "VALUES(%s, %s);",(Email, Tv_series,))
	
	#commiting the current transaction
	db_connection.commit()

	#close database connection
	db_connection.close()



def get_tv_series_list(email) :
	"""This method returns the TV series for which updates are subscibed for a particular email address.
	:param email : Email address of user.
	:return : returns the string consisting of TV series subscribed for user with that Email address"""
	try:
		#Establishing connection with the database server.
		db_connection= MySQLdb.connect(host="localhost",port=3306,user="root",passwd="8687",db="imdb") 
	except: 
		print("Can't connect to database") 
		return 0

	#cursor created
	cursor=db_connection.cursor() 

	#query executed
	cursor.execute("SELECT tv_series FROM imdb.user_table WHERE email=%s;",(email,))

	#Output of query stored in list
	m = cursor.fetchone()  
	
	#connection closed
	db_connection.close() 
	
	return m;

def googleSearch(tv_series) :
	"""This method searches the tv_series in google using google API and return the links as result of search
	:param tv_series: TV series to be searched on google
	:return : returns the link of imdb website of tv_series"""
	
	#query : Text to be searched on google wit its api.
	query = "imdb tv series : " + tv_series
	 
	#links : Links of the pages displayed after performing google search. 
	links = list(search(query, tld="co.in", num=3, stop=1, pause=2))  

	#links[0] : first link of the page(Google search generally gives the desired result on first link)
	return links[0]	

def scrapeAirDates (link) :
	"""This method scraped airdates of episode of latest season of a TV series
	:param link : Hyperlink of the webpage to be scraped
	:return : returns pandas object containing airdates of episode of latest season"""
	found = False
	while not found :
		tv_series_page = requests.get(link)
		if(tv_series_page.ok) :
			found = True

	#soup1 : BeautifulSoup object of html content of the imdb TV series website
	soup1 = BeautifulSoup(tv_series_page.content, 'html.parser')

	#episode_widget : extracting all div tags with particular id.
	episode_widget = soup1.find('div', id='title-episode-widget')

	#a_tag = Extracting first a tag i.e. which contains the hyperlink of latest season
	a_tag = episode_widget.find('a')

	href = a_tag['href']
	
	found = False
	while not found :
		episode_page = requests.get("https://www.imdb.com"+href)
		if(episode_page.ok) :
			found = True

	# print("https://www.imdb.com"+href)
	soup2 = BeautifulSoup(episode_page.content, 'html.parser')

	#div_airdate : Extracting all div tags with class as airdates
	div_airdate = soup2.select("div .airdate")
	
	#list containing all airdates
	airdates = []
	
	#list containing all airdates
	for ad in div_airdate :
		#For each div tag extract its content i.e. airdate.
		airdate = ad.get_text().strip()
		if(airdate) :
			airdates.append(airdate)
	
	#pd_airdates : Pandas object for all airdates
	pd_airdates = pd.DataFrame({"airdate" : airdates})
	return pd_airdates


def convertDateinFormat(date) :
	"""This method converts the date of form "15 Jan. 2019" or "2019" to datetime object for comparing with current date and time.
	:param date : Date in the form of string.
	:return : Returns datetime object for the input date."""
	
	#Dictionary of months abbreviation name with their respective numbers i.e. months_dict[Jan]=1, months_dict[Feb]=2   
	months_dict = {abbr: num for num,abbr in enumerate(calendar.month_abbr)}
	
	#Separating Days, Months and Years and storing it in a list date_list.
	date_list =  date.split(" ")
	
	if(len(date_list) == 1) :
		#When only year is present
		day = "1"
		month_abr = "Jan"
		year = date_list[0]
	elif(len(date_list) == 2) :
		#When month and year is present
		day = "1"
		month_abr = date_list[0]
		year = date_list[1]
		month_abr = month_abr.strip(".")
	else :
		#When day, month and year all are present
		day, month_abr, year = map(str,date_list)
		month_abr = month_abr.strip(".")
	month = months_dict[month_abr]
	#month stores the respective number representation for the month.
	return datetime.datetime(int(year), month, int(day))


def getAirdateStatus(pd_airdates, dim, CurrentDate) :
	""" This method Compares the Expected date of the episodes with the Current date and tells the status airdate of the TV series 
	:param pd_airdates : Pandas object storing the airdates of all episodes of last season of a TV series
	:param dim : num of rows of pd_airdates pandas object
	:param CurrentDate : Current date as datetime object 
	:return : returns a string consisting of status of the TV series
	"""
	msg_status = ""
	flag = True
	for index in range(dim) :
		"""For airdate of each episode of the latest season check -
			-(Finished streaming all episodes)whether all airdates are less than current date
			-(Next episode Release date)whether there exists an episode with an airdate more than current date and it is not first episode
			-(Next season Release date)whether the first episode has airdate for than curret date"""
		date = pd_airdates.iloc[index,0]
		Date = date.split()
		ExpectedDate = convertDateinFormat(date)
		# print(ExpectedDate)
		if(ExpectedDate > CurrentDate) :
			flag = False
			if(index == 0) :
				msg_status = msg_status + "The next season begins in " + date +".\n"
			else :
				msg_status = msg_status + "Next episode airs on " + date + ".\n"
			break
		elif(len(Date) == 1) and (datetime.date.today().year == int(date) ) :
			flag = False
			if(index == 0) :
				msg_status = msg_status + "The next season begins in " + date +".\n"
			else :
				msg_status = msg_status + "Next episode airs on " + date + ".\n"
			break
			
	if(flag) :
		msg_status = msg_status + "The show has finished streaming all its episodes." + "\n"

	return msg_status


def send_email(EmailId, message) :
	"""This method sends email using smtp gmail account 
	:param EmailId : Email address of the user
	:param message : the message which is send over email"""

	# create message object instance
	msg_obj = MIMEMultipart()
	 
	# setup the parameters of the message
	password = "Ayushhsuya1671"
	msg_obj['From'] = "iim2015004ayush@gmail.com"
	msg_obj['To'] = EmailId
	msg_obj['Subject'] = "Subscription"
	 
	# add in the message body
	msg_obj.attach(MIMEText(message, 'plain'))
	 
	#create server
	server = smtplib.SMTP('smtp.gmail.com', 587)
	
	#starting tls server
	server.starttls()
	 
	# Login Credentials for sending the mail
	server.login(msg_obj['From'], password)
	 
	 
	# send the message via the server.
	server.sendmail(msg_obj['From'], msg_obj['To'], msg_obj.as_string())
	
	#Exiting the mail server.
	server.quit()
	
	#Output message
	print("Successfully sent email to %s:" % (msg_obj['To']))


def main() :
	""" Main method to take Inputs as - Number of users and for each user - its email address and list of TV series subscribed.
	:return : Returns nothing"""
	print("Enter number of users :")
	num_of_users = int(input())

	#data : a list of lists of user data[email,tv_series].
	data = []
	
	#taking input as Email and TV series for num_of_users  
	while num_of_users > 0 :
		num_of_users = num_of_users - 1
		print()
		print("Email address :", end=" ")
		email = input()
		print("TV Series :", end=" ")
		tvSeriesList = input()

		#adds data of a user to the database.
		add_user_data(email,tvSeriesList)
		data.append([email, tvSeriesList])
		
	#CurrentDate : datetime object for current date.
	CurrentDate = datetime.datetime.now()

					
	for row in data :
		#For each user search status of all its subscribed TV series
		EmailId = row[0]
		msg = ""
		tvSeriesList = row[1].split(",")
		#tvSeriesList : contains all the Tv series subscribed by a user in form of a list.
		
		for tv_series in tvSeriesList :
			#loop for each TV series in TV series list.
			tv_series = tv_series.strip()

			msg_tv_series = "Tv series name: " + tv_series + "\n"
			msg_status = "Status: "
			
			#link : Contains the IMDB link of TV series after scraping from google search
			link = googleSearch(tv_series)
			
			#pd_airdates : Pandas object for all airdates
			pd_airdates = scrapeAirDates(link)

			#dim : Dimensions of pandas object pd_airdates
			dim = pd_airdates.shape[0]

			#msg_status : Status of release date of TV series
			msg_status = getAirdateStatus(pd_airdates, dim, CurrentDate)

			msg = msg + (msg_tv_series + msg_status + "\n")	

		print(EmailId)
		print(msg)

		#send_email(EmailId, msg)

if __name__ == '__main__':
	main()
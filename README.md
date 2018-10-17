# Entertainment-tracker 
Keep track of your favourite TV-series and always stay updated with latest information. 

## Installation

### Requirements
* Linux
* mysql-server
* Python 3.3 and up
* python-mysqldb
* BeautifulSoup package
* google search package
* smtplib library
* Good internet connection for web scraping

`$ sudo apt-get install python3-mysqldb`

`$ sudo apt-get install python-mysqldb`

`$ sudo apt-get install python3-bs4`

`$ pip install google`


## Usage

##### For approach-1 :
###### Navigate to [Entertainment-tracker/Approach1/](https://github.com/AyushAgnihotri/Entertainment-tracker/tree/master/Approach1)

`$ python Approach1.py`


##### For approach-2 :
###### Navigate to [Entertainment-tracker/Approach2/](https://github.com/AyushAgnihotri/Entertainment-tracker/tree/master/Approach2)

`$ python Approach2.py`

##### For approach-3 :
###### Navigate to [Entertainment-tracker/Approach3/](https://github.com/AyushAgnihotri/Entertainment-tracker/tree/master/Approach3)


`$ python Approach3.py`

----

##### To view the user details :
The user details are stored in MySQL database as :

 `imdb.user_table(email, tv_series)`

###### Note : Database has been hosted over a DigitalOcean Droplet (139.59.91.20:3306) which is accessible publicly.

To view the user details, connect with mysql database :

`$ sudo mysql -u root -p imdb -h 139.59.91.20`

`Password : agnihotri987`

Execute the query

`$ mysql>  SELECT * FROM imdb.user_table;`


### Description :

#### Approach-1 :

The URL of a TV series on IMDb website has the following format :

 `https://www.imdb.com/title/tt1632701/?ref_=fn_al_tt_1` 

, where `tt1632701` is TitleId of TV-series with Title "Suits". Titles of each and every TV-series and movie are mapped with different TitleId's which can not be generated by simple logic. In order to get the TitleId values of TV series, the dataset([title.akas.tsv.gz](https://datasets.imdbws.com/)) of IMDb TV-series and Movies is used. The descriptions of dataset are found here -[IMDb datasets](https://www.imdb.com/interfaces/).
The dataset is stored in MySQL database as `imdb.akas(titleId, ordering, title, region, language, types, attributes, isOriginalTitle)`.[Python script for storing dataset in database can be found in [Entertainment-tracker/Approach1/](https://github.com/AyushAgnihotri/Entertainment-tracker/tree/master/Approach1)]. The corresponding TitleId's of Movies or TV-series with similar name are stored in a list. Each title Id is used to scrape the content of website of TV-series or Movie checked sequentially whether it is TV-series till a TV-series is found. The scraped page is searched for the hyperlink of latest season of TV series. Using hyperlink of latest season, the information of all its episodes is scraped and Airdates are stored. Stored airdates are further compared with current date and output is send to the user's email address using gmail SMTP.

#### Approach-2 :

The name of tv series is searched as `imdb tvseries : "TV_SERIES"` over `www.google.co.in/` via google search package (assuming the topmost link of google search result to be most relevant). The topmost link is scraped and hyperlink for latest season is fetched. Using hyperlink of latest season, the information of all its episodes is scraped and Airdates are stored. Stored airdates are further compared with current date and output is send to the user's email address using gmail SMTP.

#### Approach-3 :
The name of TV series is searched over imdb website as `https://www.imdb.com/find?ref_=nv_sr_fn&q=suits&s=all` (where "suits" is a TV series), the page is scraped and all the hyperlinks of TV-series or Movies with similar name are stored. Stored hyperlinks are further scraped and check whether they are of a TV series. Hyperlink found to be of a TV series is considered to be relevant and scraped. The scraped page is further used to fetch the hyperlink of latest season of TV series. Using hyperlink of latest season, the information of all its episodes is scraped and Airdates are stored. Stored airdates are further compared with current date and output is send to the user's email address using gmail SMTP.


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

# Import pandas and numpy
import pandas as pd
import numpy as np
# Import the GoogleNews package to fetch the news articles
from GoogleNews import GoogleNews

googlenews = GoogleNews()

keywords = ['ETH', 'Ethereum', 'ETH-USD']
googlenews.set_time_range('08/02/2021', '08/03/2021')
# googlenews.set_period('7d')
googlenews.set_lang('en')

# Dataframe to store the news article information
article_info = pd.DataFrame(columns=['Date', 'Time', 'Title', 'Articles', 'Link'])


# Gathering all the data of the current page to one dataframe
# The frame.append method is deprecated and will be removed from pandas in a future version.
# Use pandas.concat instead.
def newsfeed(article_info, raw_dictionary):
    for i in range(len(raw_dictionary) - 1):
        if raw_dictionary is not None:
            # Fetch the date and time and convert it into datetime format
            date = raw_dictionary[i]['datetime']
            date = pd.to_datetime(date)
            # Fetch the title, time, description and source of the news articles
            title = raw_dictionary[i]['title']
            time = raw_dictionary[i]['date']
            articles = raw_dictionary[i]['desc']
            link = raw_dictionary[i]['link']
            # Append all the above information in a single dataframe
            article_info = article_info.append({'Date': date, 'Time': time, 'Title': title,
                                                'Articles': articles, 'Link': link}, ignore_index=True)
        else:
            break

    return article_info


# Dataframe containing the news of all the keywords searched
articles = pd.DataFrame()

# Each keyword will be searched seperately and results will be saved in a dataframe
for steps in range(len(keywords)):
    string = (keywords[steps])
    googlenews.search(string)

    # Fetch the results
    result = googlenews.results()

    # Number of pages up to which you want to fetch news articles
    total_pages = 1

    for steps in range(total_pages):
        # Variable consists of pages specified by user so using "for loop" to retrieve all the data in dataframe
        googlenews.get_page(steps)
        feed = newsfeed(article_info, result)

    articles = articles.append(feed)

    # Clear off the search results of previous keyword to avoid duplication
    googlenews.clear()

shape = articles.shape[0]

# Resetting the index of the final result
articles.index = np.arange(shape)
articles
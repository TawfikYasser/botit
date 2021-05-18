from bs4 import BeautifulSoup
import requests

def crawling(website_link, link_class):
    '''
    Args: website_link = string; link of website to be crawled
          link_class = string; class name for job link on website
    Returns: jobs_link = list; list of jobs 
    '''
    
    # get content of website and parse it
    website_request = requests.get(website_link, timeout=5)
    website_content = BeautifulSoup(website_request.content, 'html.parser')
    
    # extract job description
    jobs_link = website_content.find_all(class_ = link_class)
    return jobs_link

def send_message(chat_id, text):
    '''
    Takes the chat id of a telegram bot and the text that was  crawled from the
    website and sends it to the bot
    Args: chat_id = string; chat id of the telegram bot, 
          text = string; crawled text to be sent
    Returns: None
    '''
    
    parameters = {'chat_id': chat_id, 'text': text}
    message = requests.post(bot + 'sendMessage', data=parameters)

import os
import psycopg2
import sqlite3 as lite

def check_result_send_mess():
    '''
    This function looks up the values stored in the SQL database
    and compares them to the crawled jobs and sends out any jobs
    not in the db to the telegram bot
    Args: None
    Returns: None
    '''
    
    # try to create SQL database and table to store jobs in, else send error message to bot
    try:
       DATABASE_URL = os.environ['DATABASE_URL']
       conn = psycopg2.connect(DATABASE_URL, sslmode='require')
       jobs_db = conn.cursor()
       jobs_db.execute('CREATE TABLE IF NOT EXISTS jobs (id SERIAL, job TEXT NOT NULL)')
    except:
       send_message(chat_id, 'The database could not be accessed')
        
    # crawl the jobs from website
    jobs_link_pm = crawling('https://www.linkedin.com/jobs', 'jsc_c_ci')
    
    # check if there were new jobs added
    for item in jobs_link_pm:
        job_exists = jobs_db.execute('SELECT job FROM jobs WHERE job = %s', [item.text])
        
        if len(jobs_db.fetchall()) != 1:
            mess_content = item.text + item['href']
            send_message(chat_id, mess_content)
            jobs_db.execute('INSERT INTO jobs (job) VALUES (%s);', [item.text])
            conn.commit()
        else:
            continue
            
    # end SQL connection
    jobs_db.close()


import schedule

# bot and chat ids
bot = '1849763275:AAH7RHF_nE1SZQ09lY_o0ISzg__FHrtcHh0'
chat_id = 1269048570

# schedule crawler
schedule.every().day.at("21:10").do(check_result_send_mess)

# run script infinitely
while True:
    schedule.run_pending()
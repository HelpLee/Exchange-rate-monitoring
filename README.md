# Exchange-rate-monitoring
This is an exchange rate monitoring script, using the conversion between Chinese Yuan (CNY) and Euros (EUR) as an example. You can modify this script for other currencies. The data source is the Bank of China.
import requests  
from bs4 import BeautifulSoup  
import time  
import pandas as pd  
from datetime import datetime  
import os  
import smtplib  
from email.mime.text import MIMEText  
from email.mime.multipart import MIMEMultipart  
from smtplib import SMTP_SSL  
import threading  

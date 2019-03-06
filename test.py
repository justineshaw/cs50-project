from flask import Flask, flash, jsonify, redirect, render_template, request, session
import requests
import urllib.parse
from urllib.parse import urlparse


try:
        # response = requests.get(f"https://api.iextrading.com/1.0/stock/{urllib.parse.quote_plus(symbol)}/quote")
        # "https://api.edamam.com/search?q=chicken&app_id=${YOUR_APP_ID}&app_key=${YOUR_APP_KEY}&from=0&to=3&calories=591-722&health=alcohol-free"
    o = urllib.parse.urlparse("http://www.cwi.nl:80/%7Eguido/Python?search=1")
    print(o.query)
    if o.query == "search=1":
        print("Nice!")

except (KeyError, TypeError, ValueError):
    print("error")
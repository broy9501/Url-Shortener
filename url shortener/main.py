from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import string, random, json, datetime
#import pyshorteners

app = Flask(__name__)

FILEPATH = 'urls.json'
#BASEURL = 'https://b.roy/'


def load_urls():
    try:
        with open(FILEPATH, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_urls(urls):
    with open(FILEPATH, 'w') as file:
        return json.dump(urls, file)
    
def generateShortUrl(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for x in range(length))

@app.route('/')
def home():
    urls = load_urls()
    sorted_urls = sorted(urls.items(), key=lambda x: x[1]['createdAt'], reverse=True)
    latest_urls = sorted_urls[:5]
    return render_template('home.html', latestUrls=latest_urls)

@app.route('/shorten', methods=['POST'])
def shorten():
    #Retrive the url from the user and load up the existing URLs
    urlRecieved = request.form["urlShort"]
    urlCustom = request.form["urlCustom"]
    urls = load_urls()    

    #If the user creates a customised shorten link
    if urlCustom:
        if urlCustom in urls:
            return "Custom URL already exists. Please choose another one.", 400
        else:
            shortUrl = urlCustom
    else:
        #Create the short URL and check if it is unique in the urls
        shortUrl = generateShortUrl()
        while shortUrl in urls:
            shortUrl = generateShortUrl

    #update and save the urls with the clicks initially to 0 as well
    urls[shortUrl] = {"original_url": urlRecieved, "clicks": 0, "createdAt": datetime.datetime.now().isoformat()}
    save_urls(urls)

    #Sort the URLs and get the latest 5 URLs
    sortedUrls = sorted(urls.items(), key=lambda x: x[1]['createdAt'], reverse=True)
    latestUrls = sortedUrls[:5]

    #Join the base url and the short url together
    shortUrlFull = 'http://127.0.0.1:5000/' + shortUrl
    return render_template("home.html", new_url=shortUrlFull,  latestUrls=latestUrls)

@app.route("/<shortUrl>")
def redirect_to_short(shortUrl):
    urls = load_urls()
    #Each time the link is used, it update the click by one showing how many times the link has been used
    if shortUrl in urls:
        urls[shortUrl]['clicks'] += 1
        save_urls(urls)
        return redirect(urls[shortUrl]['original_url'])
    else:
        return "URL not found", 404

# def home():
#     if request.method == "POST": 
#         urlRecieved = request.form["urlShort"]
#         shortUrl = pyshorteners.Shortener().isgd.short(urlRecieved)
#         return render_template("home.html", old_url=urlRecieved, new_url=shortUrl)
#     else:
#         return render_template("home.html")

if __name__ == "__main__":
    app.run()

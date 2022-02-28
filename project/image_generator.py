import os
import requests
import json
import functools
from flask import jsonify, request

def show_authentication():
    response = jsonify("Authorize")
    response.status_code = 401
    response.headers['WWW-Authenticate'] = 'Basic realm="Main"'
    return response

def authorize(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not auth.username == os.environ["USERNAME"] and not auth.password == os.environ["PASSWORD"]:
            return show_authentication()
        return f(*args, **kwargs)
    return decorated

@authorize
def get_image(request):

    url = "https://api.bing.microsoft.com/v7.0/images/search?"

    if not request.args.get("query"):
        return "query must be provided in the query parameters", 400

    url = url + "&q=" + request.args.get("query")

    if request.args.get("size"):
        url = url + "&size=" + request.args.get("size")

    url = url + "&count=1"

    image_data = requests.get(url, headers={"Ocp-Apim-Subscription-Key": os.environ['API_KEY']})

    image_url = json.dumps(image_data.json()["value"][0]["thumbnailUrl"]).strip('\"')

    return {"url": image_url}

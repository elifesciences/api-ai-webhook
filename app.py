#!/usr/bin/env python

import json
import os

from flask import Flask
from flask import make_response
from flask import request
from urllib2 import Request, urlopen

import requests

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print('Request:')
    print(json.dumps(req, indent=4))

    r = make_response(json.dumps(processRequest(req), indent=4))

    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    # curl -v "https://api.elifesciences.org/search?subject\[\]=neuroscience&order=desc&per-page=5" | jq .items[].title

    if req.get('result').get('action') != "articles.list":
        return {}

    subject_id = req.get('result').get('parameters').get('subject')

    api_gateway_uri = 'https://prod--gateway.elifesciences.org'

    q = Request(api_gateway_uri + '/subjects/' + subject_id)

    q.add_header('Accept', 'application/vnd.elife.subject+json;version=1')

    print(api_gateway_uri + '/subjects/' + subject_id)
    print(q.headers)

    subject = urlopen(q)

    titles_url = "https://api.elifesciences.org/search?subject[]={subject}&order=desc&per-page=5".format(subject=subject_id)
    titles_response = requests.get(url=titles_url)

    if titles_response.status_code != 200:
        return {}

    if subject.getcode() != 200:
        return {}

    subject = json.loads(subject.read())

    titles = [item['title'] for item in titles_response.json()['items']]

    print('titles: ', titles)

    speech_text = 'Articles about {}, '.format(subject.get('name'))
    speech_text += ', '.join(titles)

    display_text = speech_text

    return {
        'speech': speech_text,
        'displayText': display_text,
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))

    print("Starting app on port %d" % port)

    app.run(debug=True, port=port, host='0.0.0.0')

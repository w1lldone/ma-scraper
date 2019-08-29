import os
from flask import Flask, render_template, request
import csv
import http.client
import json
from datetime import date

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static','documents')

app = Flask(__name__, static_url_path='/static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def index(result=None):
    if request.args.get('year', None):
        result = crawler(request.args['year'])
    return render_template('index.html', result=result)

def crawler(year):
    conn = http.client.HTTPSConnection("api.labs.cognitive.microsoft.com")

    payload = "expr=And(Composite(AA.AfN=='gadjah mada university'),Y="+year+",L='en')&attributes=Id,C.CId,C.CN,L,Y,Ti,CC,J.JN,J.JId,AA.AuN,AA.AfN,E.DOI&offset=0&count=10000"

    headers = {
        'content-type': "application/x-www-form-urlencoded",
        'ocp-apim-subscription-key': "910f7d70387c416a8a3fedfe5141251d",
    }

    conn.request("POST", "/academic/v1.0/evaluate", payload, headers)

    response = conn.getresponse()
    v = json.loads(response.read().decode("utf-8"))
    no = 1

    with open(os.path.join(app.config['UPLOAD_FOLDER'], str(date.today()) + '-MA-(data for '+year+').csv'), mode='w') as f:
        z = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        z.writerow(["No", "Title", "Author", "Year", "DOI"])
        for x in v['entities']:
            # x1 = str(x['AA'])
            # x2 = x1.replace("'}, {'AfN': '",", ")
            try:
                z.writerow([
                    no, x['Ti'], x['AA'], x['Y'], x['DOI']
                ])
            except KeyError:
                z.writerow([
                    no, x['Ti'], x['Y'], None
                ])
            no += 1

    return str(date.today())+'-MA-(data for '+year+').csv'

if __name__ == '__main__':
    app.run()

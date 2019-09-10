import os
from flask import Flask, render_template, request
from pyhocon import ConfigFactory
import csv
import http.client
import json
from datetime import date, datetime
import multiprocessing

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static', 'documents')
CONFIG_FOLDER = os.path.join(APP_ROOT, 'config')

app = Flask(__name__, static_url_path='/static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CONFIG_FOLDER'] = CONFIG_FOLDER

conf = ConfigFactory.parse_file(app.config['CONFIG_FOLDER']+'/apikey.conf')

@app.route('/', methods=['GET', 'POST'])
def index(result=None):
    q = multiprocessing.Queue()
    if request.args.get('year', None):
        p1 = multiprocessing.Process(target=crawler, args=(request.args['year'], q))
        # result = crawler(request.args['year'])
        p1.start()
        p1.join()
        result = q.get()
    return render_template('index.html', result=result)

def crawler(year, q):
    fname = str(datetime.now()) + '-MA-(data for '+year+').csv'
    conn = http.client.HTTPSConnection("api.labs.cognitive.microsoft.com")

    payload = "expr=And(Composite(AA.AfN=='gadjah mada university'),Y="+year+")&attributes=Id,C.CId,C.CN,L,Y,Ti,CC,J.JN,J.JId,AA.AuN,AA.AfN,E.DOI&offset=0&count=3000"

    headers = {
        'content-type': "application/x-www-form-urlencoded",
        'ocp-apim-subscription-key': conf.get_string("APIkey.key"),
    }

    conn.request("POST", "/academic/v1.0/evaluate", payload, headers)

    response = conn.getresponse()
    v = json.loads(response.read().decode("utf-8"))
    no = 1

    with open(os.path.join(app.config['UPLOAD_FOLDER'], fname), mode='w') as f:
        z = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        z.writerow(["No", "Id", "Fakultas", "Title", "Author", "Year", "DOI", "Language"])
        for x in v['entities']:
            aa = []
            for xx in x['AA']:
                try:
                    au = xx['AuN'] + " (" + xx['AfN'] + "), "
                except KeyError:
                    au = xx['AuN'] + ", "
                aa.append(au)

            aa1 = str(aa).replace("['", "")
            aa2 = aa1.replace("', '", "")
            aa3 = aa2.replace(" ']", "")

            try:
                z.writerow([
                    no, x['Id'], '', x['Ti'], aa3, x['Y'], x['DOI'], x['L'].replace("@@@", ", ")
                ])
            except KeyError:
                try:
                    z.writerow([
                        no, x['Id'], '', x['Ti'], aa3, x['Y'], None, x['L'].replace("@@@", ", ")
                    ])
                except KeyError:
                    try:
                        z.writerow([
                            no, x['Id'], '', x['Ti'], aa3, x['Y'], x['DOI'], None
                        ])
                    except KeyError:
                        z.writerow([
                            no, x['Id'], '', x['Ti'], aa3, x['Y'], None, None
                        ])
            no += 1
    q.put(fname)
    return fname

if __name__ == '__main__':
    app.run(host='0.0.0.0')

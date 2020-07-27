from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs,SoupStrainer
from urllib.request import urlopen as uReq
import sys
import re
app = Flask(__name__)

@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")

@app.route('/review',methods=['POST','GET']) # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            home_url = 'https://parivahan.gov.in/rcdlstatus/?pur_cd=102'
            post_url = 'https://parivahan.gov.in/rcdlstatus/vahan/rcDlHome.xhtml'
            # Everything before the last four digits: MH02CL
            searchString1 = request.form['content1'].replace(" ", "")
            first = searchString1
            # The last four digits: 0555
            searchString2 = request.form['content2'].replace(" ", "")
            second = searchString2

            r = requests.get(url=home_url)
            cookies = r.cookies
            soup = bs(r.text, 'html.parser')
            viewstate = soup.select('input[name="javax.faces.ViewState"]')[0]['value']

            i = 0
            for match in soup.find_all('button', id=re.compile("form_rcdl")):
                if i == 0:
                    button_id = match.get('id')
                i = 1

            data = {
                'javax.faces.partial.ajax': 'true',
                'javax.faces.source': button_id,
                'javax.faces.partial.execute': '@all',
                'javax.faces.partial.render': 'form_rcdl:pnl_show form_rcdl:pg_show form_rcdl:rcdl_pnl',
                button_id: button_id,
                'form_rcdl': 'form_rcdl',
                'form_rcdl:tf_reg_no1': first,
                'form_rcdl:tf_reg_no2': second,
                'javax.faces.ViewState': viewstate,
            }

            r = requests.post(url=post_url, data=data, cookies=cookies)
            # print (r.text)
            soup = bs(r.text, 'html.parser')
            table = SoupStrainer('tr')
            soup = bs(soup.get_text(), 'html.parser', parse_only=table)
            # print(soup)
            nameList = soup.findAll("td")
            l = []
            for name in nameList:
                l.append(name.text)
            mydict = {l[i]: l[i + 1] for i in range(0, len(l), 2)}

            reviews = []
            reviews.append(mydict)
            return render_template('results.html', reviews=reviews)
        except Exception as e:
            print('The Exception message is: ', e)
            return 'No Details found, Try again!!!'

    # return render_template('results.html')

    else:
        return render_template('index.html')

if __name__ == "__main__":
    #app.run(host='127.0.0.1', port=8001, debug=True)
	app.run(debug=True)
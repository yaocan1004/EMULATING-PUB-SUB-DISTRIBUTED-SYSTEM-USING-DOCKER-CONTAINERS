# -*- coding: utf-8 -*-
from flask import Flask,request,render_template
import os
app = Flask(__name__)

@app.route('/',methods = ['GET','POST'])
def main():
    if request.method == "GET":
        return render_template('python Editor1.html',method = 'GET')
    else:
        code = request.form.get('editor')
        f = open('/Users/canyao/Desktop/CSE586/project2/phase1/11.py','w+')
        f.write(code)
        f.close()
        os.system('cd /Users/canyao/Desktop/CSE586/project2/phase1\ndocker build -t phase1 .')
        result = os.popen('docker run phase1')
        result_String = result.read()
        if result_String == "":
            result_String = "SyntaxError: invalid syntax"
        return render_template('python Editor2.html', code = code, result = result_String, method='POST')



if __name__ == '__main__':
    app.run(debug = True)


import json

from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response, jsonify
import config
from models import User,Studata
from exts import db
from util import Captcha
from fun import validate
from io import BytesIO
from decorator import login_required
from datetime import timedelta


app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)
# db 绑定  app

@app.route('/',methods=['POST','GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        telephone = request.form.get('telephone')
        password = request.form.get('password')
        code =request.form.get('code')
        user = User.query.filter(User.telephone == telephone, User.password == password).first()
        flash('手机号码或密码错误,请重新输入',category='2')
        scode = session.get('code')
        if user and code == scode :
            session['user_id'] = user.id
            # 如果想在31天内都不登录
            session.permanent = True
            return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))

@app.route('/captcha/')
def graph_captcha():
   text, image = Captcha.gen_graph_captcha()
   out = BytesIO()
   image.save(out, 'png')
   out.seek(0)
   text = text.lower()
   resp = make_response(out.read())
   resp.content_type = 'image/png'
   session["code"] = text
   return resp

@app.route('/index/')
@login_required
def index():
    return render_template('index.html')


@app.route('/regist/',methods=['POST','GET'])
def regist():
    if request.method=='GET':
        return render_template('regist.html')
    else:
        username = request.form.get("username")
        telephone = request.form.get("telephone")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        message = validate(telephone, password1, password2)
        flash(message,category='1')

        # user = User.query.filter(User.telephone == telephone).first()
        # if user:
        #     return '该手机号码已被注册'
        # else:
        #     if password1 != password2:
        #         return '两次密码不相等，请核对后填写'
        #     else:
        if '成功' in message:
            user = User(telephone=telephone, username=username, password=password1)
            db.session.add(user)
            db.session.commit()
        else:
            return redirect(url_for('regist'))


@app.route('/showstudent/')
@login_required
def showstudent():
    studata = Studata.query.all()
    return render_template("showstudent.html",stuinfos = studata )


@app.route('/addstudent/',methods=["GET","POST"])
@login_required
def addstudent():
    if request.method=="GET":
        return render_template("addstudent.html")
    else:
        stunumber=request.form.get("txtxuehao")
        stuname=request.form.get("txtxingming")
        grade=request.form.get("txtchengji")
        me = Studata.query.filter(Studata.stunumber == stunumber).first()
        if me:
            flash('该学号已存在,请重新输入学号', category='5')
            return redirect(url_for('addstudent'))
        else:
            studata = Studata(stunumber=stunumber, stuname=stuname, grede=grade)
            db.session.add(studata)
            db.session.commit()
        return redirect(url_for('addstudent'))

@app.route('/deletestudent/',methods=["POST","GET"])
@login_required
def deletestudent():
    if request.method == 'GET':
        return render_template("deletestudent.html")
    else:
        stunumber = request.form.get('txtxuehao')
        me = Studata.query.filter(Studata.stunumber == stunumber).first()
        if me == None:
            flash('该学号不存在,请重新输入学号',category='3')
        else:
            db.session.delete(me)
            db.session.commit()
        return redirect(url_for('deletestudent'))


@app.route('/editstudent/',methods=['POST','GET'])
@login_required
def editstudent():
    if request.method == 'GET':
        return render_template("editstudent.html")
    else:
        stunumber = request.form.get("txtxuehao")
        stuname = request.form.get("txtxingming")
        grade = request.form.get("txtchengji")
        studata = Studata.query.filter(Studata.stunumber == stunumber).first()
        if studata != None:
            studata.stuname = stuname
            studata.grede = grade
            db.session.commit()
        else:
            flash('该学号不存在,请重新输入学号',category='4')

        return redirect(url_for('editstudent'))


@app.route('/search/')
@login_required
def search():
    stunumber = request.args.get('q')
    studata = Studata.query.filter(Studata.stunumber == stunumber).all()
    return render_template('showstudent.html', stuinfos=studata)

@app.route('/loginout')
def loginout():
    del session['user_id']
    return redirect(url_for('login'))

@app.route('/edit/<post_id>',methods=['POST','GET'])
def edit(post_id):
    # print(post_id)
    studata = Studata.query.filter(Studata.id == post_id).first()
    name = studata.stuname
    grade = studata.grede
    number = studata.stunumber
    d = {
        "name":name,
        "grade":grade,
        "number":number
    }
    return jsonify(d)
# jsonify({'name':name,'words':words})#也可以传入key=value形式的参数，如jsonify(name=name,words=words)

@app.route("/delete/<post_id>",methods=['POST','GET'])
def detele(post_id):

    res = {
        "status": 1,
        "message": "success"
    }
    me = Studata.query.filter(Studata.id == post_id).first()
    if  me == None:
        res['status'] = 404
        res["message"] = "Post Not Found"
        return json.dumps(res)
    db.session.delete(me)
    db.session.commit()
    return json.dumps(res)


@app.route("/editstu/",methods=["POST","GET"])
def editstu():
    id = request.form.get('post_id')
    name = request.form.get('name')
    number = int(request.form.get('number'))
    grade = int(request.form.get('grade'))
    res = {
        "status": 1,
        "message": "success"
    }
    # print(id)
    # print(number)
    studata = Studata.query.filter(Studata.id == id).first()
    print(studata)
    studata.stunumber = number
    studata.stuname = name
    studata.grede = grade
    db.session.commit()
    return json.dumps(res)

# context_processor 上下文处理器, 返回的字典可以在全部模板中使用
@app.context_processor
def my_context_processor():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            return {'user':user}
    return {}


if __name__ == '__main__':
    app.run(Debug=True)


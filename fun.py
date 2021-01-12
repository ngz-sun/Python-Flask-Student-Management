from models import User

def validate(telephone, password1, password2=None):
    user = User.query.filter(User.telephone == telephone).first()
    if password2:
        if user:
            return '该用户已经存在'
        else:
            if len(telephone) < 11:
                return '手机号长度至少11个字符'
            elif password1 != password2:
                return '两次密码不一致'
            elif len(password1) < 6:
                return '密码长度至少6个字符'
            else:
                return '注册成功'
    else:
        if user:
            if user.password == password1:
                return '登录成功'
            else:
                return '密码错误'
        else:
            return '用户名不存在'

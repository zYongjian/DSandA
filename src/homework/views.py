from . import forms
from . import models
from django.conf import settings
from django.shortcuts import render, redirect
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse, StreamingHttpResponse
from urllib import parse
import hashlib, datetime, json, os, zipfile, io, xlwt


# Create your views here.


# 主页
def index(request):
    if request.session.get('is_login', None):  # 若session保持登录，跳转至个人页面
        return redirect("/profile/")
    login_form = forms.StudentForm()  # 否则返回登录页面
    return render(request, 'homework/index.html', locals())


# 学生登录
def login(request):
    if request.session.get('is_login', None):  # 若session保持登录，跳转至个人页面
        return redirect("/profile/")
    if request.method == "POST":
        login_form = forms.StudentForm(request.POST)
        message = "请检查填写的内容！"
        if login_form.is_valid():
            student_id = login_form.cleaned_data['student_id']
            password = login_form.cleaned_data['password']
            try:
                student = models.Student.objects.get(student_id=student_id)
                if not student.has_confirmed:  # 邮箱是否验证
                    message = "该用户还未通过邮件确认！"
                    return render(request, 'homework/index.html', locals())
                if student.password == hash_code(password):  # 密码验证
                    request.session['is_login'] = True  # 写入session
                    request.session['student_id'] = student_id
                    request.session['student_name'] = student.name
                    return redirect('/profile/')  # 跳转至个人页面
                else:
                    message = "密码不正确！"
            except:
                message = "用户不存在！"  # 账号错误返回登录页面
                return render(request, 'homework/index.html', locals())
    login_form = forms.StudentForm()  # 如果是GET，返回登录页面
    return render(request, 'homework/index.html', locals())


# 哈希加密密码
def hash_code(s, salt='dsa'):
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())
    return h.hexdigest()


# 生成验证码
def make_confirm_string(student):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code = hash_code(student.name, now)
    try:
        models.ConfirmString.objects.filter(student=student).delete()
    except:
        pass
    confirmString = models.ConfirmString.objects.create(student=student, code=code)
    confirmString.save()
    return code


# 发送邮件
def send_email(email, code):
    subject = '数算作业提交系统注册确认邮件'

    text_content = '''感谢注册，这是注册确认邮件！\
                    如果你看到这条消息，说明你正在纯文本模式浏览，请切换为HTML模式！'''

    html_content = '''
                    <p>感谢注册<a href="http://{}/confirm/?code={}" target=blank>数据结构与算法作业提交系统</a>，\
                    这是注册确认邮件！</p>
                    <p>请点击上方链接完成注册确认！</p>
                    <p>此链接有效期为{}天！</p>
                    '''.format('server address:port', code, settings.CONFIRM_DAYS)

    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


# 学生注册
def register(request):
    if request.session.get('is_login', None):  # 若session保持登录，跳转至个人页面
        return redirect("/profile/")
    if request.method == "POST":
        register_form = forms.RegisterForm(request.POST)
        message = "请检查填写的内容！"
        if register_form.is_valid():
            student_id = register_form.cleaned_data['student_id']
            name = register_form.cleaned_data['name']
            school = register_form.cleaned_data['school']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            if password1 != password2:  # 判断两次密码是否相同
                message = "两次输入的密码不同！"
                return render(request, 'homework/register.html', locals())
            else:
                try:
                    same_id_student = models.Student.objects.get(student_id=student_id)
                    if same_id_student.has_confirmed:
                        message = '用户已存在！'
                        return render(request, 'homework/register.html', locals())
                    else:
                        same_id_student.name = name
                        same_id_student.school = school
                        same_id_student.password = hash_code(password1)
                        same_id_student.save()
                        code = make_confirm_string(same_id_student)  # 生成并保存验证码
                        send_email(str(student_id) + '@pku.edu.cn', code)  # 发送验证邮件
                        message = "注册成功，请进入学号对应邮箱验证后登录！"
                except:
                    new_student = models.Student.objects.create(name=name, school=school, student_id=student_id)
                    new_student.password = hash_code(password1)
                    new_student.save()
                    code = make_confirm_string(new_student)  # 生成并保存验证码
                    send_email(str(student_id) + '@pku.edu.cn', code)  # 发送验证邮件
                        message = "注册成功，请进入学号对应邮箱验证后登录！"
                finally:
                    login_form = forms.StudentForm()
                    return render(request, 'homework/index.html', locals())
    register_form = forms.RegisterForm()  # 如果是GET，返回注册页面
    return render(request, 'homework/register.html', locals())


# 邮箱验证
def confirm(request):
    code = request.GET.get('code', None)
    try:
        confirm = models.ConfirmString.objects.get(code=code)
    except:
        message = '无效的确认请求!'
        return HttpResponse(message)
    c_time = confirm.c_time
    now = datetime.datetime.now()
    if now > c_time + datetime.timedelta(settings.CONFIRM_DAYS):
        confirm.student.delete()
        message = '您的邮件已经过期！请重新注册!'
        return HttpResponse(message)
    else:
        confirm.student.has_confirmed = True
        confirm.student.save()
        confirm.delete()
        message = '感谢确认，请使用账户登录！'
        return HttpResponse(message)


# 学生个人页面
def profile(request):
    if request.session.get('is_login', None):
        student_name = request.session.get("student_name", None)
        student_id = request.session.get("student_id", None)
        try:
            student = models.Student.objects.get(student_id=student_id)
        except:
            request.session.flush()
            return redirect("/index/")
        homeworks = models.Homework.objects.all().order_by("id").values()
        submits = models.Submit.objects.filter(student=student)
        scores = models.Score.objects.filter(student=student)
        for h in homeworks:
            for s in submits:
                if h["id"] == s.homework_id:  # 作业与提交对应
                    h["last_submit"] = s.time
                    h["scored"] = s.scored
                    h["file"] = s.file.name.split('/')[-1]
                    if s.late:
                        h["late"] = True
            for score in scores:
                if score.homework.id == h["id"]:
                    h["score"] = score.score
                    h["comment"] = score.comment
        for h in homeworks:
            if h["cutoff"] < datetime.datetime.now():
                h["late_submit"] = True
        return render(request, 'homework/profile.html', locals())
    return redirect("/index/")  # 若未登录重定向到登录页面


# 学生登出
def logout(request):
    if not request.session.get('is_login', None):  # 若未登录重定向到登录页面
        return redirect("/index/")
    request.session.flush()  # 销毁session
    return redirect("/index/")


# 学生上传作业
def upload(request):
    if request.session.get('is_login', None):
        file = request.FILES.get("file_data", None)  # 获取http传输的文件及附加信息
        homework_id = request.POST.get("homework_id", None)
        student_id = request.session.get("student_id", None)
        if file and student_id and homework_id:
            student = models.Student.objects.get(student_id=student_id)
            homework = models.Homework.objects.get(id=homework_id)
            if student and homework:
                older = models.Submit.objects.filter(student=student, homework=homework)  # 删除已有提交
                if older:
                    assistant = older[0].assistant
                    older.delete()
                    models.Score.objects.filter(student=student, homework=homework).delete()  # 删除已有分数
                    new_submit = models.Submit.objects.create(student=student, homework=homework,
                                                              assistant=assistant, file=file)
                else:
                    assistants = models.Assistant.objects.filter(working=True).order_by('id')
                    homework.iter += 1
                    if homework.iter >= assistants.count():
                        homework.iter = 0
                    homework.save()
                    new_submit = models.Submit.objects.create(student=student, homework=homework,
                                                              assistant=assistants[homework.iter], file=file)
                if datetime.datetime.now() > homework.cutoff:  # 若已过截止时间标记为补交
                    new_submit.late = True
                new_submit.save()
                data = {"success": True}
            else:
                data = {"success": False}
        else:
            data = {"success": False}
    else:
        data = {"success": False}
    return HttpResponse(json.dumps(data))


# 文件迭代器
def file_iterator(file_name, chunk_size=512):
    with open(file_name, 'rb') as f:
        while True:
            c = f.read(chunk_size)
            if c:
                yield c
            else:
                break


# 学生下载已提交作业
def download(request):
    if request.session.get('is_login', None):
        student_id = request.session.get("student_id", None)
        homework_id = request.GET.get("homework_id", None)
        homework = models.Homework.objects.get(id=homework_id)
        student = models.Student.objects.get(student_id=student_id)
        the_file_name = models.Submit.objects.get(homework=homework, student=student).file.name
        response = StreamingHttpResponse(file_iterator(the_file_name))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename=' + parse.quote(the_file_name.split('/')[-1])
        return response


# 助教登录
def a_login(request):
    if request.session.get('a_login', None):  # 若已登录，重定向至个人页面
        return redirect("/at-y/")
    if request.method == "POST":
        login_form = forms.AssistantForm(request.POST)
        message = "请检查填写的内容！"
        if login_form.is_valid():
            student_id = login_form.cleaned_data['student_id']
            password = login_form.cleaned_data['password']
            try:
                assistant = models.Assistant.objects.get(student_id=student_id)
                if assistant.password == hash_code(password):
                    request.session['a_login'] = True
                    request.session['student_id'] = student_id
                    request.session['student_name'] = assistant.name
                    return redirect('/at-y/')
                else:
                    message = "密码不正确！"
            except:
                message = "用户不存在！"
                return render(request, 'homework/aindex.html', locals())
    login_form = forms.AssistantForm()
    return render(request, 'homework/aindex.html', locals())


# 助教登出
def a_logout(request):
    if not request.session.get('a_login', None):
        return redirect("/at-x/")
    request.session.flush()
    return redirect("/at-x/")


# 助教注册
def a_register(request):
    if request.session.get('a_login', None):
        return redirect("/at-y/")
    if request.method == "POST":
        register_form = forms.AssistantRegisterForm(request.POST)
        message = "请检查填写的内容！"
        if register_form.is_valid():
            student_id = register_form.cleaned_data['student_id']
            name = register_form.cleaned_data['name']
            secretCode = register_form.cleaned_data['secretCode']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            if secretCode != "暗号":  # 验证暗号
                message = "有空猜这个孩子都能打酱油了"
                return render(request, 'homework/aregister.html', locals())
            if password1 != password2:  # 判断两次密码是否相同
                message = "两次输入的密码不同！"
                return render(request, 'homework/aregister.html', locals())
            else:
                same_id_assistant = models.Assistant.objects.filter(student_id=student_id)
                if same_id_assistant:  # 判断学号是否已注册
                    message = '用户已存在！'
                    return render(request, 'homework/aregister.html', locals())
                new_assistant = models.Assistant.objects.create()
                new_assistant.student_id = student_id
                new_assistant.name = name
                new_assistant.password = hash_code(password1)
                new_assistant.save()
                message = "注册成功，请登录！"
                login_form = forms.AssistantForm()
                return render(request, 'homework/aindex.html', locals())  # 返回助教登录页面
    register_form = forms.AssistantRegisterForm()  # 若未GET，返回助教注册页面
    return render(request, 'homework/aregister.html', locals())


# 助教个人页面
def a_profile(request):
    if request.session.get('a_login', None):
        student_name = request.session.get("student_name", None)
        student_id = request.session.get("student_id", None)
        Assistant = models.Assistant.objects.get(student_id=student_id)
        homeworks = models.Homework.objects.all().order_by("id")
        homeworklist = homeworks.values()
        for h in homeworklist:
            h["mine"] = models.Submit.objects.filter(assistant=Assistant, homework=h["id"]).count()  # 分配给助教的作业数
            h["to_score"] = models.Submit.objects.filter(assistant=Assistant, scored=False,
                                                         homework=h["id"]).count()  # 分配给助教待批的改作业数
            h["all"] = models.Submit.objects.filter(homework=h["id"]).count()  # 全部作业数
            h["all_to_score"] = models.Submit.objects.filter(homework=h["id"], scored=False).count()  # 全部待批改的作业数
            if h["cutoff"] < datetime.datetime.now():
                h["late"] = True
            now = datetime.datetime.now()
        assistantlist = models.Assistant.objects.filter(working=True).values()
        for a in assistantlist:
            assistant = models.Assistant.objects.get(id=a["id"])
            a["work"] = []
            for h in homeworks:
                all = models.Submit.objects.filter(assistant=assistant, homework=h).count()  # 分配给助教的作业数
                toscore = models.Submit.objects.filter(assistant=assistant, scored=True,
                                                       homework=h).count()  # 分配给助教待批的改作业数
                a["work"].append({"all": all, "toscore": toscore, "homework_id": h.id})
        return render(request, 'homework/aprofile.html', locals())
    return redirect("/at-x/")


# 作业批量显示页面
def a_homeworks(request):
    if request.session.get('a_login', None):
        student_id = request.GET.get("student_id", None)
        if not student_id:
            student_id = request.session.get("student_id", None)
        all = json.loads(request.GET.get("all", None))
        to_score = json.loads(request.GET.get("to_score", None))
        homework_id = request.GET.get("homework_id", None)
        homework = models.Homework.objects.get(id=homework_id)
        # 根据参数决定显示哪些提交
        if not all and not to_score:
            assistant = models.Assistant.objects.get(student_id=student_id)
            submits = models.Submit.objects.filter(homework=homework, assistant=assistant).order_by(
                "student__student_id").values()
        if not all and to_score:
            assistant = models.Assistant.objects.get(student_id=student_id)
            submits = models.Submit.objects.filter(homework=homework, scored=False, assistant=assistant).order_by(
                "student__student_id").values()
        if all and not to_score:
            submits = models.Submit.objects.filter(homework=homework).order_by("student__student_id").values()
        if all and to_score:
            submits = models.Submit.objects.filter(homework=homework, scored=False).order_by(
                "student__student_id").values()
        for s in submits:
            assistant = models.Assistant.objects.get(id=s["assistant_id"])
            student = models.Student.objects.get(id=s["student_id"])
            try:
                score = models.Score.objects.get(student=student, homework=homework)
                s["score"] = score.score
            except:
                pass
            s["assistant_name"] = assistant.name
            s["student_name"] = student.name
            s["student_id"] = student.student_id
            s["student_school"] = student.school
        all = json.dumps(all)
        to_score = json.dumps(to_score)
        return render(request, 'homework/ahomeworks.html', locals())


# 作业评分
def a_score(request):
    message = {"success": False}
    if request.session.get('a_login', None):
        student_id = request.session.get("student_id", None)
        submit_id = request.POST.get("submit_id", None)
        score = int(request.POST.get("score", None))
        comment = request.POST.get("comment", None)
        if submit_id and score != None:
            try:  # 防止评分时上传新版本
                submit = models.Submit.objects.get(id=submit_id)
            except:
                message["message"] = "学生提交了新版本，请重新查看"
                return HttpResponse(json.dumps(message), content_type='application/json')
            try:
                models.Score.objects.get(student=submit.student, homework=submit.homework).delete()
            except:
                new_score = models.Score.objects.create(student=submit.student, homework=submit.homework,
                                                        score=score)
                new_score.save()
            if comment != "":
                submit.comment = comment
            submit.scored = True
            assistant = models.Assistant.objects.get(student_id=student_id)
            submit.assistant = assistant
            submit.save()
            message = {"success": True, "score": str(score), "assistant": assistant.name}
    return HttpResponse(json.dumps(message), content_type='application/json')


# 查看所有学生
def a_students(request):
    if request.session.get('a_login', None):
        students = models.Student.objects.all().order_by("student_id")
        studentlist = students.values()
        homeworks = models.Homework.objects.all().order_by("id")
        homeworklist = homeworks.values()
        scorelist = []
        for s in students:
            scores = []
            for h in homeworks:
                try:
                    score = models.Score.objects.get(student=s, homework=h)
                    scores.append(str(score.score))
                except:
                    scores.append('-')
            scorelist.append(scores)
        i = 0
        for s in studentlist:
            s["scores"] = scorelist[i]
            i = i + 1
        return render(request, 'homework/astudents.html', locals())


# 查看单个学生作业信息
def a_student(request):
    if request.session.get('a_login', None):
        student_id = request.GET.get("student_id", None)
        student = models.Student.objects.get(student_id=student_id)
        submits = models.Submit.objects.filter(student=student)
        homeworks = models.Homework.objects.all().order_by("id").values()
        scores = models.Score.objects.filter(student=student)
        for h in homeworks:
            for s in submits:
                if s.homework.id == h["id"]:
                    h["submit"] = True
                    h["submit_time"] = s.time
                    h["scored"] = s.scored
                    h["submit_id"] = s.id
                    h["late"] = s.late
                    h["student_id"] = s.student_id
                    h["file"] = s.file.name.split('/')[-1]
                    h["assistant_name"] = s.assistant.name
            for s in scores:
                if s.homework.id == h["id"]:
                    h["score"] = s.score
        return render(request, 'homework/astudent.html', locals())


# 助教下载学生作业
def a_download(request):
    if request.session.get('a_login', None):
        student_id = request.GET.get("student_id", None)
        homework_id = request.GET.get("homework_id", None)
        homework = models.Homework.objects.get(id=homework_id)
        student = models.Student.objects.get(student_id=student_id)
        the_file_name = models.Submit.objects.get(homework=homework, student=student).file.name
        response = StreamingHttpResponse(file_iterator(the_file_name))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename=' + parse.quote(the_file_name.split('/')[-1])
        return response


# 助教批量下载学生作业
def a_zip(request):
    if request.session.get('a_login', None):
        student_id = request.session.get("student_id", None)
        all = json.loads(request.GET.get("all", None))
        to_score = json.loads(request.GET.get("to_score", None))
        homework_id = request.GET.get("homework_id", None)
        homework = models.Homework.objects.get(id=homework_id)
        if not all and not to_score:
            assistant = models.Assistant.objects.get(student_id=student_id)
            submits = models.Submit.objects.filter(homework=homework, assistant=assistant)
        if not all and to_score:
            assistant = models.Assistant.objects.get(student_id=student_id)
            submits = models.Submit.objects.filter(homework=homework, scored=False, assistant=assistant)
        if all and not to_score:
            submits = models.Submit.objects.filter(homework=homework)
        if all and to_score:
            submits = models.Submit.objects.filter(homework=homework, scored=False)
        the_file_names = [s.file.name for s in submits]
        now = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        z_name = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                              homework.name + "_" + now + ".zip")
        z_file = zipfile.ZipFile(z_name, 'w')
        for f in the_file_names:
            z_file.write(f, f.split('/')[-1])
        z_file.close()
        z_file = open(z_name, 'rb')
        data = z_file.read()
        z_file.close()
        os.remove(z_file.name)
        response = HttpResponse(data, content_type='application/zip')
        response['Content-Disposition'] = 'attachment;filename=' + parse.quote(z_name.split('/')[-1])
        return response


def get_excel_stream(file):
    # StringIO操作的只能是str，如果要操作二进制数据，就需要使用BytesIO。
    excel_stream = io.BytesIO()
    # 这点很重要，传给save函数的不是保存文件名，而是一个BytesIO流（在内存中读写）
    file.save(excel_stream)
    # getvalue方法用于获得写入后的byte将结果返回给re
    res = excel_stream.getvalue()
    excel_stream.close()
    return res


# 下载所有学生名单及作业成绩excel表单
def get_excel(request):
    students = models.Student.objects.all().order_by("student_id")
    homeworks = models.Homework.objects.all().order_by("id")
    lines = []
    for s in students:
        line = []
        line.append(s.student_id)
        line.append(s.name)
        line.append(s.school)
        for h in homeworks:
            try:
                score = models.Score.objects.get(student=s, homework=h)
                line.append(str(score.score))
            except:
                line.append('-')
        lines.append(line)
    file = xlwt.Workbook()
    table = file.add_sheet("this", cell_overwrite_ok=True)
    title = ['学号', '姓名', '学院'] + [h.name for h in homeworks]
    for col, t in enumerate(title):
        table.write(0, col, t)
    for row, line in enumerate(lines):
        for col, item in enumerate(line):
            table.write(row + 1, col, item)
    now = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    file_name = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), now + ".xls")
    file.save(file_name)
    res = get_excel_stream(file)
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename=' + parse.quote(file_name.split('/')[-1])
    # 将文件流写入到response返回
    response.write(res)
    os.remove(file_name)
    return response

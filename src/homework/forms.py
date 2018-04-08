from django import forms


class StudentForm(forms.Form):
    student_id = forms.CharField(label="学号", max_length=10, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="密码", max_length=256, widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class RegisterForm(forms.Form):
    student_id = forms.CharField(label="学号", max_length=10, widget=forms.TextInput(attrs={'class': 'form-control'}))
    name = forms.CharField(label="姓名", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    school = forms.ChoiceField(label="学院",
                               choices=[('地球与空间科学学院', '地球与空间科学学院'), ('数学科学学院', '数学科学学院'), ('物理学院', '物理学院'),
                                        ('化学与分子工程学院', '化学与分子工程学院'), ('生命科学学院', '生命科学学院'), ('心理学系', '心理学系'),
                                        ('软件与微电子学院', '软件与微电子学院'), ('新闻与传播学院', '新闻与传播学院'), ('中国语言文学系', '中国语言文学系'),
                                        ('历史学系', '历史学系'), ('考古文博学院', '考古文博学院'), ('哲学系', '哲学系'), ('国际关系学院', '国际关系学院'),
                                        ('经济学院', '经济学院'), ('光华管理学院', '光华管理学院'), ('法学院', '法学院'), ('信息管理系', '信息管理系'),
                                        ('社会学系', '社会学系'), ('政府管理学院', '政府管理学院'), ('英语语言文学系', '英语语言文学系'),
                                        ('外国语学院', '外国语学院'), ('艺术学院', '艺术学院'), ('元培学院', '元培学院'),
                                        ('信息科学技术学院', '信息科学技术学院'), ('国家发展研究院', '国家发展研究院'), ('教育学院', '教育学院'),
                                        ('工学院', '工学院'), ('城市与环境学院', '城市与环境学院'), ('环境科学与工程学院', '环境科学与工程学院'),
                                        ('医学部', '医学部')],
                               widget=forms.Select(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label="密码", max_length=256, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label="确认密码", max_length=256,
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class AssistantForm(forms.Form):
    student_id = forms.CharField(label="学号", max_length=10, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="密码", max_length=256,
                               widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class AssistantRegisterForm(forms.Form):
    student_id = forms.CharField(label="学号", max_length=10, widget=forms.TextInput(attrs={'class': 'form-control'}))
    name = forms.CharField(label="姓名", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    secretCode = forms.CharField(label="暗号", max_length=128,
                                 widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label="密码", max_length=256,
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label="确认密码", max_length=256,
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))

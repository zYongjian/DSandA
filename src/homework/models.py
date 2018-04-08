import os
from django.db import models
from django.conf import settings
from django.dispatch import receiver


# 定义文件存储路径
def upload_to(instance, filename):
    return '/'.join([settings.MEDIA_ROOT, instance.homework.name,
                     instance.homework.name + "_" + instance.student.student_id + "_" + instance.student.name + "." +
                     filename.split('.')[-1]])


# 学生
class Student(models.Model):
    student_id = models.CharField(max_length=10, null=False, blank=False, verbose_name="学号")  # 学号
    school = models.CharField(max_length=128, null=False, blank=False, verbose_name="学院")  # 学院
    name = models.CharField(max_length=128, null=False, blank=False, verbose_name="姓名")  # 姓名
    password = models.CharField(max_length=256, null=False, blank=False, verbose_name="密码")  # 密码
    time = models.DateTimeField(auto_now=True, verbose_name="注册时间")  # 注册时间
    has_confirmed = models.BooleanField(default=False, verbose_name="已验证")  # 是否已邮箱验证

    class Meta:
        ordering = ["student_id"]
        verbose_name = "学生"
        verbose_name_plural = "学生"

    def __str__(self):
        return self.name


# 验证码
class ConfirmString(models.Model):
    code = models.CharField(max_length=256)  # 验证码字符串
    student = models.OneToOneField(Student, on_delete=models.CASCADE)  # 一对一关联学生，级联删除
    c_time = models.DateTimeField(auto_now_add=True)  # 生成时间


# 作业
class Homework(models.Model):
    name = models.CharField(max_length=128, null=False, blank=False, verbose_name="作业名")  # 名称
    cutoff = models.DateTimeField(verbose_name="截止日期")  # 截止日期
    can_submit = models.BooleanField(default=True, verbose_name="允许提交")  # 是否允许提交
    iter = models.PositiveSmallIntegerField(null=False, blank=False, default=0, verbose_name="作业分配迭代器")  # 用于迭代分配助教

    class Meta:
        verbose_name = "作业"
        verbose_name_plural = "作业"

    def __str__(self):
        return self.name


# 助教
class Assistant(models.Model):
    student_id = models.CharField(max_length=10, null=False, blank=False, verbose_name="学号")  # 学号
    name = models.CharField(max_length=128, null=False, blank=False, verbose_name="姓名")  # 姓名
    password = models.CharField(max_length=256, null=False, blank=False, verbose_name="密码")  # 密码
    working = models.BooleanField(default=True, verbose_name="为其分配作业")  # 是否分配作业

    class Meta:
        verbose_name = "助教"
        verbose_name_plural = "助教"

    def __str__(self):
        return self.name


# 评分
class Score(models.Model):
    score = models.PositiveSmallIntegerField(null=False, blank=False, default=0, verbose_name="分数")  # 分数
    comment = models.TextField(max_length=512, default="", verbose_name="反馈")  # 反馈
    student = models.ForeignKey(Student, on_delete=models.CASCADE, default="", verbose_name="学生")  # 关联学生，级联删除
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE, default="", verbose_name="作业")  # 关联作业，级联删除

    class Meta:
        verbose_name = "评分"
        verbose_name_plural = "评分"


# 作业提交
class Submit(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, default="", verbose_name="学生")  # 关联学生，级联删除
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE, default="", verbose_name="作业")  # 关联作业，级联删除
    assistant = models.ForeignKey(Assistant, on_delete=models.CASCADE, default="", verbose_name="批改人")  # 分配助教，级联删除
    file = models.FileField(upload_to=upload_to, verbose_name="文件")  # 上传文件
    scored = models.BooleanField(default=False, verbose_name="已评分")  # 是否已评分
    late = models.BooleanField(default=False, verbose_name="补交")  # 是否为补交
    time = models.DateTimeField(auto_now=True, verbose_name="提交时间")  # 提交时间

    class Meta:
        verbose_name = "作业提交"
        verbose_name_plural = "作业提交"


# 文件随提交记录级联删除
@receiver(models.signals.post_delete, sender=Submit)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)

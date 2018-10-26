# 保存发送短信的异步任务
from ManyBeautifulMall.utils.ytx_sdk.sendSMS import CCP
from celery_tasks.main import app


# # 装饰器用于在视图之中调用此函数
@app.task(name='send_sms_code')
def send_sms_code(mobile, code, expires, template_id):
    # CCP.sendTemplateSMS(mobile,code,expires,template_id)
    print(code)

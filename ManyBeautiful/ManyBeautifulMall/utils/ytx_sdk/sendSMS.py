from .CCPRestSDK import REST


class CCP:
    @classmethod
    def sendTemplateSMS(self, mobile, code, expires, template_id):
        # 主帐号
        accountSid = '8aaf070866196530016622cb0e3f0667'

        # 主帐号Token
        accountToken = '78a6a8c06d9a432bba5d3b6177ad017f'

        # 应用Id
        appId = '8aaf070866196530016622cb0ea2066e'

        # 请求地址，格式如下，不需要写http://
        serverIP = 'app.cloopen.com'

        # 请求端口
        serverPort = '8883'

        # REST版本号
        softVersion = '2013-12-26'

        # 发送模板短信
        # @param to 手机号码
        # @param datas 内容数据 格式为列表 例如：[验证码，以分为单位的有效时间]
        # @param $tempId 模板Id

        # 初始化REST SDK
        rest = REST(serverIP, serverPort, softVersion)
        rest.setAccount(accountSid, accountToken)
        rest.setAppId(appId)

        result = rest.sendTemplateSMS(mobile, [str(code),str(expires)], template_id)
        return result.get('statusCode')

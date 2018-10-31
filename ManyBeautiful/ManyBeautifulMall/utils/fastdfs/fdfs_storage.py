# 实现使用FastDFS存储文件
from django.conf import settings
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from fdfs_client.client import Fdfs_client


@deconstructible
class FastDFSStorage(Storage):
    """FastDFS存储文件的存储类"""

    def __init__(self, base_url=None, client_conf=None):
        """
        类的初始化
        :param base_url: 服务器域名
        :param client_conf: FastDFS客户端配置文件路径
        """
        if base_url is None:
            base_url = settings.FDFS_URL
        self.base_url = base_url
        if client_conf is None:
            client_conf = settings.FDFS_CLIENT_CONF
        self.client_conf = client_conf

    def _open(self, name, mode='rb'):  # 必有
        """打开文件,此处用不到"""
        pass

    def _save(self, name, content):  # 必有
        """
        保存文件
        :param name: 传入文件的文件名
        :param content: 传入文件的文件内容
        :return: FastDFS返回的文件名
        """
        # 创建Fdfs_client对象,指明配置文件
        client = Fdfs_client(self.client_conf)
        # 以bytes读取上传的文件内容
        ret = client.upload_by_buffer(content.read())

        if ret.get('Status') != "Upload successed.":
            raise Exception("upload file failed")

        # 获取FastDFS返回的文件名,并返回
        file_name = ret.get("Remote file_id")
        return file_name

    def url(self, name):
        """
        返回文件的完整访问URL
        :param name: 数据库中保存文文件名
        :return: 完整的url
        """

        return self.base_url + name

    def exists(self, name):
        """
        判断文件是否存在, 解决文件重名问题
        :param name: 文件名
        :return: False
        """

        return False  # False 为告诉django山川的都是新文件


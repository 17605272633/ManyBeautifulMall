from fdfs_client.client import Fdfs_client


if __name__ == '__main__':
    client = Fdfs_client('client.conf')
    ret = client.upload_by_filename('/home/python/Desktop/1.jpg')
    print(ret)

    """
    {
        'Storage IP': '192.168.188.136', 
        'Local file name': 
        '/home/python/Desktop/1.jpg', 
        'Status': 'Upload successed.', 
        'Remote file_id': 'group1/M00/00/02/wKi8iFvapfaAFskWAADt0_dcecw368.jpg', 
        'Uploaded size': '59.00KB', 
        'Group name': 'group1'
    }
    """
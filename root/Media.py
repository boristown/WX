import json
import requests
from requests.packages.urllib3.filepost import encode_multipart_formdata

class Media(object):
  #def __init__(self):
    #register_openers()

  def uplaod(accessToken, filePath, mediaType):
    openFile = open(filePath, "rb")
    param = {'media': openFile.read()}
    postData, content_type = encode_multipart_formdata(param)

    postUrl = "https://api.weixin.qq.com/cgi-bin/media/upload?access_token=%s&type=%s" % (accessToken, mediaType)
    headers = {'Content-Type': content_type}
    files = {'media': open(filePath, "rb")}
    urlResp = requests.post(postUrl, files=files)
    #print(urlResp.text)
    return json.loads(urlResp.text)['media_id']
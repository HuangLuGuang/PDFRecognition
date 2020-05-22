##### 三坐标测量仪PDF识别
linux ImportError: libSM.so.6: cannot open shared object file: No such file or directory
```shell script
Traceback (most recent call last):
File "parse.py", line 5, in <module>
  import cv2
File "/home/ai/venv/tf/lib/python3.6/site-packages/cv2/__init__.py", line 3, in <module>
  from .cv2 import *
ImportError: libSM.so.6: cannot open shared object file: No such file or directory
```
原因是：缺少共享库
用一下命令查看查看缺少的共享库：   

```shell script
yum whatprovides libSM.so.6
```

可以看到缺少的是这个包：libSM-1.2.2-2.el7.i686，接下来可以使用这个命令进行安装：

```shell script
sudo yum install libSM-1.2.2-2.el7.x86_64 --setopt=protected_multilib=false
```
安装tr

安装方法一
git clone https://github.com/myhub/tr.git
cd ./tr
sudo python setup.py install
安装方法二
pip install git+https://github.com/myhub/tr.git@master

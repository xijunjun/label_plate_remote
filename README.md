# label_plate
Easy to label China plate<br>
## 程序功能：这是一个用来标注中国车牌的程序
    标注信息包括【四个点的坐标（顺时针排序），颜色，行数，车牌号】，格式为[x1 y1 x2 y2 x3 y3 x4 y4 color nline plate_string]
    每个车牌占据一行。下面是标注示例：
    114 207 420 223 417 299 110 276 blue s "川D71603"
    373 374 601 366 599 413 375 422 blue s "京AD6A99"
## 运行环境：linux或windows+pyhton2.7     依赖库：cv2,pillow(PIL)
#### 测试过可行的配置：【ubuntu16.04+python2.7+pillow+opencv3.3.0.10及以上版本】【windows7+python2.7+pillow+opencv3.1】
    linux下pip安装opencv，先更新pip， 然后运行sudo pip install opencv-python==3.3.0.10
    (查看opencv候选版本命令sudo pip install opencv-python==)
## 使用步骤：
### 一、配置按键
    程序通过cv2.waitKey()获得按键值，但是经测试某些按键值在不同的电脑或主机或opencv版本上不一样，所以需要通过运行
    mk_keymap.py来配置当前环境的下的按键值，按界面提示操作，配置文件自动保存在key_val.txt，key_val_win.txt(windows)，
    只需配置一次即可。
### 二、修改代码：
    1.修改程序中的local_path为需要标注的文件夹路径
    2.根据屏幕分辨率，修改 MAX_WIDTH和MAX_HEIGHT，分别代表图像窗口最大的宽度和高度(确保图像显示不会超出屏幕)
### 三、标注程序使用步骤：
    1.运行label_plate.py，会弹出图像窗口
    2.找到图像中的车牌，从车牌左上角开始，按顺时针点4个点，如果当前点点错了，可以按backspace删除点，若图像中无车牌，按
      delete键开始标注下一张图像，按ESC可以退出程序。
    3.点完4个点，会弹出一个窗口，用于修正四个点的位置，按space选取不同的点，上下左右键移动点。完成后，按enter进入下一步
    4.需要根据当前标注车牌的信息，通过鼠标点击对话框选择颜色、行数，通过鼠标输入中文，键盘输入英文和数字，backspace可以
      删除输入的字符,完成后，按enter进入下一步
    5.此时有三种情况：
      a.图像中的车牌没标注完，回到第2步，继续标注
      b.图像中的车牌标注完，按enter保存标注结果并开始标注下一张图像，当前文件也会被移动到‘标注完成‘文件夹
      c.不想保存当前图像的标注结果，按delete键开始标注下一张图像
## 注意事项:
    1.在第2步，标4个点时，如果没有选取点，可以按backspace键删除之前已标注的车牌（绿框）
    2.在指明需要标注的文件夹下，已经被正确标注的图像会被移动到‘标注完成‘文件夹，通过delete键不予标注的图像，将被移动到
      ‘不合格’文件夹下。
    3.生成的txt编码方式为utf-8
    4.不可删除同目录的dialog.jpg、simhei.ttf、key_val.txt、key_val_win.txt(windows)文件
    4.在dialog窗口：输入字符最多10个，英文字符自动转为大写，双行车牌将前两个字符提行显示（并不影响标注）
    5.程序只会处理指定目录下后缀为'.png','.jpeg','.jpg','bmp'的图像，不会处理指定目录下子文件夹里的图像
    6.车牌中不含字母O和I，所以输入车牌信息时无法输入字母O和I
    7.你也可以用此程序来只标注4个点，将only4points改为1即可，标注信息只包括目标的四个点

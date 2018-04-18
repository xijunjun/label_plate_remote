#coding:utf-8
# --------------------------------------------------------
# KB537_TEXT_GROUP
# 2018-3-26
# --------------------------------------------------------
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
import cv2,time
import os
import numpy as np
import shutil
import platform
import paramiko
import thread,threading


########################################
local_path = 'double_plate'         #远程主机目录
SCREEN_WIDTH=1800                    #本地图像窗口最大宽度
SCREEN_HEIGHT=900                    #本地图像窗口最大高度
only4points=0                       #若只标注四个点则设为1
hostname=''; port=9391; username=''; password=''     #远程主机信息
########################################
local_path +='/'
lock=threading.Lock();lock1=threading.Lock();lock2=threading.Lock()

key_dic={}
global cur_num

def load_key_val():
    lines=open('key_val.txt').readlines()
    for line in lines:
        item=line.split(' ')
        vals=item[1].split(',')
        val_lst=[]
        for val in vals:
            val_lst.append(int(val))
        key_dic[item[0]]=val_lst
        # print item[0],val_lst
load_key_val()

plate_anno,ptlist,platelist,global_var=[],[],[],[]

def file_extension(path):
  return os.path.splitext(path)[1]
def sum_img_vertical(imglist):
    rows=0;cols=0
    for img in imglist:
        rows+=img.shape[0]+10
        if img.shape[1]>cols:
            cols=img.shape[1]
    sumimg = np.zeros((rows, cols, 3), np.uint8)
    ystart = 0
    for img in imglist:
        sumimg[ystart:ystart+img.shape[0],0:img.shape[1]]=img
        ystart=ystart+img.shape[0]+10
    return sumimg
def limit_imgw(img):
    if  img.shape[1]>360:
        img=cv2.resize( img,(360,int(360.0/img.shape[1]*img.shape[0])),interpolation=cv2.INTER_CUBIC )
    if  img.shape[0]>360:
        img=cv2.resize( img,(int(360.0/img.shape[0]*img.shape[1]),360),interpolation=cv2.INTER_CUBIC )
    return  img
def refresh_ori():
    disimg=ori_img.copy()
    for pt in ptlist:
        cv2.circle(disimg, (pt[0], pt[1]),int(4/ global_var[0]), (0, 0, 255), thickness=-1)
    for i in range(0,len(ptlist)):
        if (i+1)%4>=len(ptlist):break
        cv2.line(disimg,tuple(ptlist[i%4]),tuple(ptlist[(i+1)%4]), (0, 0,255),int(2/ global_var[0]))
    for oneplate in platelist:
        for i in range(0,4):
            cv2.line(disimg, tuple(oneplate[i % 4]), tuple(oneplate[(i + 1) % 4]), (0, 255, 0), int(2 / global_var[0]))
    cv2.imshow('img', disimg)
def refresh_preview(tpimg,offpt):
    global goodimg
    disimg=tpimg.copy()
    bdrct = cv2.boundingRect(np.array(ptlist))
    oripts = [[ptlist[0][0]-bdrct[0], ptlist[0][1]-bdrct[1]], [ptlist[1][0]-bdrct[0], ptlist[1][1]-bdrct[1]],
              [ptlist[2][0]-bdrct[0], ptlist[2][1]-bdrct[1]], [ptlist[3][0]-bdrct[0], ptlist[3][1]-bdrct[1]] ]
    rctpts=[[0,0], [bdrct[2]-1,0], [bdrct[2]-1,bdrct[3]-1], [0,bdrct[3]-1]]
    pt_tl=[bdrct[0],bdrct[1]]
    pt_rd=[bdrct[0]+ bdrct[2]-1,bdrct[1]+ bdrct[3]-1]
    goodimg = ori_img[pt_tl[1]:pt_rd[1] + 1, pt_tl[0]:pt_rd[0] + 1].copy()
    M=cv2.getPerspectiveTransform(np.array(oripts,dtype="float32"),np.array(rctpts,dtype="float32"))
    goodimg=cv2.warpPerspective(goodimg,M,(bdrct[2],bdrct[3]))
    disimg=sum_img_vertical([disimg,goodimg])
    #limit_window(disimg, 'preview')
    wm_ratio = get_ratio(disimg)
    cv2.circle(disimg, (ptlist[global_var[1]][0] - offpt[0],ptlist[global_var[1]][1] - offpt[1]), int(6 / wm_ratio), (0, 255, 0), thickness=-1)
    for pt in ptlist:
        cv2.circle(disimg, (pt[0]-offpt[0], pt[1]-offpt[1]),int(4/ wm_ratio), (0, 0, 255), thickness=-1)
    for i in range(0,4):
        cv2.line(disimg,(ptlist[i%4][0]-offpt[0],ptlist[i%4][1]-offpt[1]),(ptlist[(i+1)%4][0]-offpt[0],ptlist[(i+1)%4][1]-offpt[1]),(0, 0,255),int(2/wm_ratio))
    cv2.imshow('preview', disimg)
    limit_window(disimg, 'preview')
    if disimg.shape[0]<150 or disimg.shape[1]<150:
        cv2.resizeWindow('preview', disimg.shape[1]*2, disimg.shape[0]*2)
def get4pts():
    cv2.namedWindow('preview', cv2.WINDOW_FREERATIO)
    cv2.moveWindow('preview',0,0)
    bdrct= cv2.boundingRect(np.array(ptlist))
    delta_w=int(bdrct[2]*0.3)
    delta_h=int(bdrct[3]*0.5)
    pt_tl=[bdrct[0],bdrct[1]]
    pt_rd=[bdrct[0]+ bdrct[2]-1,bdrct[1]+ bdrct[3]-1]
    pt_tl[0]=0 if pt_tl[0]-delta_w<0 else pt_tl[0]-delta_w
    pt_rd[0] =ori_img.shape[1]-1 if  pt_rd[0]+delta_w>ori_img.shape[1]-1 else pt_rd[0]+delta_w
    pt_tl[1] =0 if pt_tl[1]-delta_h<0 else pt_tl[1]-delta_h
    pt_rd[1] = ori_img.shape[0]-1 if pt_rd[1]+delta_h>ori_img.shape[0]-1 else pt_rd[1]+delta_h
    pltimg = ori_img[pt_tl[1]:pt_rd[1]+1, pt_tl[0]:pt_rd[0]+1].copy()
    refresh_preview(pltimg, pt_tl)
    while 1:
        key=cv2.waitKey(0)
        if key in key_dic['ENTER']:
            break
        if key in key_dic['SPACE']:
            global_var[1]=(global_var[1]+1)%4
        if key in key_dic['UP']:
            if ptlist[global_var[1]][1]-pt_tl[1]-global_var[2]>=0:
                ptlist[global_var[1]][1] -=global_var[2]
        if key in key_dic['DOWN']:
            if ptlist[global_var[1]][1]-pt_tl[1]+global_var[2]<=pltimg.shape[0]-1:
                ptlist[global_var[1]][1]  +=global_var[2]
        if key in key_dic['LEFT']:
            if ptlist[global_var[1]][0]-pt_tl[0]-global_var[2]>=0:
                ptlist[global_var[1]][0]  -=global_var[2]
        if key in key_dic['RIGHT']:
            if ptlist[global_var[1]][0]-pt_tl[0]+global_var[2]<=pltimg.shape[1]-1:
                ptlist[global_var[1]][0]  +=global_var[2]
        if key in key_dic['ESC']:
            del ptlist[:]
            cv2.destroyWindow('preview')
            return
        refresh_preview(pltimg, pt_tl)
        # refresh_ori()
    # print ptlist
    platelist.append(list(ptlist))#list.append([])只拷贝索引,不拷贝对象
    refresh_ori()
    cv2.destroyWindow('preview')
def draw_circle(event,x,y,flags,param):
    if len(ptlist) == 4:
        return
    if event == cv2.EVENT_LBUTTONDOWN:
        ptlist.append([x,y])
        refresh_ori()
        if len(ptlist)==4:
            get4pts()
            get_info()
            refresh_ori()
            cv2.waitKey(1)#注意此处等待按键

def limit_window(disimg,winnane):
    wm_ratio=1.0
    if disimg.shape[1] > SCREEN_WIDTH or disimg.shape[0] > SCREEN_HEIGHT:
        if (disimg.shape[1] / float(disimg.shape[0])) > (SCREEN_WIDTH / float(SCREEN_HEIGHT)):
            cv2.resizeWindow(winnane, SCREEN_WIDTH, int(SCREEN_WIDTH / float(disimg.shape[1]) * disimg.shape[0]))
            wm_ratio = SCREEN_WIDTH / float(disimg.shape[1])
        else:
            cv2.resizeWindow(winnane, int(SCREEN_HEIGHT / float(disimg.shape[0]) * disimg.shape[1]), SCREEN_HEIGHT)
            wm_ratio = SCREEN_HEIGHT / float(disimg.shape[0])
    else:
        cv2.resizeWindow(winnane, disimg.shape[1], disimg.shape[0])
    return wm_ratio
def get_ratio(disimg):
    wm_ratio=1.0
    if disimg.shape[1] > SCREEN_WIDTH or disimg.shape[0] > SCREEN_HEIGHT:
        if (disimg.shape[1] / float(disimg.shape[0])) > (SCREEN_WIDTH / float(SCREEN_HEIGHT)):
            wm_ratio = SCREEN_WIDTH / float(disimg.shape[1])
        else:
            wm_ratio = SCREEN_HEIGHT / float(disimg.shape[0])
    return wm_ratio

def select_info(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN:
        idx,idy=xy2id(x, y)
        global_var[3]=get_dic_key_by_val(color_dic,list((idx,idy)),global_var[3])
        global_var[4] = get_dic_key_by_val(hangshu_dic, list((idx, idy)), global_var[4])
        if list((idx, idy))  in chi_dic.values():
            global_var[5] = get_dic_key_by_val(chi_dic, list((idx, idy)), global_var[5])
            if len(platestr) < 10:
                 platestr.append(global_var[5])
        refresh_dialog(newdialogimg)
def xy2id(x,y):
    return x/30,y/40
def dis_index_rec(srcimg,xy):
    x,y=xy[0],xy[1]
    cv2.rectangle(srcimg, (30 *x, 40 * y),(30 * (x+1), 40 * (y+1)), (0, 0, 255), 1)
def refresh_dialog(tpimg):
    disimg=tpimg.copy()
    dis_index_rec(disimg,color_dic[global_var[3]])
    dis_index_rec(disimg, hangshu_dic[global_var[4]])
    dis_index_rec(disimg, chi_dic[global_var[5]])
    dis_platestr(disimg)
    cv2.imshow('dialog', disimg)
    cv2.moveWindow('dialog', 0, 0)
def gen_char(f,val,color):
    bkcolor,charcolor=color[0],color[1]
    img=Image.new("RGB", (30,40),bkcolor)
    draw = ImageDraw.Draw(img)
    draw.text((0, 6),val,charcolor,font=f)
    A = np.array(img)
    return A
def paste_img(src,x,y,val,color):
    img=gen_char(gfont, val,color)
    src[y:y+40,x:x+30,:]=img.copy()
def dis_platestr(img):
    if global_var[4]=='s':
        for i,pchar in enumerate(platestr):
            paste_img(img, (1+i)*30, 9*40, pchar, color=plate_color_dic[global_var[3]])
    else :
        for i,pchar in enumerate(platestr):
            if i<2:paste_img(img, (2+i)*30, 8*40, pchar, color=plate_color_dic[global_var[3]])
            else :paste_img(img, (1+i-2)*30, 9*40, pchar, color=plate_color_dic[global_var[3]])
def get_info():
    global newdialogimg
    if len(ptlist)==0:
        return
    if only4points==1:
        plate_anno.append('')
        del platestr[:]
        del ptlist[:]#重新初始化参数
        global_var[1] = 0
        return
    newdialogimg=sum_img_vertical([dialogimg,limit_imgw(goodimg)])
    paste_img(newdialogimg, 8 * 30, 9 * 40, '|', color=[(255,255,255),(50,50,50)])
    refresh_dialog(newdialogimg)
    cv2.setMouseCallback('dialog', select_info)
    # cv2.imshow('goodimg',goodimg)
    while 1:
        key=cv2.waitKey(0)
        if key in key_dic['ENTER']:
            anno_str=global_var[3]+' '+global_var[4]+' "'
            for pchar in platestr:
                anno_str+=pchar
            anno_str += '"'
            plate_anno.append(anno_str)
            del platestr[:]
            print anno_str
            # global_var[3] = 'blu'
            break
        if key in key_dic['BACK']:
            if len(platestr)>0:
                platestr.pop()
        if ((key>=ord('0') and key<=ord('9')) or (key>=ord('a') and key<=ord('z')) or (key>=ord('A') and key<=ord('Z'))) and chr(key).upper() in engnumtable:
            if len(platestr) < 10:
                platestr.append(chr(key).upper())
        refresh_dialog(newdialogimg)
    cv2.destroyWindow('dialog')
    del ptlist[:]#重新初始化参数
    global_var[1] = 0
def get_dic_key_by_val(src_dic,dstval,rtval):
    if dstval not in src_dic.values():return rtval
    for key, value in src_dic.items():
        if value==dstval:
            return  key
def encode_thr_sys(tstr):
    return tstr.encode('gbk') if 'Windows' in platform.system() else tstr.encode('utf-8')
##########################################################
def ssh_make_dir(ssher,path):
    command='if [ ! -d '+path+' ] ;then\n mkdir '+path+'\nfi'
    ssher.exec_command(command)

def ssh_listdir(ssher,path):
    stdin, stdout, stderr = ssher.exec_command('ls '+path)
    res,err = stdout.read(),stderr.read()
    result = res if res else err
    imglst=[]
    for item in result.split('\n'):
        if  file_extension(item) in ['.JPG','.bmp','.PNG','.png','.jpeg','.jpg']:
            imglst.append(item)
    return imglst
def sftp_imread(sftp,path):
    sftp.get(path, 'cache'+file_extension(path))
    img=cv2.imread('cache'+file_extension(path))
    return img
def mov_A2B(ssher,A,B):
    ssher.exec_command('mv '+A+' '+B)
def save_ano(sftp,rootpath,imgname,lines):
    txtname='.cache/'+os.path.splitext(imgname)[0]+'.txt'
    with open(txtname, 'w') as f:
        f.write((lines.rstrip(' \n')).encode('utf-8'))
    sftp.put(txtname, rootpath+'标注完成/'+os.path.splitext(imgname)[0]+'.txt')
def make_dir(local_path):
    if os.path.isdir(local_path + '.cache'):
        shutil.rmtree('.cache')
    os.mkdir('.cache')
    if os.path.isdir(local_path + '标注完成') is False:
        os.mkdir(local_path + '标注完成')
def sftp2cache(sftp,local_path,cache_size):
    global cur_num
    for i_img in imgpathlist:
        sftp.get(local_path+i_img, '.cache/'+i_img)
        produce(cache_size)

def produce(csize):
        global cur_num
        lock.acquire()
        cur_num+=1
        if cur_num==1:
            lock1.release()
        lock.release()
        if cur_num>=csize:
            lock2.acquire()
def consume(csize):
        global cur_num
        if cur_num<1:
            lock1.acquire()
        lock.acquire()
        cur_num-=1
        if cur_num==csize-1:
            lock2.release()
        lock.release()
def get_new_name(path,filen):
    all_dir=os.listdir(path)
    newname=filen
    while 1:
        if newname not in all_dir:
            break
        else :
            fileitem=os.path.splitext(newname)
            newname=fileitem[0]+'+'+fileitem[1]
    return newname

if __name__ == '__main__':
    global cur_num
    cur_num=0
    stopflag=0
    platestr=[]
    global_var.append(1.0)#缩放尺度参数，画线和点的依据
    global_var.append(0)#cursor点选择
    global_var.append(2)#move_step调整点时的步长
    global_var.append('blue')  #
    global_var.append('s')#
    global_var.append(u'京')  #
    gfont = ImageFont.truetype("./simhei.ttf", 30, 0)

    chi_dic={}
    engnumtable='0123456789ABCDEFGHJKLMNPQRSTUVWXYZ'
    chi_table = u'京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼警港澳挂领使学'
    for i,chi in enumerate(chi_table):
        chi_dic[chi]=[i%11,4+i/11]
    color_dic={'blue':[3,0],'yellow':[5,0],'black':[7,0],'white':[9,0],'green':[11,0]}
    hangshu_dic={'s':[3,1],'d':[5,1]}
    plate_color_dic={'blue':[(155,0,0),(255,255,255)],'yellow':[(0,185,255),(0,0,0)],'black':[(0,0,0),(185,185,185)],'white':[(200,200,200),(0,0,0)],'green':[(0,150,0),(255,255,255)]}

##############################################
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())#第一次登录的认证信息
    # 连接服务器
    ssh.connect(hostname, port, username, password)

    ssh_make_dir(ssh,local_path+'标注完成')
    ssh_make_dir(ssh,local_path+'不合格')
    make_dir('')

    transport = paramiko.Transport((hostname, port))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)
########################################

    imgpathlist=ssh_listdir(ssh,local_path)
    cv2.namedWindow('img', cv2.WINDOW_FREERATIO)
    cv2.setMouseCallback('img', draw_circle)

    dialogimg=cv2.imread(('dialog.jpg'))


    lock1.acquire()
    lock2.acquire()
    cachesize=5
    cachesize=cachesize if cachesize<len(imgpathlist) else len(imgpathlist)

    thread.start_new_thread(sftp2cache,(sftp,local_path,cachesize))

    for i_img in imgpathlist:

        print (local_path + i_img)
        consume(cachesize)
        ori_img=cv2.imread('.cache/'+ i_img)

        global_var[0]=limit_window(ori_img, 'img')
        cv2.imshow('img',ori_img )
        cv2.moveWindow('img', 0, 0)
        while 1:
            key=cv2.waitKey(0)
            if key in key_dic['ESC']:
                stopflag=1
                break
            if key in key_dic['BACK']:
                if len(ptlist)>0:
                    ptlist.pop()
                elif len(plate_anno)>0:
                    plate_anno.pop()
                    platelist.pop()
            if key in key_dic['DELETE']:
                mov_A2B(ssh,(local_path + i_img),((local_path+'不合格/')+ i_img))
                os.remove('.cache/'+i_img)
                break
            if key in key_dic['ENTER']:
                if len(platelist)==0:
                    os.remove('.cache/'+i_img)
                    break
                lines=''
                for i,oneplate in enumerate(platelist):
                    lines += str(oneplate[0][0]) + ' ' + str(oneplate[0][1]) + ' ' + str(oneplate[1][0]) + ' ' + str(oneplate[1][1]) + ' ' + str(oneplate[2][0]) + ' ' +\
                             str(oneplate[2][1]) + ' ' + str(oneplate[3][0]) + ' ' + str(oneplate[3][1]) +' '+plate_anno[i]+'\n'
                # shutil.copy('cache'+file_extension(i_img),'标注完成/' + i_img)
                # shutil.move('.cache/'+i_img,'标注完成/' + i_img)
                new_name=get_new_name('标注完成/',i_img)#如果标注完成文件夹中有相同的文件则重命名
                os.rename('.cache/'+i_img,'标注完成/' +new_name )
                save_ano(sftp,local_path,i_img,lines)
                os.rename('.cache/'+os.path.splitext(i_img)[0]+'.txt','标注完成/' + os.path.splitext(new_name)[0]+'.txt')
                mov_A2B(ssh,local_path + i_img, local_path + '标注完成/' + i_img)
                break
            refresh_ori()
        if stopflag:
            break
        ptlist = []
        del platelist[:]
        del plate_anno[:]
        global_var[0]=1.0
        global_var[1] = 0
    ssh.close()
    transport.close()

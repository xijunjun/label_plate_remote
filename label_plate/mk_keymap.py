# -*- coding: utf-8 -*-
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
import cv2
import os
import numpy as np
import shutil
import platform
def gen_char(f,val,bkcolor,charcolor):
    img=Image.new("RGB", (30,40),bkcolor)
    draw = ImageDraw.Draw(img)
    draw.text((0, 6),val,charcolor,font=f)
    A = np.array(img)
    return A

def paste_img(src,x,y,val,bkcolor=(255,255,255),charcolor=(0,0,0)):
    img=gen_char(gfont, val,bkcolor,charcolor)
    # print src.shape
    src[y:y+40,x:x+30,:]=img.copy()
def dis_str(img,x,y,mstr):
    for i,val in enumerate(mstr):
        paste_img(img, x+i*30, y, val)
def dis_num(img,x,y,mstr):
    for i,val in enumerate(mstr):
        paste_img(img, x+i*30, y, val,bkcolor=(255,255,255),charcolor=(0,0,255))
def refresh_img(img,key,keyval):
    mimg=img.copy()
    dis_str(mimg,0,0,key+u'的键值:')
    dis_num(mimg,0,40,str(keyval))
    cv2.imshow('img',mimg )

if __name__ == '__main__':
    key_val_path='key_val.txt'
    if 'Windows' in platform.system():
        print 'Windows'
        key_val_path='key_val_win.txt'
    lines=open(key_val_path)
    gfont = ImageFont.truetype("./simhei.ttf", 30, 0)
    img = 255-np.zeros((150, 400, 3), np.uint8)
    dis_str(img,0,80,u'按S键下一个')
    keys=[]
    key_dic=[]
    for line in lines:
        keys.append(line.split(' ')[0])
        print keys[-1]
    for key in keys:
        cur_val=-1
        refresh_img(img,key,cur_val)
        while 1:
            keyval=cv2.waitKey()
            if  (keyval==ord('S') or keyval==ord('s')) and cur_val!=-1:
                key_dic.append(cur_val)
                break
            cur_val=keyval
            refresh_img(img,key,cur_val)

    keylines=''
    for i,key in enumerate(keys):
        keylines+=key+' '+str(key_dic[i])+'\n'
    with open(key_val_path, 'w') as f:
        f.write((keylines.rstrip('\n')).encode('utf-8'))




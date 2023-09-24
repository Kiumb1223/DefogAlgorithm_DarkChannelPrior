# -*- encoding: utf-8 -*-
'''
@File    :   main.py
@Time    :   2023/09/23 18:59:48
@Author  :   Kiumb 
@Description :  暗通道先验算法复现
'''

import cv2
import numpy as np

def darkChannel(img,r = 7,bt_show = False,bt_save = False):
    '''
    @Description :求取暗通道图
                  np.min实现三通道中的最小值;cv2.erode实现了窗口中的最小值 
    @Parameter   :img为原始图像
    @Parameter   :r  为窗口大小
    @Parameter   :bt_show为暗通道图显示标志位
    @Parameter   :bt_save为暗通道图保存标志位(命名为'DarkChannel.png')
    @Return      :原始图像的暗通道图
    '''
    DarkChann = cv2.erode(np.min(img,2),np.ones((2 * r + 1, 2 * r + 1)))
    if bt_show:
        cv2.imshow('DarkChannel',DarkChann)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    if bt_save:
        cv2.imwrite(r'Result\DarkChannel.png',DarkChann*255)
    return DarkChann


def estimateA(img,darkChann,bt_show = False,bt_save = False):
    '''
    @Description :将按通道中前0.1%亮度的像素定位到原图中,并在这些位置上求取各个通道的均值以作为三通道的全局大气光A   
    @Parameter   :img为原始图像
    @Parameter   :darkChann为暗通道图
    @Parameter   :bt_show为是否在原图上标注这些像素的位置
    @Parameter   :bt_save为是否保存标注像素的图片(命名为'NotatedImg.png')
    @Return      :三通道下的A
    '''
    imgCopy = img.copy() 
    h,w,_  = img.shape
    length = h*w
    num    = max(int(length *0.0001),1)
    DarkChannVec = np.reshape(darkChann,length)  # convert to a row vector
    index  = DarkChannVec.argsort()[length-num:]
    rowIdx = index // w
    colIdx = index %  w
    coords = np.stack((colIdx,rowIdx),axis = 1)

    sumA   = np.zeros((1,3))
    for coord in coords:
        col,row = coord
        sumA    += img[row,col,:]
    A = sumA / num
    if bt_show:
        # img     *= 255    # Python传参为指针而非值
        for coord in coords:
            cv2.circle(imgCopy, coord,3,(255,0,0),3)
        cv2.imshow('NotatedImg',imgCopy)
        cv2.waitKey(0)
        cv2.destroyAllWindows()   
    if bt_save:
        cv2.imwrite(r'Result\NotatedImg.png',imgCopy*255)
    return A 


def estimateT(img,A,omega = 0.95):
    '''
    @Description :按照推导的公式计算传输率图   
    @Parameter   :img为原始图像   
    @Parameter   :A为三通道的全局大气光值   
    @Parameter   :omega为去雾程度   
    @Return      :transmissionMap为投射率图
    '''
    tempMap = np.empty(img.shape,img.dtype)
    tempMap = img / A
    transmissionMap = 1 - omega * darkChannel(tempMap)
    return transmissionMap

def guidedfilter(I, p, r, eps = 0.0001):
    '''
    @Description :导向滤波算法   
    @Parameter   :I为引导图
                  p为输入图像
                  r为窗口大小(经验值 - 暗通道窗口半径的四倍)
                  eps为正则参数  
    @Return      :导向滤波后的图像
    '''
    height, width = I.shape
    m_I = cv2.boxFilter(I, -1, (r, r))
    m_p = cv2.boxFilter(p, -1, (r, r))
    m_Ip = cv2.boxFilter(I * p, -1, (r, r))
    cov_Ip = m_Ip - m_I * m_p

    m_II = cv2.boxFilter(I * I, -1, (r, r))
    var_I = m_II - m_I * m_I

    a = cov_Ip / (var_I + eps)
    b = m_p - a * m_I

    m_a = cv2.boxFilter(a, -1, (r, r))
    m_b = cv2.boxFilter(b, -1, (r, r))
    return m_a * I + m_b


def deHaze(img,r = 7,T_threshold = 0.1,bt_show = False ,bt_save = False):
    '''
    @Description :暗通道去雾   
    @Parameter   :img为原始图像
    @Parameter   :r为暗通道窗口
    @Parameter   :t_threshold为透射率t的阈值
    @Parameter   :bt_show为是否显示去雾图像的标志位
    @Parameter   :bt_save为保存去雾图像的标志位(命名为'DehazeImg.png')
    @Return      :去雾图像
    '''
    imgNormal = img / 255
    darkChann  = darkChannel(imgNormal,r,bt_show=True,bt_save=True)
    A = estimateA(imgNormal,darkChann,bt_show=True,bt_save=True)
    print(f'A - {A}')
    T = estimateT(imgNormal,A)
    imgGray    = np.min(img,2) / 255
    T_refine   = guidedfilter(imgGray,T,81)
    # T_refine   = guidedfilter(darkChann,T,81)
    imgRecover = np.empty(imgNormal.shape,imgNormal.dtype)
    T = cv2.max(T_refine,T_threshold)
    for i in range(3):
        imgRecover[:,:,i] = (imgNormal[:,:,i] - A[0,i]) / T + A[0,i] 
    if bt_show:
        cv2.imshow('DehazeImg',imgRecover)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    if bt_save:
        cv2.imwrite(r'Result\DehazeImg.png',imgRecover*255)
    return imgRecover*255


if __name__ == '__main__':
    img = cv2.imread(r'FoggyImage\2.jpg')
    imgRecover = deHaze(img,bt_show=True,bt_save=True)


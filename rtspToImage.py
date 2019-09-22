# coding:utf-8

import cv2
import dlib
import time
import glob

cnt = 0
def getImgFromCamera(folder_path):
    detector = dlib.get_frontal_face_detector()
    #cap = cv2.VideoCapture("rtsp://192.168.169.30:8554/")#获取网络摄像机
    cap = cv2.VideoCapture(0)#/dev/video0
    print("cap.isOpened:",cap.isOpened())

    #while i<10:
    while(cap.isOpened()):
        if cap.isOpened() == True:
            ret, frame = cap.read()#读一帧
            
            # #探测图片中的人脸
            # gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # dets = detector(gray_img, 1)
            # print("人脸数：", len(dets))
            
            # #绘制矩形框出人脸区域
            # for e, d in enumerate(dets):
                # x1 = d.top() if d.top() > 0 else 0
                # y1 = d.bottom() if d.bottom() > 0 else 0
                # x2 = d.left() if d.left() > 0 else 0
                # y2 = d.right() if d.right() > 0 else 0 
                
                # cv2.rectangle(frame, (x2, x1), (y2, y1), (0, 255, 0), 2)
                
            # 当发现人脸进行操作:显示,保存图片文件,保存为视频,推送rtmp
            cv2.imshow("capture", frame)#显示一帧图像
            cv2.imwrite(folder_path + str(cnt) + '.jpg', frame)# 保存图片文件
                        
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
    cap.release()
    cv2.destroyAllWindows()
 
# 测试
if __name__ == '__main__':
    folder_path = '/home/mj/experiment/golang/src/cameraToRtmp/'
    getImgFromCamera(folder_path)

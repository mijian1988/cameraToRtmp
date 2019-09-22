import cv2
import subprocess

#这种方式容易出现broken pipe，优化详见cameraToRtmp.py

rtsp = "rtsp://192.168.0.10/live/live0"
rtmp = 'rtmp://192.168.0.30:1935/live/movie'

# 读取视频并获取属性
cap = cv2.VideoCapture(rtsp)
size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
sizeStr = str(size[0]) + 'x' + str(size[1])
print(sizeStr)

command = ['ffmpeg',
    '-y', '-an',
    '-f', 'rawvideo',
    '-vcodec','rawvideo',
    '-pix_fmt', 'bgr24',
    '-s', sizeStr,
    '-r', '25',
    '-i', '-',
    '-c:v', 'libx264',
    '-pix_fmt', 'yuv420p',
    '-preset', 'ultrafast',
    '-f', 'flv',
    rtmp]
 
pipe = subprocess.Popen(command
    , shell=False
    , stdin=subprocess.PIPE
)
 
while cap.isOpened():
    success,frame = cap.read()
    if success:
        #'''
		#对frame进行识别处理
		#'''
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break    
        pipe.stdin.write(frame.tostring())
 
cap.release()
pipe.terminate()

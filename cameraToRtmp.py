import queue
import dlib
import threading
import cv2 as cv
import subprocess as sp
from signal import signal, SIGPIPE, SIG_DFL

#/****************************************************************************************************/
# import numpy as np
# import tensorflow as tf
# from object_detection.utils import ops as utils_ops
# from object_detection.utils import label_map_util
# from object_detection.utils import visualization_utils as vis_util
#/****************************************************************************************************/

#降低延迟操作：1.增大fps;2.减小缓存个数CAP_PROP_BUFFERSIZE;3.隔两帧进行人脸探测(failed);4.降低分辨率cv.resize;

# 让python忽略SIGPIPE信号,并且不抛出异常
signal(SIGPIPE,SIG_DFL) 

class Live(object):
    def __init__(self):
        self.frame_queue = queue.Queue()
        self.command = ""
        # 自行设置
        self.rtmpUrl = "rtmp://192.168.0.30:1935/live/movie"
        #self.rtmpUrl = "rtmp://192.168.126.30:1935/live/movie"
        #self.camera_path = 0
        self.camera_path = "rtsp://192.168.0.10/live/live0"
        self.detector = dlib.get_frontal_face_detector()
        
        # List of the strings that is used to add correct label for each box.
        #self.PATH_TO_LABELS = './object_detection/face_label_map.pbtxt'
        #self.PATH_TO_FROZEN_GRAPH = './pb/face_model.pb'
        
    def read_frame(self):
        print("read_frame...")
        cap = cv.VideoCapture(self.camera_path)

        # Get video information ： 30|640|480,fps改大to降低延迟效果
        #fps = int(cap.get(cv.CAP_PROP_FPS))
        fps = int(100)
        width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
        nbuffers=int(cap.set(cv.CAP_PROP_BUFFERSIZE,2))
        print("fps:",fps,"|","width:",width,"|","height","|",height,"|","nbuffers",nbuffers)

        # ffmpeg command
        self.command = ['ffmpeg',
                '-y',
                '-f', 'rawvideo',
                '-vcodec','rawvideo',
                '-pix_fmt', 'bgr24',
                '-s', "{}x{}".format(width, height),
                '-r', str(fps),
                '-i', '-',
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                '-preset', 'ultrafast',
                '-f', 'flv', 
                self.rtmpUrl]
        
        # read webcamera
        while(cap.isOpened()):
            ret, frame = cap.read()
            if not ret:
                print("Opening camera failed")
                break
            
            # resize 320*240
            cv.resize(frame,(320,240),interpolation=cv.INTER_CUBIC)
            
            # put frame into queue
            self.frame_queue.put(frame)

    def push_frame(self):
        print("push_frame...")
        # 防止多线程时command未被设置
        while True:
            if len(self.command) > 0:
                # 管道配置
                p = sp.Popen(self.command, stdin=sp.PIPE)
                break
                
        #/****************************************************************************************************/        
        # # 2.process frame,探测图片中的人脸(zy他们的算法,比dlib(fps:7)慢一半fps:2.4)
        # category_index = label_map_util.create_category_index_from_labelmap(self.PATH_TO_LABELS, use_display_name = True)
        # # 重启网络
        # IMAGE_SIZE = (256, 256)
        # detection_sess = tf.compat.v1.Session()
        # with detection_sess.as_default():
            # od_graph_def = tf.compat.v1.GraphDef()
            # with tf.io.gfile.GFile(self.PATH_TO_FROZEN_GRAPH, 'rb') as fid:
                # serialized_graph = fid.read()
                # od_graph_def.ParseFromString(serialized_graph)
                # tf.import_graph_def(od_graph_def, name='') 
                # ops = tf.compat.v1.get_default_graph().get_operations()
                # all_tensor_names = {output.name for op in ops for output in op.outputs}
                # tensor_dict = {}
                # for key in [
                    # 'num_detections', 'detection_boxes', 'detection_scores',
                    # 'detection_classes', 'detection_masks'
                # ]:
                    # tensor_name = key + ':0'
                    # if tensor_name in all_tensor_names:
                        # tensor_dict[key] = tf.compat.v1.get_default_graph().get_tensor_by_name(tensor_name)
                
                # if 'detection_masks' in tensor_dict:
                    # # The following processing is only for single image
                    # detection_boxes = tf.squeeze(tensor_dict['detection_boxes'], [0])
                    # detection_masks = tf.squeeze(tensor_dict['detection_masks'], [0])
                    # # Reframe is required to translate mask from box coordinates to image coordinates and fit the image size.
                    # real_num_detection = tf.cast(tensor_dict['num_detections'][0], tf.int32)
                    # detection_boxes = tf.slice(detection_boxes, [0, 0], [real_num_detection, -1])
                    # detection_masks = tf.slice(detection_masks, [0, 0, 0], [real_num_detection, -1, -1])
                    # detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
                        # detection_masks, detection_boxes, IMAGE_SIZE[0], IMAGE_SIZE[1])
                    # detection_masks_reframed = tf.cast(
                        # tf.greater(detection_masks_reframed, 0.5), tf.uint8)
                    # # Follow the convention by adding back the batch dimension
                    # tensor_dict['detection_masks'] = tf.expand_dims(
                        # detection_masks_reframed, 0)
                # image_tensor = tf.compat.v1.get_default_graph().get_tensor_by_name('image_tensor:0')
        #/****************************************************************************************************/

        while True:
            if self.frame_queue.empty() != True:
                frame = self.frame_queue.get()
                
                # 1.process frame,探测图片中的人脸(dlib)
                # gray_img = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
                # dets = self.detector(gray_img, 1)
                #绘制矩形框出人脸区域
                # for e, d in enumerate(dets):
                    # x1 = d.top() if d.top() > 0 else 0
                    # y1 = d.bottom() if d.bottom() > 0 else 0
                    # x2 = d.left() if d.left() > 0 else 0
                    # y2 = d.right() if d.right() > 0 else 0
                    # cv.rectangle(frame, (x2, x1), (y2, y1), (0, 255, 0), 2)
                
                #/****************************************************************************************************/
                # 2.process frame,探测图片中的人脸(zy他们的算法,比dlib(fps:7)慢一半fps:2.4)
                # im_data = cv.resize(frame, IMAGE_SIZE)
                # output_dict = detection_sess.run(tensor_dict,
                                                 # feed_dict={image_tensor:
                                                     # np.expand_dims(
                                                         # im_data, 0)})
                # # all outputs are float32 numpy arrays, so convert types as appropriate
                # output_dict['num_detections'] = int(output_dict['num_detections'][0])
                # output_dict['detection_classes'] = output_dict['detection_classes'][0].astype(np.uint8)
                # output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
                # output_dict['detection_scores'] = output_dict['detection_scores'][0]
                # if 'detection_masks' in output_dict:
                    # output_dict['detection_masks'] = output_dict['detection_masks'][0]
                
                # vis_util.visualize_boxes_and_labels_on_image_array(
                    # frame,
                    # output_dict['detection_boxes'],
                    # output_dict['detection_classes'],
                    # output_dict['detection_scores'],
                    # category_index,
                    # instance_masks=output_dict.get('detection_masks'),
                    # use_normalized_coordinates=True,
                    # line_thickness=8)
                #/****************************************************************************************************/
            
                # write to pipe
                p.stdin.write(frame.tostring())
                
    def run(self):
        threads = [
            threading.Thread(target=Live.read_frame, args=(self,)),
            threading.Thread(target=Live.push_frame, args=(self,))
        ]
        #[thread.setDaemon(True) for thread in threads]
        [thread.start() for thread in threads]
        
# 测试
if __name__ == '__main__':       
    t = Live()
    t.run()      

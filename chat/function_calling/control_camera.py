import cv2
import numpy as np
import time

def control_camera():
    # 打开摄像头
    cap = cv2.VideoCapture(1)
    
    # 检查摄像头是否成功打开
    if not cap.isOpened():
        print("无法打开摄像头")
        return
    
    # 设置摄像头的初始位置和摇头范围
    current_pos = 0
    max_pos = 3
    direction = 1
    cap.set(cv2.CAP_PROP_TILT,0)
    # 记录摇头次数
    shake_count = 0
    
    while shake_count < 5:
        # 自动摇头逻辑
        if direction == 1:
            current_pos += 10
            if current_pos >= 30:  # 向右转到30度
                direction = -1
        else:
            current_pos -= 10
            if current_pos <= -30:  # 向左转到-30度
                direction = 1
                # 完成一次完整的摇头动作
                shake_count += 1
        # 设置摄像头位置
        cap.set(cv2.CAP_PROP_PAN, current_pos)
        
        
        # 添加短暂延时使摇头更平滑
        time.sleep(0.1)
    
    # 释放资源
    cap.release()

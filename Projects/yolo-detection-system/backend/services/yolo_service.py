import os
import time
import random
import uuid
from flask import current_app


class YoloService:
    """YOLO 目标检测服务

    开发环境使用 mock 数据，生产环境接入真实模型
    """
    _instance = None
    _model = None
    _model_loaded = False

    # Mock 类别名称（植物病害检测示例）
    MOCK_CLASSES = ['健康', '斑点病', '白粉病', '锈病', '灰霉病', '炭疽病']

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _use_mock(self):
        """是否使用 mock 数据"""
        return current_app.config.get('YOLO_USE_MOCK', True)

    def load_model(self, model_path=None):
        """加载模型（生产环境使用）"""
        if self._use_mock():
            self._model_loaded = True
            return True

        if model_path is None:
            model_path = current_app.config['YOLO_MODEL_PATH']

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"模型文件不存在: {model_path}")

        try:
            from ultralytics import YOLO
            self._model = YOLO(model_path)
            self._model_loaded = True
            return True
        except ImportError:
            raise RuntimeError("ultralytics 未安装，请先安装: pip install ultralytics")

    def is_model_loaded(self):
        """检查模型是否已加载"""
        return self._model_loaded

    def get_class_names(self):
        """获取类别名称列表"""
        if self._use_mock():
            return self.MOCK_CLASSES

        if not self.is_model_loaded():
            self.load_model()
        return list(self._model.names.values()) if self._model else []

    def _generate_mock_detections(self, image_path=None):
        """生成 mock 检测结果"""
        num_objects = random.randint(1, 6)
        detections = []
        class_summary = {}

        for _ in range(num_objects):
            cls_id = random.randint(0, len(self.MOCK_CLASSES) - 1)
            cls_name = self.MOCK_CLASSES[cls_id]
            confidence = round(random.uniform(0.6, 0.98), 4)

            # 生成随机 bbox [x1, y1, x2, y2]
            x1 = random.randint(20, 200)
            y1 = random.randint(20, 200)
            x2 = x1 + random.randint(50, 200)
            y2 = y1 + random.randint(50, 200)
            bbox = [x1, y1, x2, y2]

            detections.append({
                'class_id': cls_id,
                'class_name': cls_name,
                'confidence': confidence,
                'bbox': bbox,
                'area_ratio': round(random.uniform(0.05, 0.3), 4)
            })
            class_summary[cls_name] = class_summary.get(cls_name, 0) + 1

        return {
            'detections': detections,
            'total_count': len(detections),
            'class_summary': class_summary
        }

    def detect_image(self, image_path, result_dir, save_result=True):
        """检测单张图片

        Args:
            image_path: 图片路径
            result_dir: 结果保存目录
            save_result: 是否保存结果图

        Returns:
            dict: 检测结果
        """
        start_time = time.time()

        if self._use_mock():
            # Mock 模式：生成假数据
            time.sleep(random.uniform(0.1, 0.3))  # 模拟处理耗时
            mock_result = self._generate_mock_detections(image_path)
            processing_time = round(time.time() - start_time, 3)

            result_path = None
            if save_result:
                # Mock 模式下结果路径指向原图（没有真实绘制）
                os.makedirs(result_dir, exist_ok=True)
                result_filename = f"{uuid.uuid4().hex}_result.jpg"
                result_path = os.path.join(result_dir, result_filename)
                # 复制原图作为占位（实际项目中会绘制检测框）
                import shutil
                if os.path.exists(image_path):
                    shutil.copy2(image_path, result_path)

            return {
                'detections': mock_result['detections'],
                'total_count': mock_result['total_count'],
                'class_summary': mock_result['class_summary'],
                'result_path': result_path,
                'processing_time': processing_time,
                'model_version': 'mock-yolo26s'
            }

        # 真实模型检测
        if not self.is_model_loaded():
            self.load_model()

        import cv2

        results = self._model(
            image_path,
            conf=current_app.config['YOLO_CONF_THRESHOLD'],
            iou=current_app.config['YOLO_IOU_THRESHOLD']
        )
        result = results[0]

        processing_time = round(time.time() - start_time, 3)

        # 保存结果图
        result_path = None
        if save_result:
            os.makedirs(result_dir, exist_ok=True)
            filename = f"{uuid.uuid4().hex}_result.jpg"
            result_path = os.path.join(result_dir, filename)
            result_img = result.plot()
            cv2.imwrite(result_path, cv2.cvtColor(result_img, cv2.COLOR_RGB2BGR))

        # 解析检测结果
        detections = []
        class_summary = {}
        for i in range(len(result.boxes)):
            cls_id = int(result.boxes.cls[i])
            cls_name = result.names[cls_id]
            conf = float(result.boxes.conf[i])
            bbox = result.boxes.xyxy[i].tolist()

            detections.append({
                'class_id': cls_id,
                'class_name': cls_name,
                'confidence': round(conf, 4),
                'bbox': [int(x) for x in bbox]
            })
            class_summary[cls_name] = class_summary.get(cls_name, 0) + 1

        return {
            'detections': detections,
            'total_count': len(detections),
            'class_summary': class_summary,
            'result_path': result_path,
            'processing_time': processing_time,
            'model_version': 'yolo26s'
        }

    def detect_video(self, video_path, result_dir, save_result=True, progress_callback=None):
        """检测视频

        Args:
            video_path: 视频路径
            result_dir: 结果保存目录
            save_result: 是否保存结果视频
            progress_callback: 进度回调函数

        Returns:
            dict: 检测结果汇总
        """
        start_time = time.time()

        if self._use_mock():
            # Mock 模式：生成假视频检测结果
            frame_count = random.randint(300, 1500)
            time.sleep(random.uniform(1, 3))  # 模拟处理耗时

            result_path = None
            if save_result:
                os.makedirs(result_dir, exist_ok=True)
                result_filename = f"{uuid.uuid4().hex}_result.mp4"
                result_path = os.path.join(result_dir, result_filename)
                import shutil
                if os.path.exists(video_path):
                    shutil.copy2(video_path, result_path)

            frames_with_objects = int(frame_count * random.uniform(0.5, 0.9))
            class_stats = {}
            for cls_name in random.sample(self.MOCK_CLASSES, random.randint(2, 4)):
                class_stats[cls_name] = random.randint(50, 500)

            processing_time = round(time.time() - start_time, 3)

            return {
                'result_path': result_path,
                'frame_count': frame_count,
                'detection_summary': {
                    'total_frames': frame_count,
                    'frames_with_objects': frames_with_objects,
                    'class_stats': class_stats
                },
                'processing_time': processing_time,
                'model_version': 'mock-yolo26s'
            }

        # 真实视频检测（略，根据需求实现）
        raise NotImplementedError("视频检测功能待实现")


yolo_service = YoloService()

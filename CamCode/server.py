from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import cv2
import time
import numpy as np
from datetime import datetime
import threading
import subprocess
import platform
import logging
import eventlet
eventlet.monkey_patch()

# Настройка путей для Flask
import os
template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Site', 'templates')
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Site', 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# Глобальные переменные
monitor_thread = None
is_monitoring = False
current_mode = None
current_camera_url = "rtsp://ins046msc:wQpQk35t@85.141.77.197:7554/ISAPI/Streaming/Channels/103"

class WebCameraMonitor:
    def __init__(self, rtsp_url, camera_id, socketio, mode='basic'):
        self.rtsp_url = rtsp_url
        self.camera_id = camera_id
        self.socketio = socketio
        self.mode = mode
        self.bitrate_history = []
        self.fps_history = []
        self.window_size = 30
        self.threshold_ratio = 0.3
        self.low_bitrate_count = 0
        self.max_low_bitrate_count = 3
        
    def extract_host(self):
        """Извлечение host из RTSP URL"""
        try:
            if '@' in self.rtsp_url:
                host_part = self.rtsp_url.split('@')[1]
            else:
                host_part = self.rtsp_url.split('//')[1]
            return host_part.split(':')[0]
        except:
            return None
    
    def ping_camera(self, host):
        """Пинг камеры ТОЛЬКО при проблемах"""
        param = "-n" if platform.system().lower() == "windows" else "-c"
        command = ["ping", param, "1", host]
        
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=5)
            return "success" if result.returncode == 0 else "failed"
        except:
            return "error"
    
    def check_bitrate_drop(self, current_bitrate):
        """Проверка падения битрейта"""
        if len(self.bitrate_history) < self.window_size:
            return False
        avg_bitrate = np.mean(self.bitrate_history[-self.window_size:])
        return current_bitrate < avg_bitrate * self.threshold_ratio and avg_bitrate > 1000
    
    def check_fps_drop(self, current_fps):
        """Проверка падения FPS"""
        if len(self.fps_history) < 10:
            return False
        avg_fps = np.mean(self.fps_history[-10:])
        return current_fps < 5 or (avg_fps > 10 and current_fps < avg_fps * 0.2)
    
    def analyze_image_quality(self, frame):
        """Анализ качества изображения (для расширенного режима)"""
        if frame is None or self.mode != 'advanced':
            return {}
        
        quality_metrics = {}
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Детекция черного/белого экрана
            mean_brightness = np.mean(gray)
            quality_metrics['brightness'] = mean_brightness
            if mean_brightness < 10:
                quality_metrics['black_screen'] = True
            elif mean_brightness > 240:
                quality_metrics['white_screen'] = True
            
            # Анализ резкости
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            quality_metrics['sharpness'] = laplacian_var
            quality_metrics['blurry'] = laplacian_var < 50
            
            # Анализ контраста
            contrast = np.std(gray)
            quality_metrics['contrast'] = contrast
            quality_metrics['low_contrast'] = contrast < 20
            
        except Exception as e:
            print(f"Ошибка анализа изображения: {e}")
            
        return quality_metrics
    
    def send_status_update(self, data):
        """Отправка данных через WebSocket"""
        self.socketio.emit('status_update', data)
    
    def send_log_entry(self, message, log_type='info'):
        """Отправка лога через WebSocket"""
        self.socketio.emit('log_entry', {
            'message': message,
            'type': log_type,
            'time': datetime.now().strftime('%H:%M:%S')
        })
    
    def monitor_stream(self):
        """Основной цикл мониторинга"""
        global is_monitoring
        
        self.send_log_entry(f'Запуск мониторинга ({self.mode} режим)...', 'info')
        
        cap = cv2.VideoCapture(self.rtsp_url)
        if not cap.isOpened():
            self.send_log_entry('ERROR: Не удалось подключиться к RTSP потоку', 'error')
            self.send_status_update({
                'connectionStatus': 'Ошибка подключения',
                'alert': True
            })
            return
        
        self.send_log_entry('Успешное подключение к RTSP потоку', 'success')
        
        frame_count = 0
        start_time = time.time()
        last_status_time = time.time()
        last_frame_time = time.time()
        
        try:
            while is_monitoring:
                ret, frame = cap.read()
                current_time = time.time()
                
                if not ret:
                    self.send_log_entry('WARNING: Потерян видеопоток', 'warning')
                    host = self.extract_host()
                    if host:
                        ping_result = self.ping_camera(host)
                        if ping_result == "success":
                            self.send_log_entry('Камера доступна по ping - проблема с RTSP потоком', 'info')
                        else:
                            self.send_log_entry('CRITICAL: Камера недоступна по ping!', 'error')
                            self.send_status_update({
                                'connectionStatus': 'Камера недоступна',
                                'alert': True
                            })
                    
                    time.sleep(5)
                    continue
                
                # Расчет метрик
                current_bitrate = len(frame) * 8 if frame is not None else 0
                current_fps = 1.0 / (current_time - last_frame_time) if current_time - last_frame_time > 0 else 0
                
                self.bitrate_history.append(current_bitrate)
                self.fps_history.append(current_fps)
                
                # Ограничение истории
                if len(self.bitrate_history) > self.window_size * 2:
                    self.bitrate_history.pop(0)
                if len(self.fps_history) > 20:
                    self.fps_history.pop(0)
                
                frame_count += 1
                last_frame_time = current_time
                
                # Анализ качества в расширенном режиме
                quality_metrics = {}
                quality_status = "Хорошее"
                if self.mode == 'advanced':
                    quality_metrics = self.analyze_image_quality(frame)
                    if quality_metrics.get('black_screen'):
                        quality_status = "Черный экран"
                    elif quality_metrics.get('white_screen'):
                        quality_status = "Белый экран"
                    elif quality_metrics.get('blurry'):
                        quality_status = "Размытое"
                    elif quality_metrics.get('low_contrast'):
                        quality_status = "Низкая контрастность"
                
                # Проверка проблем каждые 2 секунды
                if current_time - last_status_time >= 2:
                    bitrate_problem = self.check_bitrate_drop(current_bitrate)
                    fps_problem = self.check_fps_drop(current_fps)
                    
                    alert_triggered = False
                    
                    if bitrate_problem or fps_problem:
                        self.low_bitrate_count += 1
                        if self.low_bitrate_count >= self.max_low_bitrate_count:
                            alert_triggered = True
                            self.send_log_entry('ALERT: Проблема с качеством видео', 'warning')
                            
                            host = self.extract_host()
                            if host:
                                ping_result = self.ping_camera(host)
                                if ping_result == "success":
                                    self.send_log_entry('Камера доступна - проблема в качестве потока', 'info')
                                else:
                                    self.send_log_entry('CRITICAL: Камера недоступна по ping!', 'error')
                    else:
                        self.low_bitrate_count = max(0, self.low_bitrate_count - 1)
                    
                    # Отправка данных в веб-интерфейс
                    avg_bitrate = np.mean(self.bitrate_history[-10:]) if len(self.bitrate_history) >= 10 else current_bitrate
                    avg_fps = np.mean(self.fps_history[-10:]) if len(self.fps_history) >= 10 else current_fps
                    
                    status_data = {
                        'bitrate': f"{(current_bitrate/1000):.1f}",
                        'fps': f"{current_fps:.1f}",
                        'connectionStatus': 'Активно',
                        'quality': quality_status,
                        'frameCount': frame_count,
                        'avgBitrate': f"{(avg_bitrate/1000):.1f}",
                        'alert': alert_triggered,
                        'uptime': int(current_time - start_time)
                    }
                    
                    self.send_status_update(status_data)
                    last_status_time = current_time
                
                time.sleep(0.01)
                
        except Exception as e:
            self.send_log_entry(f'ERROR: {str(e)}', 'error')
        finally:
            cap.release()
            self.send_log_entry('Мониторинг остановлен', 'warning')
            self.send_status_update({
                'connectionStatus': 'Не активно',
                'alert': False
            })

# WebSocket события
@socketio.on('connect')
def handle_connect():
    print('Клиент подключился')
    emit('log_entry', {
        'message': 'Подключение к серверу установлено',
        'type': 'success',
        'time': datetime.now().strftime('%H:%M:%S')
    })

@socketio.on('disconnect')
def handle_disconnect():
    print('Клиент отключился')

@socketio.on('start_monitoring')
def handle_start_monitoring(data):
    global monitor_thread, is_monitoring, current_mode
    
    if is_monitoring:
        emit('log_entry', {
            'message': 'Мониторинг уже запущен',
            'type': 'warning',
            'time': datetime.now().strftime('%H:%M:%S')
        })
        return
    
    mode = data.get('mode', 'basic')
    current_mode = mode
    is_monitoring = True
    
    monitor = WebCameraMonitor(current_camera_url, "cam_001", socketio, mode)
    
    # Запуск мониторинга в отдельном потоке
    monitor_thread = threading.Thread(target=monitor.monitor_stream)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    emit('log_entry', {
        'message': f'Запущен {mode} мониторинг',
        'type': 'success',
        'time': datetime.now().strftime('%H:%M:%S')
    })

@socketio.on('stop_monitoring')
def handle_stop_monitoring():
    global is_monitoring
    
    is_monitoring = False
    
    emit('log_entry', {
        'message': 'Остановка мониторинга...',
        'type': 'warning',
        'time': datetime.now().strftime('%H:%M:%S')
    })

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/logs')
def get_logs():
    """Получение логов из файла log.txt"""
    try:
        # Используем абсолютный путь относительно корня проекта
        import os
        log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Site', 'templates', 'log.txt')
        with open(log_path, 'r', encoding='utf-8') as f:
            logs = f.read()
        return jsonify({'logs': logs})
    except FileNotFoundError:
        return jsonify({'logs': 'Файл логов не найден'})
    except Exception as e:
        return jsonify({'logs': f'Ошибка чтения логов: {str(e)}'})

if __name__ == '__main__':
    print("Запуск сервера мониторинга камер...")
    print("Откройте http://localhost:5000 в браузере")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
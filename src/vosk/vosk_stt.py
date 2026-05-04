import os
import time
import wave
import json
from datetime import datetime
import numpy as np
import sounddevice as sd
import soundfile as sf
from vosk import Model, KaldiRecognizer
import resampy
import threading
import socket

# 全局变量
UI_IP = "127.0.0.1"
UI_PORT = 7399

# 显示可用的麦克风
def show_microphones():
    """显示可用的麦克风（修复设备ID问题）"""
    print("\n 正在扫描音频设备...")
    devices = sd.query_devices()
    mic_list = []
    
    print("\n可用麦克风列表:")
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            device_name = device['name']
            sample_rate = int(device['default_samplerate'])
            channels = device['max_input_channels']
            mic_list.append({
                'id': i,  # 实际的设备ID
                'name': device_name,
                'rate': sample_rate,
                'channels': channels
            })
            print(f"  [{len(mic_list)-1}] {device_name}")
            print(f"      通道: {channels}, 默认采样率: {sample_rate}Hz")
    
    return mic_list

def select_microphones(name):
    # 显示可用的麦克风（修复设备ID问题）
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            if name in device['name']:
                return i
    return -1
    
def choose_microphone():
    """让用户选择麦克风（修复索引问题）"""
    mics = show_microphones()
    
    if not mics:
        print(" 未找到麦克风设备")
        return None
    
    try:
        choice = input(f"\n选择麦克风编号 (0-{len(mics)-1}，默认0): ").strip()
        if choice == "":
            selected = mics[0]
        else:
            index = int(choice)
            if 0 <= index < len(mics):
                selected = mics[index]
            else:
                print("⚠ 编号无效，使用默认设备")
                selected = mics[0]
        
        print(f" 已选择: {selected['name']} (设备ID: {selected['id']})")
        return selected['id']  # 返回实际的设备ID
        
    except Exception as e:
        print(f" 选择失败: {e}，使用默认设备")
        return mics[0]['id'] if mics else None

def test_microphone(device_id, test_duration=2):
    """测试麦克风是否能正常工作"""
    if device_id is None:
        return False
    
    try:
        device_info = sd.query_devices(device_id)
        default_rate = int(device_info['default_samplerate'])
        
        print(f"\n 测试麦克风: {device_info['name']}")
        print(f"   测试时长: {test_duration}秒")
        print(f"   采样率: {default_rate}Hz")
        print("   请对着麦克风说话...")
        
        # 录制测试音频
        test_audio = sd.rec(
            int(test_duration * default_rate),
            samplerate=default_rate,
            channels=1,
            device=device_id,
            dtype='float32'
        )
        
        for i in range(test_duration):
            time.sleep(1)
            print(f"\r  测试中... {i+1}/{test_duration}秒", end="")
        
        sd.wait()
        print("\n测试完成")
        
        # 分析录音音量
        if test_audio is not None and len(test_audio) > 0:
            rms = np.sqrt(np.mean(test_audio**2))
            print(f" 录音音量: {rms:.6f}")
            
            if rms < 0.001:  # 非常低的音量阈值
                print("   警告: 检测到音量极低，可能麦克风未正确捕获声音")
                print("   请检查:")
                print("   1. 麦克风是否被物理静音")
                print("   2. 系统麦克风权限是否开启")
                print("   3. 麦克风是否被其他程序占用")
                return False
            else:
                print("麦克风工作正常")
                return True
        else:
            print("未录制到音频数据")
            return False
            
    except Exception as e:
        print(f"麦克风测试失败: {e}")
        return False

record_files = []

def simple_record(device_id, duration=5):
    """使用设备默认采样率录音（增强版）"""
    if device_id is None:
        print("无可用麦克风设备")
        return None
    
    # 获取设备信息
    try:
        device_info = sd.query_devices(device_id)
        device_name = device_info['name']
        device_sample_rate = int(device_info['default_samplerate'])
    except:
        print("无法获取设备信息")
        return None
    
    # 创建保存目录
    save_dir = os.path.join(os.getcwd(), "recordings")
    os.makedirs(save_dir, exist_ok=True)
    
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"recording_{timestamp}.wav"
    filepath = os.path.join(save_dir, filename)
    
    print(f"\n开始录音:")
    print(f"   设备: {device_name}")
    print(f"   时长: {duration}秒")
    print(f"   采样率: {device_sample_rate}Hz")
    print(f"   保存到: {filepath}")
    print("   请说话...")
    
    try:
        # 使用设备默认采样率录音
        recording = sd.rec(
            int(duration * device_sample_rate),
            samplerate=device_sample_rate,
            channels=1,
            device=device_id,
            dtype='int16'
        )
        
        # 显示录音进度
        for i in range(duration):
            time.sleep(1)
            print(f"\r  {i+1}/{duration}秒", end="", flush=True)
        
        sd.wait()
        print("\n录音完成")
        
        # 检查录音数据
        if recording is None or len(recording) == 0:
            print("错误: 录音数据为空")
            return None
        
        # 计算音量
        rms = np.sqrt(np.mean(recording.astype(float)**2))
        print(f"录音音量: {rms:.2f} (0-32767范围)")
        
        if rms < 100:  # int16范围下的低音量
            print("警告: 录音音量较低")
        
        # 保存为WAV文件
        sf.write(filepath, recording, device_sample_rate)
        print(f"已保存: {filename}")
        
        ret = {
            'filepath': filepath,
            'sample_rate': device_sample_rate,
            'duration': duration,
            'volume': rms
        }
        
        record_files.append(ret)
        
        return ret
        
    except Exception as e:
        print(f"录音失败: {e}")
        return None

def resample_audio(audio_data, original_rate, target_rate=16000):
    """将音频重采样到目标采样率"""
    if original_rate == target_rate:
        return audio_data
    
    # 使用resampy进行高质量重采样
    resampled = resampy.resample(
        audio_data.astype(float) / 32768.0,  # 归一化到[-1, 1]
        sr_orig=original_rate, 
        sr_new=target_rate
    )
    
    # 转换回int16
    resampled = np.int16(resampled * 32767)
    
    print(f"重采样: {original_rate}Hz → {target_rate}Hz")
    return resampled

def simple_transcribe(audio_info, model):
    """语音转文字（自动重采样）"""
    if not audio_info:
        return
    
    wav_file = audio_info['filepath']
    original_rate = audio_info['sample_rate']
    
    print(f"\n 开始识别:")
    print(f"   文件: {os.path.basename(wav_file)}")
    print(f"   原始采样率: {original_rate}Hz")
    
    try:
        # 读取音频文件
        data, samplerate = sf.read(wav_file, dtype='int16')
        
        # 检查音频数据
        if len(data) == 0:
            print("错误: 音频文件为空")
            return None
        
        # 如果是立体声，转换为单声道
        if len(data.shape) > 1 and data.shape[1] > 1:
            data = np.mean(data, axis=1, dtype=np.int16)
            print(f"立体声转单声道")
        
        # 自动重采样到16000Hz
        if samplerate != 16000:
            data = resample_audio(data, samplerate, 16000)
            samplerate = 16000
        
        # 创建Vosk识别器
        rec = KaldiRecognizer(model, samplerate)
        rec.SetWords(True)
        
        # 分块识别
        chunk_size = 4000
        result_text = ""
        
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i+chunk_size]
            if len(chunk) < chunk_size:
                # 补零填充最后一个块
                chunk = np.pad(chunk, (0, chunk_size - len(chunk)), 'constant')
            
            if rec.AcceptWaveform(chunk.tobytes()):
                result = json.loads(rec.Result())
                if 'text' in result and result['text']:
                    result_text += result['text'] + " "
        
        # 获取最终结果
        final_result = json.loads(rec.FinalResult())
        if 'text' in final_result and final_result['text']:
            result_text += final_result['text']
        
        if result_text.strip():
            print(f"\n识别结果:\n{result_text.strip()}")
        else:
            print("\n未识别到语音内容")
        
        return result_text.strip()
        
    except Exception as e:
        print(f"识别失败: {e}")
        return None


def transcribe_thread(model):
    pos = 0
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dest_addr = (UI_IP,UI_PORT)
    while True:
        if len(record_files) > pos:
            text = simple_transcribe(record_files[pos], model)
            text = f"@person:{text}"
            if text:
                udp_socket.sendto(text.encode('utf-8'), dest_addr)
                print(f"发送给客户端:{text}")
            pos+=1
        
# ========== 主程序 ==========
def main():
    print("="*60)
    print("语音转文字系统")
    print("="*60)
    
    # 加载Vosk模型
    model_path = "vosk-model-small-cn-0.22"
    if not os.path.exists(model_path):
        print(f"❌ 找不到模型: {model_path}")
        print("   请从 https://alphacephei.com/vosk/models 下载中文模型")
        return
    
    print("加载语音识别模型...")
    try:
        model = Model(model_path)
        print("模型加载成功")
    except Exception as e:
        print(f"模型加载失败: {e}")
        return
    
    # 选择USB麦克风
    device_name = "USB"
    device_id = select_microphones(device_name)
    if device_id < 0:
        print(f"没有找到有关({device_name})的麦克风")
        return
    
    # 清除录制目录下的文件
    save_dir = os.path.join(os.getcwd(), "recordings")
    os.system(f"rm -r {save_dir}")
    
    while True:
        # 转文字任务
        rec_thread = threading.Thread(target=transcribe_thread, args=(model,), daemon=True)
        rec_thread.start()

        # 录制任务
        try:
            cycle = 1
            while True:
                print(f"\n第{cycle}次录音:")
                simple_record(device_id, 5)
                # 录制后识别
                # audio_info = simple_record(device_id, 5)
                # if audio_info:
                #    _ = simple_transcribe(audio_info, model)
                cycle += 1
        except KeyboardInterrupt:
            break
    
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"\n程序出错: {e}")
        import traceback
        traceback.print_exc()
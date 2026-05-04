
import pyttsx3
import os
import threading
import sys

def speak_chinese_async(text, rate=160, volume=1.0):
    def _speak_task():
        try:
            # # 初始化语音引擎
            # engine = pyttsx3.init(driverName='espeak')
            
            # # 设置语速和音量
            # engine.setProperty('rate', rate)
            # engine.setProperty('volume', volume)
            
            # # 获取所有可用语音并查找中文语音
            # voices = engine.getProperty('voices')
            # chinese_voice_id = None
            # for voice in voices:
            #     # 匹配包含 'chinese' 或 'zh' 标识的语音
            #     if 'chinese' in voice.name.lower() or 'zh' in voice.id.lower():
            #         chinese_voice_id = voice.id
            #         break
            
            # # 如果找到中文语音则设置，否则使用默认（可能发音不准）
            # if chinese_voice_id:
            #     engine.setProperty('voice', chinese_voice_id)
            # else:
            #     print("警告：未检测到明确的中文语音包，将使用系统默认语音。")
                
            # # 执行朗读
            # engine.say(text)
            # engine.runAndWait()
            os.system(f"espeak -v zh {text}")
        except Exception as e:
            print(f"语音播放出错: {e}")

    # 创建并启动守护线程
    thread = threading.Thread(target=_speak_task, daemon=True)
    thread.start()

if __name__ == "__main__":
    print("=== 中文语音播报助手 ===")
    print("请输入要朗读的文本（输入 'quit' 或 'exit' 退出）：")
    
    while True:
        try:
            # 获取用户输入
            user_input = input("\n> ")
            
            # 检查退出条件
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("程序已退出。")
                break
            
            # 忽略空输入
            if not user_input.strip():
                continue
                
            # 执行异步语音播报
            speak_chinese_async(user_input)
            print(">> 语音正在后台播放...")
            
        except KeyboardInterrupt:
            print("\n程序被用户中断。")
            break
        except EOFError:
            print("\n输入流结束，程序退出。")
            break


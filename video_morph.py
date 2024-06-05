
import os
from pathlib import Path
from dotenv import load_dotenv
import shutil
import argparse
from urllib.parse import urlparse
import requests

from base import RvcBase
from uvr import UvrClient
from extra.utils import add_suffix_to_filename

from  extra.logger import setup_logger
log_file = 'VideoMorph.log' 
logger = setup_logger(log_file,"VideoMorph")

TEMP = "./temp"
INPUT_FILE_TAG = ""
def get_file(file_path:str):

    """
    根据提供的文件路径或URL，获取文件并将其保存到临时目录中。
    
    参数:
    - file_path: 字符串，文件的路径或URL。
    
    返回值:
    - 如果成功复制或下载文件并保存到临时目录，返回新文件的路径；
    - 如果发生异常，抛出相应的异常。
    """
    # 解析输入路径或URL
    parsed_url = urlparse(file_path)
    if parsed_url.scheme in ('http', 'https'):
        logger.info("开始下载视频: {}".format(file_path))
        response = requests.get(file_path, stream=True)
        if response.status_code == 200:
            # 获取文件名并创建新的文件路径
            filename = os.path.basename(parsed_url.path)
            #filename = INPUT_FILE_TAG  +  "_" + filename
            new_file_path = os.path.join(TEMP, filename)
            new_file_path = add_suffix_to_filename(new_file_path,INPUT_FILE_TAG)
            # 下载并保存文件
            try:
                with open(new_file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                logger.info(f"视频下载成功")
                return new_file_path
                
            except Exception as e:
                logger.warning(f"视频下载失败: {e}")
                raise Exception(f"视频下载失败: {e}")
        else:
            error_msg = f"链接请求失败: 状态码 {response.status_code}"
            logger.error(error_msg)
            raise Exception(error_msg)
    else:
        # 本地文件情况
        logger.info("获取本地文件：{}".format(file_path))
        file_path = Path(file_path)
        if file_path.exists() and file_path.is_file():
            # 获取文件名并创建新的文件路径
            filename = file_path.name
            new_file_path = os.path.join(TEMP, filename)
            new_file_path = add_suffix_to_filename(new_file_path,INPUT_FILE_TAG)

            #如果输出路径文件存在，判断是否是一个文件
            if os.path.exists(new_file_path):
                from extra.utils import is_same_file
                if is_same_file(file_path, new_file_path):
                    logger.info(f"目标位置同名文件校验一直，跳过复制")
                    return new_file_path
                else:
                    logger.info(f"目标位置同名文件校验不一致，删除")
                    os.remove(new_file_path)
            try:
                shutil.copy(file_path, new_file_path)
                logger.info(f"文件复制成功")
                return new_file_path
            except Exception as e:
                logger.warning(f"文件复制失败: {e}")
                raise Exception(f"文件复制失败: {e}")
        else:
            error_msg = "文件复制失败：文件不存在"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

class VideoMorph:
    def __init__(self,model_name:str):
        load_dotenv()
        self.uvr_1 = UvrClient(model_name = os.getenv('uvr_1_model_name'))
        #self.uvr_2 = UvrClient(model_name = os.getenv('uvr_2_model_name'))
        self.rvc_client = RvcBase(model_name=model_name)
    def run(self,input_file,output_folder_path="./temp/output",pitch_shift=0):
        if not os.path.exists(output_folder_path):
            os.makedirs(output_folder_path,exist_ok=True)
        temp_file_path = get_file(input_file)
        
        # 第一步：得到音频
        if temp_file_path.endswith((".mp4", ".avi")):
            logger.info(f"视频文件提取音轨")
            try:
                temp_audio_path = os.path.splitext(temp_file_path)[0] + ".wav"
                from extra.utils import extract_audio
                extract_audio(temp_file_path, temp_audio_path)
            except Exception as e:
                logger.warning(f"提取音轨失败: {e}")
                raise Exception(f"提取音轨失败: {e}")

        elif temp_file_path.endswith((".wav", ".mp3")):
            temp_audio_path = temp_file_path
        else:
            raise ValueError("不支持的文件类型")
        logger.info("RVC 开始处理: {}".format(temp_audio_path))
        # 第二步：音频清洁
        try:
            logger.info("UVR 1 开始处理，使用模型：{}".format(os.getenv('uvr_1_model_name')))
            instrumental_1,vocals_1=self.uvr_1.infer(temp_audio_path)
            logger.info("UVR 2 开始处理，使用模型：{}".format(os.getenv('uvr_2_model_name')))
            self.uvr_1.change_model(os.getenv('uvr_2_model_name'))
            no_echo,instrumental =self.uvr_1.infer(os.path.join(TEMP,vocals_1))
            temp_separator_audio_path = os.path.join(TEMP,no_echo)
            logger.info("UVR 音频清洁结束：{}".format(temp_separator_audio_path))
        except Exception as e:
            logger.warning(f"UVR 音频清洁失败: {e}")
            raise Exception(f"UVR 音频清洁失败: {e}")

        # 第三步：音频变声
        logger.info("RVC 变声开始: {}".format(temp_separator_audio_path))
        final_audio_path = self.rvc_client.run(input_audio_path=temp_separator_audio_path,
                                                output_folder_path=TEMP,
                                                pitch_shift=pitch_shift)
        logger.info("RVC 变声结束：{}".format(final_audio_path))

        # 根据输入类型不同进行不同处理
        if temp_file_path.endswith((".mp4", ".avi")):
            # 如果传入是视频，则将变声音轨融合
            final_videos_path = add_suffix_to_filename(temp_file_path,"rvc")
            logger.info("视频合成结束：{}".format(final_videos_path))
            from extra.utils import concat_video_audio
            concat_video_audio(temp_file_path,
                               final_audio_path,
                                final_videos_path)
            logger.info("视频合成结束")

            # 删除最初视频提取的音频
            temp_audio_path = Path(temp_audio_path)
            if temp_audio_path.exists():
                temp_audio_path.unlink()
            # 删除变声后文件
            final_audio_path = Path(final_audio_path)
            if final_audio_path.exists():
                final_audio_path.unlink()

            shutil.move(final_videos_path,output_folder_path)
        else:
            shutil.move(final_audio_path,output_folder_path)

        # 删除清理后音频
        temp_separator_audio_path = Path(temp_separator_audio_path)    
        if temp_separator_audio_path.exists():
            temp_separator_audio_path.unlink()
        # 删除最初输入文件
        temp_file_path = Path(temp_file_path)
        if temp_file_path.exists():
            temp_file_path.unlink()

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="变声工具")
    parser.add_argument("--input","-i", help="输入音频或者视频，可以是url或者本地文件", type=str,required=True)
    parser.add_argument("--output","-o", help="输出文件路径", type=str,required=False,default="./temp/output")
    parser.add_argument("--pitch","-p", help="变声音调", type=int,required=False,default=0)
    parser.add_argument("--model","-m", help="模型名称", type=str,required=False,default=None)
    args = parser.parse_args()

    rvc = VideoMorph(args.model)
    rvc.run(args.input,args.output,args.pitch)
    

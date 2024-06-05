from dotenv import load_dotenv
import os
from base import RvcBase
from uvr import UvrClient

from  extra.logger import setup_logger
log_file = 'MusicMorph.log' 
logger = setup_logger(log_file,"MusicMorph")


class MusicMorph():
    def __init__(self,model_name=None):
        load_dotenv()
        self.uvr = UvrClient(model_name = os.getenv('uvr_1_model_name'))
        self.rvc = RvcBase(model_name=model_name)
        self.temp_folder_path = os.getenv('temp_files')
    
    def run(self,input_file,output_folder_path="./temp/output",pitch_shift=0):
        if not os.path.exists(output_folder_path):
            os.makedirs(output_folder_path,exist_ok=True)
        

        logger.info("RVC 开始处理: {}".format(input_file))
        # 第一步，分离人声伴奏
        try:
            logger.info("UVR 1 开始处理，使用模型：{}".format(os.getenv('uvr_1_model_name')))
            instrumental_1,vocals_1=self.uvr.infer(input_file)
            logger.info("UVR 2 开始处理，使用模型：{}".format(os.getenv('uvr_2_model_name')))
            self.uvr.change_model(os.getenv('uvr_2_model_name'))
            uvr_1_temp = os.path.join(self.temp_folder_path,vocals_1)
            no_echo,instrumental =self.uvr.infer(uvr_1_temp)
            
            temp_bg1_audio_path = os.path.join(self.temp_folder_path,instrumental_1)
            temp_bg2_audio_path = os.path.join(self.temp_folder_path,instrumental)
            temp_separator_audio_path = os.path.join(self.temp_folder_path,no_echo)

            logger.info("UVR 音频清洁结束：{}".format(temp_separator_audio_path))
        except Exception as e:
            logger.warning(f"UVR 音频清洁失败: {e}")
            raise Exception(f"UVR 音频清洁失败: {e}")
        
        # 第二步，变声
        logger.info("RVC 变声开始: {}".format(temp_separator_audio_path))
        rvc_audio_path = self.rvc.run(input_audio_path=temp_separator_audio_path,
                                        output_folder_path=self.temp_folder_path,
                                        pitch_shift=pitch_shift)
        logger.info("RVC 变声结束：{}".format(rvc_audio_path))

        # 第三步，融合背景音
        output_audio_path = os.path.join(output_folder_path, os.path.basename(input_file))
        from extra.utils import add_suffix_to_filename
        from extra.utils import merge_audio_files
        output_audio_path = add_suffix_to_filename(output_audio_path, "rvc")
        if(os.path.exists(output_audio_path)):
            os.remove(output_audio_path)
        input_files = [rvc_audio_path, temp_bg1_audio_path, temp_bg2_audio_path]
        merge_audio_files(output_audio_path, *input_files)
        
        # 第四步，删除临时文件
        if os.path.exists(uvr_1_temp):
            os.remove(uvr_1_temp)
        if os.path.exists(rvc_audio_path):
            os.remove(rvc_audio_path)
        if os.path.exists(temp_bg1_audio_path):
            os.remove(temp_bg1_audio_path)
        if os.path.exists(temp_bg2_audio_path):
            os.remove(temp_bg2_audio_path)
        if os.path.exists(temp_separator_audio_path):
            os.remove(temp_separator_audio_path)

        logger.info("RVC 变声结束：{}".format(output_audio_path))

        
import argparse
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="歌曲变声")
    parser.add_argument("--input","-i", help="输入音频或者视频，可以是url或者本地文件", type=str,required=True)
    parser.add_argument("--output","-o", help="输出文件路径", type=str,required=False,default="./temp/output")
    parser.add_argument("--pitch","-p", help="变声音调", type=int,required=False,default=0)
    parser.add_argument("--model","-m", help="模型名称", type=str,required=False,default=None)
    args = parser.parse_args()

    rvc = MusicMorph(args.model)
    rvc.run(args.input,args.output,args.pitch)


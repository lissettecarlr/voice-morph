import os
from pathlib import Path
from dotenv import load_dotenv
from scipy.io import wavfile
from rvc.modules.vc.modules import VC
from extra.utils import add_suffix_to_filename

from extra.logger import setup_logger
log_file = 'base.log' 
logger = setup_logger(log_file,"base")

class RvcBase:
    def __init__(self,model_name = None):
        load_dotenv()
        self.temp_folder_path = Path(os.getenv('temp_files'))
        #print("缓存目录: {}".format({self.temp_folder_path}))
        if not self.temp_folder_path.exists():
            self.temp_folder_path.mkdir(parents=True, exist_ok=True)

        self.rvc_client = VC()
        if model_name is None:
            self.rvc_client.get_vc(os.getenv('rvc_default_model_name') + '.pth')
        else:
            self.rvc_client.get_vc(model_name + '.pth')

    def model_change(self,model_name):
        logger.info(f"RVC 模型切换: {model_name}")
        self.rvc_client.get_vc(model_name + '.pth')

    def run(self,input_audio_path,output_folder_path="",pitch_shift=0):
        if output_folder_path == "":
            output_folder_path = self.temp_folder_path
       
        # 判断输入文件是否存在
        if not os.path.exists(input_audio_path):
            logger.error(f"输入文件不存在: {input_audio_path}")
            return
        if not input_audio_path.endswith((".wav", ".mp3")):
            logger.error(f"不支持的文件类型: {input_audio_path}，请传入wav或mp3格式的文件")

        logger.info("RVC 开始处理: {}".format(input_audio_path))

        if not os.path.exists(output_folder_path):
            os.makedirs(output_folder_path)

        input_audio_name = os.path.basename(input_audio_path)
        output_audio_path = os.path.join(output_folder_path, input_audio_name)
        output_audio_path = add_suffix_to_filename(output_audio_path,"rvc")

        if os.path.exists(output_audio_path):
            logger.info(f"{output_audio_path} 已存在，删除旧文件")
            os.remove(output_audio_path)
                
        tgt_sr, audio_opt, times, _ = self.rvc_client.vc_single(
            sid=1,
            input_audio_path=Path(input_audio_path),
            f0_up_key=pitch_shift  # 0 # 
        )
        wavfile.write(output_audio_path, tgt_sr, audio_opt)
        logger.info("RVC 变声结束：{}".format(output_audio_path))
        return output_audio_path

    
import argparse

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="变声工具")
    parser.add_argument("--input","-i", help="输入干音频", type=str,required=True)
    parser.add_argument("--output","-o", help="输出文件路径", type=str,required=False,default="")
    parser.add_argument("--pitch","-p", help="变声音调", type=int,required=False,default=0)
    parser.add_argument("--model","-m", help="模型名称", type=str,required=False,default=None)
    args = parser.parse_args()
    client = RvcBase(model_name=args.model)
    client.run(input_audio_path=args.input,output_folder_path=args.output,pitch_shift=args.pitch)

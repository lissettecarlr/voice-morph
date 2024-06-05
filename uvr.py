# 音频清洁工具

import argparse
from audio_separator.separator import Separator  
import os
import logging
import torch

from dotenv import load_dotenv
load_dotenv()
DEFAULT_UVR_MODEL_FOLDER = os.getenv("./models/uvr")

class UvrClient:
    def __init__(self, model_name, model_file_dir=DEFAULT_UVR_MODEL_FOLDER, output_dir="./temp", sample_rate=44000) -> None:
        self.model = Separator(log_level=logging.WARN,
                               model_file_dir=model_file_dir,
                               output_dir=output_dir,
                               sample_rate=sample_rate,
                               output_format="WAV")
        # 搜索模型文件夹model_file_dir，找到后缀为pth或者onnx的文件
        self.models_list = []
        for file in os.listdir(model_file_dir):
            if file.endswith(".pth") or file.endswith(".onnx"):
                self.models_list.append(file)
        
        self.change_model(model_name)
 
    def change_model(self, model_name):      
        if model_name not in self.models_list:
            raise ValueError(f"model {model_name} not found in {self.models_list}")
        else:
            self.model.load_model(model_name)
   

    def infer(self, audio):
        primary_stem_output_path, secondary_stem_output_path = self.model.separate(audio)
        torch.cuda.empty_cache()
        return primary_stem_output_path, secondary_stem_output_path

def main():
    parser = argparse.ArgumentParser(description="UVR MDXNET Client Tool")
    parser.add_argument('--model_name', type=str, required=True, help='Path to the model name')
    parser.add_argument('--audio', type=str, required=True, help='Path to the audio file to process')
    parser.add_argument('--model_file_dir', type=str, default=DEFAULT_UVR_MODEL_FOLDER, help='Directory of the model files')
    parser.add_argument('--output_dir', type=str, default="./temp", help='Directory to save the output files')
    parser.add_argument('--sample_rate', type=int, default=44000, help='Sample rate of the audio')
    
    args = parser.parse_args()
    
    client = UvrClient(model_name=args.model_name,
                               model_file_dir=args.model_file_dir,
                               output_dir=args.output_dir,
                               sample_rate=args.sample_rate)
    
    primary_stem_output_path, secondary_stem_output_path = client.infer(audio=args.audio)
    
    print(f"Primary stem output path: {primary_stem_output_path}")
    print(f"Secondary stem output path: {secondary_stem_output_path}")

if __name__ == "__main__":
    main()


# python uvr.py --model_name="UVR_MDXNET_Main.onnx" --audio="./temp/SPEAKER_03_750225_752706.wav"
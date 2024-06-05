# 音频清洁工具

import argparse
from audio_separator.separator import Separator  
import os
import logging
import torch

from dotenv import load_dotenv
load_dotenv()
DEFAULT_UVR_MODEL_FOLDER = os.getenv("weight_uvr5_root")

class UvrClient:
    def __init__(self, model_name, model_file_dir=DEFAULT_UVR_MODEL_FOLDER, output_dir="./temp", sample_rate=44000) -> None:


        vr_params={"batch_size": 8,  # 批处理大小 值越大将会消耗更多的内存
                   "window_size": 512, # 平衡质量和速度。1024=速度快但质量较低，320=速度慢但质量更好
                   "aggression": 5, # 主要音轨提取的强度，范围为-100到100。通常5适用于人声和乐器
                   "enable_tta": False, # 启用测试时增强；速度较慢但提高质量
                   "enable_post_process": False,  # 识别人声输出中的残留伪影；可能改善某些歌曲的分离效果
                   "post_process_threshold": 0.2,  # 后处理功能的阈值：0.1-0.3
                   "high_end_process": False} # 镜像输出的缺失频率范围
        
        mdx_params={"hop_length": 1024, 
                    "segment_size": 256, # 控制处理段的大小。值越大，消耗的资源越多，但可能会得到更好的结果
                    "overlap": 0.25, # 控制预测窗口之间的重叠量，取值范围为0.001到0.999。值越高，效果越好，但速度会变慢
                    "batch_size": 1, # 批处理大小。值越大，消耗的内存越多
                    "enable_denoise": False}

        self.model = Separator(log_level=logging.WARN,
                               model_file_dir=model_file_dir,
                               output_dir=output_dir,
                               sample_rate=sample_rate,
                               output_format="WAV",
                               vr_params= vr_params,
                               mdx_params=mdx_params)
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
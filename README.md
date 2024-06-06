# voice morph

变声工具，模型基于[Retrieval-based-Voice-Conversion-WebUI](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI)训练，通过web界面或命令行的方式交互。

改变的只是音色，而不是说话的习惯。


## 1 环境

### 1.1 base

1. 安装Pytorch及其核心依赖，若已安装则跳过。参考自: https://pytorch.org/get-started/locally/
2. 安装依赖包
    ```bash
    pip install -r requirements.txt
    ```
    安装fairseq
    ```bash
    git clone https://github.com/pytorch/fairseq
    cd fairseq
    pip install --editable ./
    ```


3. 下载模型，所以模型都被保存在models文件夹中
    下列模型放在models根目录

    * [rmvpe.pt](https://huggingface.co/lj1995/VoiceConversionWebUI/blob/main/rmvpe.pt)
    * [rmvpe.onnx](https://huggingface.co/lj1995/VoiceConversionWebUI/blob/main/rmvpe.onnx)
    * [hubert_base.pt](https://huggingface.co/lj1995/VoiceConversionWebUI/blob/main/hubert_base.pt)
    
    rvc变声模型则放到`./models/rvc`目录下

    目录结构：
    ```bash
    models
        ├──hubert_base.pt
        ├──rmvpe.onnx
        ├──rmvpe.pt
        ├──rvc/
        |   ├── kuon-bc-v1.pth
        |   └── kuon-bc-v1.index
    ```

4. 安装 ffmpeg
    * ubuntu
        ```bash
        sudo apt install ffmpeg
        ```
    * windows
        下载个[exe](https://ffmpeg.org/)后添加到环境变量中


### 1.2 清洁音频

想要好的效果则需要输入干净的音频，也就是仅仅只有说话的语音。可以通过[Ultimate Vocal Remover](https://ultimatevocalremover.com/)进行处理，也可以通过本仓库的工具，需要下列安装下列环境。

1. 安装软件包
```bash
# https://github.com/karaokenerds/python-audio-separator
pip install audio-separator[gpu]
# pip install audio-separator[cpu]
```
2. 下载模型

将模型文件夹放到`models/uvr/`中，目前我只使用了两个：
* [uvr模型](https://huggingface.co/lissette/uvr/tree/main/MDX-Net)
    * [UVR_MDXNET_Main.onnx](https://huggingface.co/lissette/uvr/blob/main/MDX-Net/UVR_MDXNET_Main.onnx)
    * [UVR-De-Echo-Aggressive.pth](https://huggingface.co/lissette/uvr/blob/main/VR%20Arch/UVR-De-Echo-Aggressive.pth)
 
目录结构:

```bash
models
    ├── uvr
        ├── UVR_MDXNET_Main.onnx
        ├── UVR-De-Echo-Aggressive.pth
```


## 2 使用

### 2.1 清洁音频

该功能用于人声伴奏分离

```bash
python uvr.py --model_name="UVR_MDXNET_Main.onnx" --audio="./temp/SPEAKER_03_750225_752706.wav"
```
python uvr.py --model_name="UVR-De-Echo-Aggressive.pth" --audio="./file/cn-test.wav"

参数：
* model_name 模型名
* audio 输入音频文件
* model_file_dir 存放模型文件夹
* output_dir 输出目录
* sample_rate 音频的采样率

如果在进行分离时报错，说内存不足，可以到`uvr.py`中修改`batch_size`参数往小调。

### 2.2 base 命令行

通过命令行使用基础变声服务

示例：
```bash
CUDA_VISIBLE_DEVICES=0
python .\base.py -i ./file/jp-test-1.wav -m "kuon-1000-(default40k)-w"
```

参数：
* -i 输入音频或者视频，可以是本地文件或者url链接
* -o 输出目录
* -p 变声音调值
* -m 模型名，如果使用，则会使用默认模型，默认模型在.env中修改

七海千秋原音：

[s1.webm](https://github.com/lissettecarlr/voice-morph/assets/16299917/08023e5a-bd3c-4656-8118-b751bdec6ab1)


久远模型输出：

[s2.webm](https://github.com/lissettecarlr/voice-morph/assets/16299917/3abbed0b-0d2f-45d3-82c1-968cd31f044c)


### 2.3 base web使用

通过web界面使用基础变声服务

```bash
streamlit run base_web.py  --server.port 1234 --server.maxUploadSize 1000
```

### 2.4 视频变声 命令行

需要安装基础环境和清洁音频环境

```bash
CUDA_VISIBLE_DEVICES=0
python video_morph.py -i ./file/test.mp4 -o ./temp/output -m "kuon-1000-(default40k)-w"
```
* -i 输入视频，也可以是url链接
* -o 输出目录（可选，默认temp/output文件夹）
* -p 变声音调值（可选，默认 0）
* -m 模型名（可选）默认模型在.env中修改


### 2.5 视频变声 web使用

```bash
streamlit run video_morph_web.py  --server.port 1234 --server.maxUploadSize 1000
```


### 2.6 歌曲变声 命令行

```bash
CUDA_VISIBLE_DEVICES=0
python .\music_morph.py -i ./file/jp-music.mp3 -m "kuon-1000-(default40k)-w" -o ./temp/output
```
import ffmpeg
import os

def concat_video_audio(video_path,audio_path,output_video_path="./final_video.mp4"):
    """
    通过ffmpeg合并视频和音频
    """
    try:
        if not os.path.exists(video_path):
            raise "{} not find".format(video_path)
        if not os.path.exists(audio_path):
            raise "{} not find".format(audio_path)
        if  os.path.exists(output_video_path):
            os.remove(output_video_path)
        video_stream = ffmpeg.input(video_path)
        audio_stream = ffmpeg.input(audio_path)
        (
            ffmpeg
            #.output(video_stream, audio_stream, output_video_path, codec="copy", **{'c:a': 'aac'})
            .output(video_stream.video, audio_stream.audio, output_video_path, vcodec='copy', acodec='aac')
            .run()
        )
    except Exception as e:
        raise e
    
def separate_audio(video_path,output_audio_path="./output_separate_audio.wav",ac=2,ar="44000"):
    """
    从视频中分离音频
    """
    if not os.path.exists(video_path):
        raise "{} not find".format(video_path)
    if  os.path.exists(output_audio_path):
        os.remove(output_audio_path)

    audio_stream = ffmpeg.input(video_path)
    (
        ffmpeg
        .output(audio_stream,output_audio_path,acodec="pcm_s16le", ac=ac, ar=ar)
    )


def extract_audio(video_path, output_audio_path):
    """
    从视频文件中提取音频并保存为wav。
    参数:
    video_path (str): 视频文件的路径。
    output_audio_path (str): 输出音频文件的路径。
    """
    if not os.path.exists(video_path):
        raise "{} not find".format(video_path)
    if  os.path.exists(output_audio_path):
        os.remove(output_audio_path)
    try:
        (
            ffmpeg
            .input(video_path)
            .output(output_audio_path, acodec='mp3', audio_bitrate='320k')
            .run(overwrite_output=True)
        )
    except ffmpeg.Error as e:
        raise e

def extract_audio_from_folder(folder_path):
    """
    提取指定文件夹内所有视频文件的音频，并保存在同一文件夹中。
    参数:
    folder_path (str): 包含视频文件的文件夹路径。
    """
    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        video_path = os.path.join(folder_path, filename)
        # 检查文件是否是视频文件，这里假设视频文件有以下扩展名
        if video_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            # 构造输出音频文件的路径
            output_audio_path = os.path.splitext(video_path)[0] + '.mp3'
            try:
                # 调用之前定义的函数来提取音频
                extract_audio(video_path, output_audio_path)
                print(f"Extracted audio from {video_path} to {output_audio_path}")
            except Exception as e:
                print(f"Failed to extract audio from {video_path}: {e}")

def concat_videos(video_list_file_path,output_video_path):
    """
    视频合并
    """
    if not os.path.exists(video_list_file_path):
        raise "{} not find".format(video_list_file_path)
    if  os.path.exists(output_video_path):
        os.remove(output_video_path)    
    (
        ffmpeg
        .input(video_list_file_path,format='concat', safe=0)
        .output(output_video_path, c='copy')
        .run(overwrite_output=True)
    )


def clear_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        os.remove(file_path)
    print("清空文件夹：{}".format(folder_path))



def image_to_video(image_path,duration,output_video_path):
    """
    通过图片生成视频
    """
    if not os.path.exists(image_path):
        raise "{} not find".format(image_path)    
    if  os.path.exists(output_video_path):
        os.remove(output_video_path)
    (
        ffmpeg
        .input(image_path, loop=1, t=duration, framerate=25) 
        .output(output_video_path, vcodec='libx264', pix_fmt='yuv420p')
        .run()
    )


def truncated_mean(data, trim_ratio):
    """
    计算截断平均值。
    :param data: 包含数据点的列表或数组。
    :param trim_ratio: 要从每端去除的数据的比例，例如0.1表示去除最高和最低的10%数据。
    :return: 截断平均值。
    """
    if trim_ratio < 0 or trim_ratio >= 0.5:
        raise ValueError("trim_ratio 必须在0到0.5之间（不包括0.5）")
    
    # 对数据进行排序
    sorted_data = sorted(data)
    # 计算要去除的数据点数量
    n = len(data)
    trim_count = int(n * trim_ratio)
    
    # 去除最高和最低的数据点
    trimmed_data = sorted_data[trim_count:n-trim_count]
    
    # 计算并返回截断平均值
    return sum(trimmed_data) / len(trimmed_data)


def add_suffix_to_filename(filepath, suffix):
    """
    给定一个文件路径和一个后缀，返回添加了后缀的新文件路径。
    
    参数:
    filepath (str): 原始文件路径。
    suffix (str): 要添加的后缀。
    
    返回:
    str: 添加了后缀的文件路径。
    """
    if suffix == "":
        return filepath
    # 分离文件的目录部分和文件名部分
    directory, filename = os.path.split(filepath)
    
    # 分离文件名和扩展名
    file_base, file_extension = os.path.splitext(filename)
    
    # 构造新的文件名
    new_filename = f"{file_base}_{suffix}{file_extension}"
    
    # 构造新的完整文件路径
    new_filepath = os.path.join(directory, new_filename)
    
    return new_filepath


def crop_video(input_file, output_file, width, height, x, y):
    """
    使用FFmpeg裁切视频画面

    参数:
    input_file (str): 输入视频文件路径
    output_file (str): 输出视频文件路径
    width (int): 裁切后的宽度
    height (int): 裁切后的高度
    x (int): 裁切区域的左上角x坐标
    y (int): 裁切区域的左上角y坐标
    """
    try:
        # 输入文件
        input_stream = ffmpeg.input(input_file)
        # 裁切视频流
        video_stream = input_stream.video.filter('crop', width, height, x, y)
        # 复制音频流
        audio_stream = input_stream.audio
        # 输出文件
        output_stream = ffmpeg.output(video_stream, audio_stream, output_file)
        # 运行FFmpeg命令
        ffmpeg.run(output_stream)
        print(f"视频已成功裁切并保存到 {output_file}")
    except ffmpeg.Error as e:
        print(f"视频裁切失败: {e.stderr.decode('utf8')}")


def loop_crop_video(source_folder, output_folder):
    # 循环裁切视频，通过draw_area先对视频进行画框，生成config文件，文件应该与视频在同级目录
    import json

    for root, dirs, files in os.walk(source_folder):
        # 检查当前目录下是否有 config.json 文件
        config_file = os.path.join(root, 'config.json')
        if os.path.isfile(config_file):
            # 读取 config.json 文件中的参数
            with open(config_file, 'r') as f:
                config = json.load(f)
                width = config.get('width')
                height = config.get('height')
                x = config.get('x')
                y = config.get('y')
                
            for file in files:
                if file.endswith(('.mp4', '.avi', '.mov', '.mkv')):  # 根据需要添加更多的视频格式
                    input_file = os.path.join(root, file)
                    # 构建输出文件路径
                    relative_path = os.path.relpath(root, source_folder)
                    output_dir = os.path.join(output_folder, relative_path)
                    os.makedirs(output_dir, exist_ok=True)
                    # 构建输出文件名
                    output_file = os.path.join(output_dir, f"{os.path.splitext(file)[0]}_cropped{os.path.splitext(file)[1]}")
                    # 判断输出文件是否存在
                    if os.path.exists(output_file):
                        print(f"Skipped {input_file}  (already exists)")
                        continue
                    # 调用裁剪函数
                    crop_video(input_file, output_file, width, height, x, y)
                    print(f"Processed {input_file} -> {output_file}")
        else:
            print(f"Skipped {root}  (no config.json)")


def is_same_file(file_path, new_file_path):
    """
    判断两个文件是否是同一个文件。
    
    参数:
    file_path (str): 第一个文件的路径。
    new_file_path (str): 第二个文件的路径。
    
    返回:
    bool: 如果两个文件是同一个文件，则返回True；否则返回False。
    """
    stat1 = os.stat(file_path)
    stat2 = os.stat(new_file_path)
    return (stat1.st_dev == stat2.st_dev) and (stat1.st_ino == stat2.st_ino)


def sanitize_filename(filename):
    """
    去除文件名中的非法字符，避免文件名无法保存
    """
    import re
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    filename = filename.replace('/', '').replace('\0', '')
    filename = filename.rstrip('. ')
    return filename

if __name__ == "__main__":
    #concat_videos("./temp/filelist.txt","./temp/1111.mp4")
    #extract_audio_from_folder(r"C:\Users\lisse\Desktop\徐老师")
    
    # 切割视频
    #crop_video(input_file="./temp/1.mp4", output_file="./temp/crop_output.mp4", width=980, height=720, x=0, y=0)

    # 循环切割视频
    # loop_crop_video(source_folder="./temp/source", output_folder="./temp/output")

    # 测试函数
    print(is_same_file("../file/cn-test-1.wav", "../cn-test-1.wav"))

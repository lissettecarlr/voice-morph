# 该代码用于批量转换


import os
from pathlib import Path
from extra.logger import setup_logger
log_file = 'batch.log' 
logger = setup_logger(log_file,"batch")
error_log_path = "./log/error.log"


def batch_video_morph_from_excel(excelfile,output_folder_path,model_name=None,pitch_shift=0):
    """"
    从excel表格中批量转换视频，只是个示例，不同表格自改
    excelfile: excel表格文件
    output_folder_path: 输出文件夹路径
    model_name: 模型名称
    pitch_shift: 音调调整
    """

    import pandas as pd
    from video_morph import VideoMorph

    df = pd.read_excel(excelfile)
    total_count = len(df)
    logger.info("总共有{}个视频".format(total_count))

    rvc_client = VideoMorph(model_name)

    # 循环表格，通过表格中的链接下载视频，然后再根据表格信息分类保存
    # 示例 : 学段/科目/教材版本/教材/视频名称/视频地址
 
    for index,row in df.iterrows():
        try:
            play_url = row["视频地址"]

            # 从链接中分离个字符用于当视频民
            id_with_extension = os.path.basename(play_url)
            id, extension = os.path.splitext(id_with_extension)

            logger.info("正在处理：{} / {}，视频url：{}".format(index+1,total_count,id))

            # 读取这些用于当作保存路径
            subject = row['科目']
            grade = row['学段']
            book_version = row['教材版本']
            name = row['视频名称']

            # 最终输出文件的名称
            from extra.utils import sanitize_filename
            output_name = sanitize_filename(name) + "_" + id + "_rvc.mp4" 
            # 最终输出文件的路径
            folder_path = Path(output_folder_path) / grade / subject / book_version
            folder_path.mkdir(parents=True, exist_ok=True)  
            output_path = os.path.join(folder_path,output_name)
 
        except Exception as e:
            logger.error("处理失败：{} / {}，原因：表格读取错误 {}".format(index+1,total_count, e))
            with open(error_log_path, "a") as file:
                file.write(f"{index}\n")
            continue
 
        # 判断该文件是否存在
        if os.path.exists(output_path):
            logger.info("文件已存在，跳过:{}".format(output_path))
            continue
        else:
            try:
                rvc_client.run(input_file=play_url, output_folder_path=output_path,pitch_shift=pitch_shift)
            except Exception as e:
                logger.error("处理失败：{} / {}，原因：视频处理失败 {}".format(index+1,total_count, e))
                with open(error_log_path, "a") as file:
                    file.write(f"{index}\n")  
                continue
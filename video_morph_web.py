import streamlit as st
import os
from dotenv import load_dotenv
from base import RvcBase
from uvr import  UvrClient

# 临时文件存放地址
TEMP = "./temp"

def data_init():

    # 保存上传视频
    if "temp_input_video" not in st.session_state:
        st.session_state['temp_input_video'] = None
    # 上传视频提取的音轨
    if "temp_audio_path" not in st.session_state:
        st.session_state['temp_audio_path'] = None
    # 进行分离后的音频    
    if "temp_separator_audio_path" not in st.session_state:
        st.session_state['temp_separator_audio_path'] = None

    # rvc模型列表
    if  "rvc_client" not in st.session_state:
        st.session_state['rvc_client'] = None  
    if "rvc_model_list" not in st.session_state:
        st.session_state['rvc_model_list'] = []
        for root,dirs,files in os.walk(os.getenv('weight_root')):
            for file in files:
                if file.endswith(".pth"):
                    st.session_state['rvc_model_list'].append(os.path.splitext(file)[0])

    # UVR模型
    if  "uvr_1" not in st.session_state:
        st.session_state['uvr_1'] = None
    if st.session_state.uvr_1 is None:
        uvr_1_model_name = os.getenv('uvr_1_model_name')
        print("加载模型：{}".format(uvr_1_model_name))   
        st.session_state.uvr_1 = UvrClient(model_name=uvr_1_model_name)

    # if "uvr_2" not in st.session_state:
    #     st.session_state['uvr_2'] = None
    # if st.session_state.uvr_2 is None:
    #     uvr_2_model_name = os.getenv('uvr_2_model_name')
    #     print("加载模型：{}".format(uvr_2_model_name))
    #     st.session_state.uvr_2 = uvr_client(model_name=uvr_2_model_name)


    # rvc模型，默认加载首个
    if "rvc_model_name" not in st.session_state:
        st.session_state['rvc_model_name'] = st.session_state['rvc_model_list'][0]
    if st.session_state.rvc_client is None:  
        print("加载模型：{}".format(st.session_state['rvc_model_name']))
        st.session_state.rvc_client = RvcBase(st.session_state.rvc_model_name)
        
    # 变调值
    if "f0_up_key" not in st.session_state:
        st.session_state['f0_up_key'] = None  

    
    if "final_audio_path" not in st.session_state:
        st.session_state['final_audio_path'] = None

def web_page():
    st.title("视频变声")
    data_init()
 
    st.markdown("------")
    if st.button("清空缓存（该按钮将删除临时文件）"):
        from extra.utils import clear_folder
        clear_folder(TEMP)

    input_file = st.file_uploader("上传视频：", type=["mp4", "avi", "mov", "mkv"])
    if input_file is not None:
        # 上传视频临时保存地址
        temp_input_video = os.path.join(
            TEMP,
            os.path.splitext(os.path.basename(input_file.name))[0]+"_temp.mp4"
        )
        if not os.path.exists(temp_input_video):      
            with open(temp_input_video, "wb") as f:
                f.write(input_file.read())
        else:
            print("文件:{} 已存在，无需创建".format(temp_input_video))
        st.session_state.temp_input_video = temp_input_video

    model_name = st.selectbox('模型选择', st.session_state['rvc_model_list'])
    if  st.session_state.rvc_model_name != model_name:
        st.session_state.rvc_client.model_change(model_name)
        st.session_state.rvc_model_name = model_name
        st.write(f'模型 {model_name} 加载成功!')

    st.session_state.f0_up_key = st.number_input("音调，输入音频的声调高于声音模型，则下调，反之则上调(整数, 半音数量, 升八度12降八度-12)", value=0)
    st.markdown("------------")


    if st.button("开始转换"):
        if input_file is None:
            st.warning("请先上传音频")
            st.stop()

        st.session_state.final_audio_path = None

        # 提取音频文件
        st.session_state.temp_audio_path = os.path.join(
           TEMP, 
           os.path.splitext(os.path.basename(input_file.name))[0]+".wav"
        )
        if os.path.exists(st.session_state.temp_audio_path):
            os.remove(st.session_state.temp_audio_path)

        with st.spinner('音频提取中'):
            try:
                from extra.utils import extract_audio
                extract_audio(
                    temp_input_video,st.session_state.temp_audio_path
                ) 
            except Exception as e: 
                st.error(e)

        if st.session_state.temp_audio_path is not None and input_file is not None:
            st.write("提取音频：")
            st.audio(st.session_state.temp_audio_path, format='audio/wav', start_time=0)
        
        with st.spinner('音频清洁中'):
            instrumental_1,vocals_1=st.session_state.uvr_1.infer(st.session_state.temp_audio_path)
            st.session_state.uvr_1.change_model(os.getenv('uvr_2_model_name'))
            no_echo,instrumental =st.session_state.uvr_1.infer(os.path.join(TEMP,vocals_1))
            st.session_state.temp_separator_audio_path = os.path.join(TEMP,no_echo)

        if st.session_state.temp_separator_audio_path is not None:
            st.write("清洁音频：")
            st.audio(st.session_state.temp_separator_audio_path, format='audio/wav', start_time=0)           


        with st.spinner('变声处理中'):    
            st.session_state.final_audio_path = st.session_state.rvc_client.run(
                input_audio_path = st.session_state.temp_separator_audio_path,
                output_folder_path = TEMP,
                pitch_shift = st.session_state.f0_up_key
            )

        if st.session_state.final_audio_path is not None:
            st.write("变声音频：")
            st.audio(st.session_state.final_audio_path, format='audio/wav', start_time=0)           

        with st.spinner('视频生成'): 
            final_video_path = os.path.join(
                TEMP, 
                os.path.splitext(os.path.basename(input_file.name))[0]+"_final.mp4"
            )
            if os.path.exists(final_video_path):
                os.remove(final_video_path)

            from extra.utils import concat_video_audio
            concat_video_audio(st.session_state.temp_input_video,
                                st.session_state.final_audio_path,
                                final_video_path)
            st.write("最终视频：")
            if os.path.exists(final_video_path):
                video_bytes = open(final_video_path, 'rb').read()
                st.video(video_bytes)

if __name__ == "__main__":
    if not os.path.exists(TEMP):
        os.makedirs(TEMP)
    load_dotenv()
    web_page()
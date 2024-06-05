import streamlit as st
import os
from dotenv import load_dotenv
from base import RvcBase

# 临时文件存放地址
TEMP = "./temp"

def data_init():

    # 上传视频提取的音轨
    if "temp_input_audio" not in st.session_state:
        st.session_state['temp_input_audio'] = None

    # rvc模型
    if  "rvc_client" not in st.session_state:
        st.session_state['rvc_client'] = None  

    if "rvc_model_list" not in st.session_state:
        st.session_state['rvc_model_list'] = []
        for root,dirs,files in os.walk(os.getenv('weight_root')):
            for file in files:
                if file.endswith(".pth"):
                    st.session_state['rvc_model_list'].append(os.path.splitext(file)[0])

    if "rvc_model_name" not in st.session_state:
        st.session_state['rvc_model_name'] = st.session_state['rvc_model_list'][0]

    if st.session_state.rvc_client is None:  
        st.session_state.rvc_client = RvcBase(st.session_state.rvc_model_name)
        
    # 变调值
    if "f0_up_key" not in st.session_state:
        st.session_state['f0_up_key'] = None  

    if "final_audio_path" not in st.session_state:
        st.session_state['final_audio_path'] = None

def web_page():
    st.title("变声模型测试")
    data_init()
 
    st.markdown("------")
    if st.button("清空缓存（该按钮将删除临时文件）"):
        from extra.utils import clear_folder
        clear_folder(os.getenv('temp_files'))

    input_file = st.file_uploader("上传干音频：", type=["wav", "mp3"])

    if input_file is not None:
        # 上传音频临时保存地址
        temp_input_audio = os.path.join(os.getenv('temp_files'),input_file.name)
        if not os.path.exists(temp_input_audio):      
            with open(temp_input_audio, "wb") as f:
                f.write(input_file.read())
        else:
            print("文件:{} 已存在，无需创建".format(temp_input_audio))

        st.session_state.temp_input_audio = temp_input_audio

    if st.session_state.temp_input_audio is not None:
        st.write("输入音频：")
        st.audio(st.session_state.temp_input_audio, format='audio/wav', start_time=0)          
      

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

        with st.spinner('变声处理中'):    

            st.session_state.final_audio_path = st.session_state.rvc_client.run(
                input_audio_path = temp_input_audio,
                output_folder_path = os.getenv('temp_files'),
                pitch_shift = st.session_state.f0_up_key
            )

    if st.session_state.final_audio_path is not None:
        st.write("变声音频：")
        st.audio(st.session_state.final_audio_path, format='audio/wav', start_time=0)          


if __name__ == "__main__":
    load_dotenv()
    if not os.path.exists(os.getenv('temp_files')):
        os.makedirs(os.getenv('temp_files'))
    web_page()
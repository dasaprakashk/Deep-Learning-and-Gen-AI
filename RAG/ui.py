import streamlit as st
from streamlit_chat import message
import requests
import time
from streamlit_option_menu import option_menu

# Setting page title and header
st.set_page_config(page_title="ChatPDF", page_icon=":robot_face:")
# horizontal Menu
selected2 = option_menu(None, ["Home", "Upload", "Tasks", 'Settings'], 
    icons=['house', 'cloud-upload', "list-task", 'gear'], 
    menu_icon="cast", default_index=0, orientation="horizontal")
selected2
st.markdown("<h1 style='text-align: center;'>ChatPDF - Chat with any PDF!!</h1>", unsafe_allow_html=True)

with st.sidebar:
    repo_name = st.sidebar.radio("Choose a repo:", ("Amazon Prospectus", "Contract", "SmartHub", "SBC")) # "Contract", "SmartHub", "Receipt", "Invoice"
    embeddings = st.sidebar.radio("Choose an embedding:", ("HuggingFace", "OpenAI Ada"))
    models = st.sidebar.radio("Choose a model:", ("GPT 3.5 Turbo", "flan-t5-xl", 'Falcon-7b'))
    counter_placeholder = st.sidebar.empty()
    clear_button = st.sidebar.button("Clear Conversation", key="clear")

if repo_name == "Amazon Prospectus":
    repo = "amazon"
elif repo_name == "Contract":
    repo = "contractorderform"
elif repo_name == "SmartHub":
    repo = "smarthub"
elif repo_name == "sbc":
    repo = "sbc"
#elif model_name == "Invoice":
#    model = "invoice"

if embeddings == "HuggingFace":
    embedding = "HF"
elif embeddings == "OpenAI Ada":
    embedding = "ADA"

# Initialise session state variables
if f'{repo}_generated' not in st.session_state:
    st.session_state[f'{repo}_generated'] = []
if f'{repo}_past' not in st.session_state:
    st.session_state[f'{repo}_past'] = []
if f'{repo}_messages' not in st.session_state:
    st.session_state[f'{repo}_messages'] = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
if f'{repo}_model_name' not in st.session_state:
    st.session_state[f'{repo}_model_name'] = []

# reset everything
if clear_button:
    st.session_state[f'{repo}_generated'] = []
    st.session_state[f'{repo}_past'] = []
    st.session_state[f'{repo}_messages'] = [
        {"role": "system", "content": "ChatPDF"}
    ]
    st.session_state['model_name'] = repo_name

# generate a response
def generate_response(prompt, repo, embedding):
    st.session_state[f'{repo}_messages'].append({"role": "user", "content": prompt})
    data = {"query":prompt, "repo":repo, "embedding":embedding}
    response = requests.post("http://127.0.0.1:5000/generate", json=data)
    st.session_state[f'{repo}_messages'].append({"role": "assistant", "content": response.text})

    # print(st.session_state['messages'])
    return response.text

# container for chat history
response_container = st.container()
# container for text box
container = st.container()

with container:
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_area("Prompt:", key='input', height=100)
        submit_button = st.form_submit_button(label='Send')

    if submit_button and user_input:
        output = generate_response(user_input, repo, embedding)
        st.session_state[f'{repo}_past'].append(user_input)
        st.session_state[f'{repo}_generated'].append(output)
        st.session_state[f'{repo}_model_name'].append(repo_name)
        
    if st.session_state[f'{repo}_generated']:
        with response_container:
            for i in range(len(st.session_state[f'{repo}_generated'])):
                message(st.session_state[f'{repo}_past'][i], is_user=True, key=str(i) + '_user')
                message(st.session_state[f'{repo}_generated'][i], key=str(i))
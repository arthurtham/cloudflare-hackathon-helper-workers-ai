# Heavily based on https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps

import json
import uwuify
import random

import streamlit as st
from cloudflare import Cloudflare


st.title(("HackUWU: Workers Edition"))
st.subheader(uwuify.uwu("For the people, by the people"))
st.markdown("(For legal reasons, this is a joke)")

# Set Cloudflare API key from Streamlit secrets
client = Cloudflare(api_token=st.secrets["CLOUDFLARE_API_TOKEN"])

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
if len(st.session_state.messages) > 0:
    with st.chat_message("assistant", avatar="🦖"):
        st.write(uwuify.uwu("Welcome back! Here's what you told my companion dinosaur previously."))
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Welcome message
with st.chat_message("assistant", avatar="🦖"):
    st.markdown(("**RAWR! Ready for action!**"))
    st.write(uwuify.uwu("It is time for this dinosaur to answer all your questions, uwu!"))

# Accept user input
if prompt := st.chat_input(uwuify.uwu("Rawr! Please ask me something, master!")):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant", avatar="🦖"):
        st.write(uwuify.uwu(random.choice([
            "I am thinking about my historical response, uwu...",
            "What a great statement you just made! I am thinking, uwu...",
            "Wow! Great thought. Let me work for a response at ancient pace, uwu..."]
        )))
        with client.workers.ai.with_streaming_response.run(
            account_id=st.secrets["CLOUDFLARE_ACCOUNT_ID"],
            model_name="@cf/meta/llama-3-8b-instruct",
            messages=[
                {"role": m["role"], "content": m["content"], "avatar": "🦖"}
                for m in st.session_state.messages
            ],
            stream=True,
        ) as response:
            # The response is an EventSource object that looks like so
            # data: {"response": "Hello "}
            # data: {"response": ", "}
            # data: {"response": "World!"}
            # data: [DONE]
            # Create a token iterator
            def iter_tokens(r):
                flags = uwuify.SMILEY | uwuify.YU
                for line in r.iter_lines():
                    if line.startswith("data: ") and not line.endswith("[DONE]"):
                        entry = json.loads(line.replace("data: ", ""))
                        yield uwuify.uwu(entry["response"], flags=flags)

            completion = st.write_stream(iter_tokens(response))
    st.session_state.messages.append({"role": "assistant", "content": completion})
    # with st.chat_message("assistant", avatar="🦖"):
    #     st.write(uwuify.uwu("Phew! I'm tired already."))

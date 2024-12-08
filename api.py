import streamlit as st
import pandas as pd
import openai

openai.api_key = st.sidebar.text_input("Enter your OpenAI API Key", type="password")

def get_word_details(word):
    if not openai.api_key:
        st.error("Please enter your API key in the sidebar.")
        return None
    try:
        with st.spinner("Fetching word details... Please wait."):
            response = openai.chat.completions.create(
                model="text-davinci-003",
                prompt=f"Provide detailed meanings, synonyms, and examples of usage for the word '{word}'.",
                max_tokens=500,
                temperature=0.7,
            )
        result_text = response.choices[0].text.strip()
        meanings = result_text.split("Meanings:")[1].split("Synonyms:")[0].strip()
        synonyms = result_text.split("Synonyms:")[1].split("Examples:")[0].strip()
        examples = result_text.split("Examples:")[1].strip()
        return pd.DataFrame([{"Word": word, "Meanings": meanings, "Synonyms": synonyms, "Examples": examples}]), meanings, synonyms.split(", "), examples
    except openai.error.OpenAIError as e:
        st.error(f"OpenAI error: {e}")
        return None

def get_related_words(word):
    if not openai.api_key:
        st.error("Please enter your API key in the sidebar.")
        return None
    try:
        with st.spinner("Fetching related words... Please wait."):
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=f"List words that are commonly used in the same context as '{word}' (not synonyms).",
                max_tokens=100,
                temperature=0.7,
            )
        related_words = response.choices[0].text.strip()
        return related_words
    except openai.error.OpenAIError as e:
        st.error(f"OpenAI error: {e}")
        return None

st.title("Find Word Meaning, Synonyms, and Related Words")

word = st.text_input("Enter a word:", placeholder="Type a word to explore its details")

if st.button("Find Meaning and Synonyms"):
    if word:
        result = get_word_details(word)
        if result:
            result_df, meanings, synonyms_list, examples = result
            st.markdown("### Word Details")
            st.write(result_df)
        else:
            st.warning("Could not fetch word details. Try another word.")
    else:
        st.warning("Please enter a word!")

if st.button("Show Related Words"):
    if word:
        related_words = get_related_words(word)
        if related_words:
            st.markdown(f"### Words in the same category as *{word}*:")
            st.write(related_words)
        else:
            st.warning("No related words found.")
    else:
        st.warning("Please enter a word!")

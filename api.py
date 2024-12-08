import openai
import streamlit as st
import pandas as pd
import json

st.title("Word Meaning and Synonyms Finder")
api_key = st.sidebar.text_input("Enter your OpenAI API key:", type="password")
if api_key:
    openai.api_key = api_key
word = st.text_input("What word are you looking for?")

def get_word_details(word):
    if not api_key:
        st.error("Please enter your API key in the sidebar.")
        return None
    if not word.strip():
        st.warning("Enter a word to search for its meaning.")
        return None
    try:
        st.write(f"Searching for meaning of: {word}")
        prompt = (
            f"Provide the meaning(s) of '{word}' and their corresponding synonyms, "
            f"part of speech, and an example sentence for each meaning in a JSON format like this:\n"
            f"{{'meanings': [\n"
            f"  {{'meaning': 'meaning1', 'synonyms': ['synonym1', 'synonym2'], 'part_of_speech': 'noun/verb/etc.', 'example': 'example sentence1'}},\n"
            f"  {{'meaning': 'meaning2', 'synonyms': ['synonym3', 'synonym4'], 'part_of_speech': 'noun/verb/etc.', 'example': 'example sentence2'}}\n"
            f"]}}"
        )
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
        )
        content = response.choices[0].message.content.strip()

        try:
            data = json.loads(content)
            meanings = data.get("meanings", [])
            if not meanings:
                st.warning("No meanings found in the API response. Please try another word.")
                return None
            rows = []
            for meaning_data in meanings:
                meaning = meaning_data.get("meaning", "N/A")
                synonyms = meaning_data.get("synonyms", [])
                part_of_speech = meaning_data.get("part_of_speech", "N/A")
                example = meaning_data.get("example", "N/A")
                rows.append({
                    "Word": word,
                    "Part of Speech": part_of_speech,
                    "Meaning": meaning,
                    "Synonyms": ", ".join(synonyms) if synonyms else "N/A",
                    "Example": example
                })

            df = pd.DataFrame(rows)
            return df
        except json.JSONDecodeError as e:
            st.error(f"Error decoding JSON response: {e}. Content: {content}")
            return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None

if st.button("Find Meaning and Synonyms"):
    if word:
        result_df = get_word_details(word)
        if result_df is not None:
            st.markdown(f"### Details for *{word}*:") 
            st.dataframe(result_df)
    else:
        st.warning("Please enter a word!")

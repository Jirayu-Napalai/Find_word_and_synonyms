import openai
import streamlit as st
import pandas as pd

st.title("Word Meaning and Synonyms Finder")

api_key = st.sidebar.text_input("Enter your OpenAI API key:", type="password")
if api_key:
    openai.api_key = api_key

word = st.text_input("What word are you looking for?")

def get_word_details(word):
    if not api_key:
        st.error("Please enter your API key in the sidebar.")
        return None

    if not word.strip().isalpha():
        st.warning("Enter a valid word containing only alphabets.")
        return None

    try:
        with st.spinner("Fetching details... Please wait."):
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an assistant specialized in language analysis."},
                    {"role": "user",
                     "content": f"Provide detailed information about the word '{word}' in this exact structured format:\n"
                                "### Meaning:\n"
                                "[Meaning]\n"
                                "### Part of Speech:\n"
                                "[Part of speech for this meaning]\n"
                                "### Synonyms:\n"
                                "[Comma-separated list of synonyms]\n"
                                "### Example:\n"
                                "[Example sentence]"}
                ],
                max_tokens=1000,
                temperature=0.7
            )

        content = response.choices[0].message.content.strip()
        parts = content.split("###")[1:]
        entries = []
        entry = {}

        for part in parts:
            if part.startswith("Meaning:"):
                if entry:
                    entries.append(entry)
                entry = {"Meaning": part.split(":", 1)[1].strip()}
            elif part.startswith("Part of Speech:"):
                entry["Part of Speech"] = part.split(":", 1)[1].strip()
            elif part.startswith("Synonyms:"):
                entry["Synonyms"] = part.split(":", 1)[1].strip()
            elif part.startswith("Example:"):
                entry["Example"] = part.split(":", 1)[1].strip()

        if entry:
            entries.append(entry)

        df = pd.DataFrame(entries)
        return df

    except openai.error.AuthenticationError:
        st.error("Authentication error: Please check your API key.")
    except openai.error.RateLimitError:
        st.error("Rate limit exceeded: Too many requests. Try again later.")
    except openai.error.OpenAIError as e:
        st.error(f"OpenAI error: {e}")
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

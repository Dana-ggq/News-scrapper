#TO RUN: streamlit run app_scrapper.py
import streamlit as st
from pygooglenews import GoogleNews
import pandas as pd
from textblob import TextBlob
import numpy as np

# Crearea obiectului GoogleNews
gn = GoogleNews()

# Funcția pentru a obține știrile în funcție de căutare, titlu și interval de timp
def get_news(search_text, search_title, search_when):
    if not search_title or not search_title.strip() or not any(char.isalpha() for char in search_title):
        return gn.search(search_text, when=search_when)
    else:
        search_title_term = 'intitle:'+ search_title
        return gn.search(search_title_term, when=search_when)

# Funcția pentru a obține detaliile știrilor (titlu, link, dată publicare)
def get_details(search):
    news = []
    articles = search['entries']
    for i in articles:
        article = {'title': i.title, 'link': i.link, "published": i.published}
        news.append(article)
    return news

#POZITIVE, NEGATIVE, NEUTRAL
def sentiment(text):
  blob=TextBlob(text)
  return blob.sentiment.polarity 

def subjectivity(text):
  blob=TextBlob(text)
  return blob.sentiment.subjectivity 

def main():
    st.title("News Search")

    # Interfețe pentru introducerea de către utilizator a textului de căutare, titlului și intervalului de timp
    search_text = st.text_input("Search by content:")

    search_title = st.text_input("Search by title:")

    search_when = st.selectbox("Select time period:", ("Last hour", "Last 12 hours", "Last day", "Last 2 days", "Last 3 days"))
    

    # Butonul pentru a iniția căutarea
    search_button = st.button("Search for news")

    if search_button:
        # Verificăm dacă cel puțin unul dintre câmpurile de căutare a fost completat
        if search_text and search_title:
            st.warning("Fill in just one of the search terms (content or title).")
        elif search_text or search_title:
            # Maparea opțiunilor selectate la string-urile așteptate de funcția de căutare
            try:
                when_mapping = {"Last hour": "1h", "Last day": "24h", "Last 12 hours": "12h", "Last 2 days": "48h", "Last 3 days": "72h"}
                search_when_code = when_mapping.get(search_when)

                # Căutarea știrilor folosind parametrii specificați
                search_results = get_news(search_text, search_title, search_when_code)

                # Extragerea detaliilor știrilor și adăugarea sentimentului și subiectivității
                data = get_details(search_results)
                df = pd.DataFrame(data)
                df['Sentiment'] = df['title'].apply(sentiment)
                df['Subjectivity'] = df['title'].apply(subjectivity)

                # Transformarea sentimentului în clasă 
                df['Sentiment'] = np.where(df['Sentiment'] < 0, "negative",
                                                np.where(df['Sentiment'] > 0, "positive", "neutral"))

                # Transformarea subiectivității în clasă
                df['Subjectivity'] = np.where(df['Subjectivity'] == 0, "very objective",
                                                    np.where(df['Subjectivity'] == 1, "very subjective",
                                                            np.where(df['Subjectivity'] < 0.5, "objective",
                                                                    np.where(df['Subjectivity'] > 0.5, "subjective",
                                                                                "neutral"))))
                # Afisarea tabelului cu rezultate
                st.dataframe(df)
            except:
                st.warning("There are no news for your search.")
        else:
            st.warning("Fill in one of the search terms (content or title).")

if __name__ == "__main__":
    main()

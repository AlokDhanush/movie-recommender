import streamlit as st 
import pickle 
import pandas as pd 
import requests
from dotenv import load_dotenv
import os
import gdown
import time

API_KEY = st.secrets["TMDB_API_KEY"]

def fetch_poster(movie_id):
    try:
        response = requests.get(
            f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US",
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            poster_url = f"https://image.tmdb.org/t/p/w500/{poster_path}"
            return poster_url
        else:
            st.warning(f"No poster found for movie ID {movie_id}")
            return "https://via.placeholder.com/300x450?text=No+Image"
    except Exception as e:
        st.error(f"Failed to fetch poster for movie ID {movie_id}: {e}")
        return "https://via.placeholder.com/300x450?text=Error"
        
def recommend(movie):
    movie_index = movies_dict[movies_dict['title'] == movie].index[0]
    distances = similarity[movie_index] 
    movies_list = list(sorted(enumerate(distances), reverse=True, key=lambda x: x[1]))[1:6]

    similar_movies = []
    similar_movies_posters = []
    for movie in movies_list:
        similar_movies.append(movies_dict.iloc[movie[0]].title)
        poster_url = fetch_poster(movies_dict.iloc[movie[0]].movie_id)
        similar_movies_posters.append(poster_url)

    return similar_movies, similar_movies_posters


movies_dict = pickle.load(open('movies_dict.pkl', 'rb')) 
movies_dict = pd.DataFrame(movies_dict) 
 
# Download large model file from Google Drive
FILE_ID = "1qoQaL5pWLwW6SfUGARrBh8TYPrHDvfwz"  
OUTPUT_PATH = "similarity.pkl"

@st.cache_data
def download_model():
    if not os.path.exists(OUTPUT_PATH):
        url = f"https://drive.google.com/uc?id={FILE_ID}"
        with st.spinner("Downloading similarity model..."):
            gdown.download(url, OUTPUT_PATH, quiet=False)
    return OUTPUT_PATH

model_path = download_model()

# Load similarity matrix
similarity = pickle.load(open(model_path, 'rb'))


st.title("🎬 Movie Recommender System") 

selected_movie_name = st.selectbox(
    'Select a movie name for similar recommendations:',
    movies_dict['title'].values
)

if selected_movie_name: 
    names, poster_urls = recommend(selected_movie_name)

    if poster_urls:
        cols = st.columns(len(poster_urls))
        for i, col in enumerate(cols):
            with col:
                st.markdown(
                    f"""
                    <figure style="text-align: center; margin: 0;">
                        <img src="{poster_urls[i]}" style="height:260px; border-radius:10px;" />
                        <figcaption style="font-size: 13px;">{names[i]}</figcaption>
                    </figure>
                    """,
                    unsafe_allow_html=True
                )
    else:
        st.warning("No similar movies found.")



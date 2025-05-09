import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import seaborn as sns
import functions
import auth
import time
from datetime import datetime
import os

# Set page configuration
st.set_page_config(
    page_title="WhatsApp Chat Analyzers",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
auth.init_session_state()

# Apply custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #25D366;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #128C7E;
        margin-bottom: 1rem;
    }
    .card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stat-number {
        font-size: 2rem;
        font-weight: bold;
        color: #075E54;
    }
    .stat-label {
        color: #128C7E;
        font-weight: bold;
    }
    .sidebar-content {
        padding: 20px 0;
    }
    .footer {
        text-align: center;
        margin-top: 50px;
        padding: 20px;
        font-size: 0.8rem;
        color: #666;
    }
    .user-info {
        padding: 10px;
        background-color: #128C7E; 
        color: white;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .login-container {
        max-width: 500px;
        margin: 0 auto;
    }
    .btn-custom {
        background-color: #25D366;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: bold;
    }
    .section-divider {
        margin: 40px 0;
        border-top: 1px solid #ddd;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar user section
with st.sidebar:
    st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    
    # User Authentication Section
    if not st.session_state.logged_in:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/WhatsApp.svg/1200px-WhatsApp.svg.png", width=100)
        st.markdown("###  WhatsApp Analyzer")
        
        # Create tabs for login and signup
        login_tab, signup_tab = st.tabs(["Login", "Sign Up"])        
        with login_tab:
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit_login = st.form_submit_button("Login")
                
                if submit_login:
                    if username and password:
                        success, message = auth.authenticate(username, password)
                        if success:
                            auth.login_user(username)
                            st.success(message)
                            st.experimental_rerun()
                        else:
                            st.error(message)
                    else:
                        st.warning("Please enter both username and password")
        
        with signup_tab:
            with st.form("signup_form"):
                new_username = st.text_input("Choose Username")
                new_email = st.text_input("Email")
                new_password = st.text_input("Choose Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                submit_signup = st.form_submit_button("Create Account")
                
                if submit_signup:
                    if new_username and new_email and new_password and confirm_password:
                        if new_password != confirm_password:
                            st.error("Passwords do not match")
                        else:
                            success, message = auth.create_user(new_username, new_password, new_email)
                            if success:
                                st.success(message)
                                st.info("Please login with your new account")
                            else:
                                st.error(message)
                    else:
                        st.warning("Please fill all fields")
        
        
    
    # Logged in user section
    else:
        # User info card
        st.markdown(f"""
        <div class="user-info">
            <h3>👤 {st.session_state.username}</h3>
            <p>Session duration: {auth.get_session_duration()} min</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.username != "Guest":
            # Show user history
            with st.expander("Your Analysis History"):
                history = auth.get_user_history(st.session_state.username)
                if history:
                    for i, entry in enumerate(reversed(history)):
                        if i >= 5:  # Show only last 5 analyses
                            break
                        st.write(f"📊 {entry['file_name']} - {entry['timestamp'].strftime('%d %b, %H:%M')}")
                else:
                    st.write("No analysis history yet")
        
        # Logout button
        if st.button("Logout"):
            auth.logout_user()
            st.experimental_rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Only show analysis options if logged in
    if st.session_state.logged_in:
        st.markdown("### Analysis Options")
        
        # This will be populated later when a file is uploaded
        if 'users' in st.session_state:
            users = st.session_state.users
            users_s = st.selectbox("Select User to View Analysis", users)
            
            if st.button("Show Analysis"):
                st.session_state.selected_user = users_s
                
                # Record this analysis in user history
                if st.session_state.username != "Guest" and 'file_name' in st.session_state:
                    auth.record_analysis(
                        st.session_state.username, 
                        st.session_state.file_name, 
                        f"Analysis for {users_s}"
                    )

# Main page content
if st.session_state.logged_in:
    # Page Header
    st.markdown('<h1 class="main-header">WhatsApp Chat Analyzer By Bhoomika</h1>', unsafe_allow_html=True)
    
    # Introduction section in a card
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("""
    ### 📊 Analyze Your WhatsApp Chats with Ease
    
    This tool helps you analyze your WhatsApp conversations to uncover interesting patterns and statistics. 
    Export your chat (without media) from WhatsApp and upload the text file here to get started.
    
    **Features:**
    - Message frequency analysis
    - Emoji usage statistics
    - Most common words
    - Activity patterns by day and time
    - Monthly and daily timeline visualization
    - Word cloud generation
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # File upload section
    st.markdown('<h2 class="sub-header">Upload Your Chat File</h2>', unsafe_allow_html=True)
    
    file = st.file_uploader("Choose WhatsApp chat export file (.txt)", type=["txt"])
    
    # Process the uploaded file
    if file:
        st.session_state.file_name = file.name
        
        with st.spinner('Processing your chat file...'):
            try:
                df = functions.generateDataFrame(file)
                
                # Storing users in session state for sidebar
                users = functions.getUsers(df)
                st.session_state.users = users
                
                # Date format selection with improved UI
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.subheader("Configure Chat Settings")
                dayfirst = st.radio(
                    "Select Date Format in the chat file:",
                    ('dd-mm-yy', 'mm-dd-yy'),
                    horizontal=True
                )
                st.markdown('</div>', unsafe_allow_html=True)
                
                if dayfirst == 'dd-mm-yy':
                    dayfirst = True
                else:
                    dayfirst = False
                
                # Check if user has selected analysis in sidebar
                if 'selected_user' in st.session_state:
                    selected_user = st.session_state.selected_user
                    
                    st.markdown(f'<h2 class="sub-header">Analysis Results for: {selected_user}</h2>', unsafe_allow_html=True)
                    
                    df = functions.PreProcess(df, dayfirst)
                    if selected_user != "Everyone":
                        df = df[df['User'] == selected_user]
                    
                    # Get statistics
                    df, media_cnt, deleted_msgs_cnt, links_cnt, word_count, msg_count = functions.getStats(df)
                    
                    # Display chat statistics in an attractive layout
                    st.markdown('<h2 class="sub-header">Chat Overview</h2>', unsafe_allow_html=True)
                    
                    col1, col2, col3, col4, col5 = st.columns(5)
                    
                    with col1:
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.markdown('<p class="stat-label">Total Messages</p>', unsafe_allow_html=True)
                        st.markdown(f'<p class="stat-number">{msg_count}</p>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.markdown('<p class="stat-label">Total Words</p>', unsafe_allow_html=True)
                        st.markdown(f'<p class="stat-number">{word_count}</p>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.markdown('<p class="stat-label">Media Shared</p>', unsafe_allow_html=True)
                        st.markdown(f'<p class="stat-number">{media_cnt}</p>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col4:
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.markdown('<p class="stat-label">Links Shared</p>', unsafe_allow_html=True)
                        st.markdown(f'<p class="stat-number">{links_cnt}</p>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col5:
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.markdown('<p class="stat-label">Deleted Messages</p>', unsafe_allow_html=True)
                        st.markdown(f'<p class="stat-number">{deleted_msgs_cnt}</p>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Add a divider
                    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                    
                    # User Activity Count (only for Everyone)
                    if selected_user == 'Everyone':
                        st.markdown('<h2 class="sub-header">User Activity Analysis</h2>', unsafe_allow_html=True)
                        
                        x = df['User'].value_counts().head()
                        name = x.index
                        count = x.values
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown('<div class="card">', unsafe_allow_html=True)
                            st.subheader('Messaging Percentage by User')
                            st.dataframe(
                                round((df['User'].value_counts() / df.shape[0]) * 100, 2)
                                .reset_index()
                                .rename(columns={'User': 'User', 'count': 'Percentage (%)'})
                                .style.background_gradient(cmap='Greens')
                            )
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown('<div class="card">', unsafe_allow_html=True)
                            fig, ax = plt.subplots()
                            colors = plt.cm.Greens(np.linspace(0.5, 0.9, len(name)))
                            ax.bar(name, count, color=colors)
                            ax.set_xlabel("Users")
                            ax.set_ylabel("Messages Sent")
                            plt.xticks(rotation='vertical')
                            fig.tight_layout()
                            st.pyplot(fig)
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Add a divider
                        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                    
                    # Emoji Analysis
                    st.markdown('<h2 class="sub-header">Emoji Analysis</h2>', unsafe_allow_html=True)
                    
                    emojiDF = functions.getEmoji(df)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.subheader('Top Emojis Used')
                        
                        # Create a better emoji dataframe display
                        if not emojiDF.empty:
                            emoji_df = pd.DataFrame({
                                'Emoji': emojiDF[0],
                                'Count': emojiDF[1]
                            }).head(10)
                            
                            st.dataframe(
                                emoji_df.style.background_gradient(cmap='Purples', subset=['Count'])
                            )
                        else:
                            st.info("No emojis found in the selected chat")
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        if not emojiDF.empty:
                            fig, ax = plt.subplots()
                            colors = plt.cm.Purples(np.linspace(0.5, 0.9, len(emojiDF[0].head())))
                            wedges, texts, autotexts = ax.pie(
                                emojiDF[1].head(), 
                                labels=emojiDF[0].head(), 
                                autopct="%0.1f%%", 
                                shadow=True,
                                colors=colors,
                                explode=[0.05] * len(emojiDF[0].head())
                            )
                            for autotext in autotexts:
                                autotext.set_fontsize(8)
                            fig.tight_layout()
                            st.pyplot(fig)
                        else:
                            st.info("No emoji data to display")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Add a divider
                    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                    
                    # Common Words
                    st.markdown('<h2 class="sub-header">Word Analysis</h2>', unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.subheader('Most Common Words')
                        
                        commonWord = functions.MostCommonWords(df)
                        
                        # Create word frequency dataframe
                        word_df = pd.DataFrame({
                            'Word': commonWord[0],
                            'Count': commonWord[1]
                        })
                        
                        st.dataframe(
                            word_df.style.background_gradient(cmap='Blues', subset=['Count'])
                        )
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        fig, ax = plt.subplots()
                        colors = plt.cm.Blues(np.linspace(0.5, 0.9, len(commonWord[0])))
                        ax.barh(commonWord[0][::-1], commonWord[1][::-1], color=colors)
                        ax.set_xlabel("Frequency")
                        ax.set_ylabel("Words")
                        fig.tight_layout()
                        st.pyplot(fig)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # WordCloud
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.subheader("Word Cloud")
                    
                    try:
                        df_wc = functions.create_wordcloud(df)
                        fig, ax = plt.subplots(figsize=(10, 6))
                        ax.imshow(df_wc)
                        ax.axis("off")
                        fig.tight_layout()
                        st.pyplot(fig)
                    except Exception as e:
                        st.error(f"Could not generate word cloud: {e}")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Add a divider
                    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                    
                    # Activity Analysis
                    st.markdown('<h2 class="sub-header">Activity Analysis</h2>', unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.subheader('Most Active Days')
                        
                        x = df['day'].value_counts()
                        fig, ax = plt.subplots()
                        colors = plt.cm.Greens(np.linspace(0.5, 0.9, len(x.index)))
                        ax.bar(x.index, x.values, color=colors)
                        ax.set_xlabel("Days")
                        ax.set_ylabel("Messages Sent")
                        plt.xticks(rotation='vertical')
                        fig.tight_layout()
                        st.pyplot(fig)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.subheader('Most Active Months')
                        
                        x = df['month_name'].value_counts()
                        fig, ax = plt.subplots()
                        colors = plt.cm.Greens(np.linspace(0.5, 0.9, len(x.index)))
                        ax.bar(x.index, x.values, color=colors)
                        ax.set_xlabel("Months")
                        ax.set_ylabel("Messages Sent")
                        plt.xticks(rotation='vertical')
                        fig.tight_layout()
                        st.pyplot(fig)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Activity Heatmap
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.subheader("Weekly Activity Heatmap")
                    
                    try:
                        user_heatmap = functions.activity_heatmap(df)
                        fig, ax = plt.subplots(figsize=(12, 6))
                        ax = sns.heatmap(user_heatmap, cmap="YlGnBu", linewidths=0.5, annot=True, fmt="g")
                        fig.tight_layout()
                        st.pyplot(fig)
                    except Exception as e:
                        st.error(f"Could not generate heatmap: {e}")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Timeline Analysis
                    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                    st.markdown('<h2 class="sub-header">Timeline Analysis</h2>', unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.subheader('Monthly Activity Timeline')
                        
                        timeline = functions.getMonthlyTimeline(df)
                        fig, ax = plt.subplots()
                        ax.plot(timeline['time'], timeline['Message'], color='#128C7E', marker='o', linestyle='-')
                        ax.set_xlabel("Month")
                        ax.set_ylabel("Messages Sent")
                        plt.xticks(rotation='vertical')
                        fig.tight_layout()
                        st.pyplot(fig)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.subheader('Daily Activity Timeline')
                        
                        try:
                            df['taarek'] = df['Date']
                            daily_timeline = df.groupby('taarek').count()['Message'].reset_index()
                            
                            fig, ax = plt.subplots()
                            ax.plot(daily_timeline['taarek'], daily_timeline['Message'], color='#075E54', marker='.', linestyle='-')
                            ax.set_xlabel("Date")
                            ax.set_ylabel("Messages Sent")
                            fig.autofmt_xdate()
                            fig.tight_layout()
                            st.pyplot(fig)
                        except Exception as e:
                            st.error(f"Could not generate daily timeline: {e}")
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.info("Please check that your chat file is in the correct format. The file should be exported from WhatsApp without media.")
    
    # Footer
    st.markdown('<div class="footer">', unsafe_allow_html=True)
    st.markdown("### About WhatsApp Chat Analyzer")
    st.markdown("""
    This application helps you analyze your WhatsApp chat history to uncover patterns and statistics.
    Upload any WhatsApp chat export file (without media) to get started.
    
    **How to export your WhatsApp chat:**
    1. Open the chat in WhatsApp
    2. Tap the three dots in the top right
    3. Select "More" > "Export chat"
    4. Choose "Without Media"
    5. Save the .txt file and upload it here
    
    Your data is processed securely and is not stored permanently.
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# If not logged in, show only the welcome screen
else:
    st.markdown('<h1 class="main-header"> WhatsApp Chat Analyzer By Bhoomika</h1>', unsafe_allow_html=True)
    
    # Centered welcome message
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/WhatsApp.svg/1200px-WhatsApp.svg.png", width=150)
        st.markdown("""
        ### Welcome to WhatsApp Chat Analyzer
        
        Discover insights from your WhatsApp conversations with detailed statistics and visualizations.
        
        **Features:**
        - Analyze message patterns
        - Track emoji usage
        - Identify most active times
        - Generate word clouds
        - And much more!
        
        Please log in or sign up using the sidebar to get started.
        """)
        st.markdown('</div>', unsafe_allow_html=True)
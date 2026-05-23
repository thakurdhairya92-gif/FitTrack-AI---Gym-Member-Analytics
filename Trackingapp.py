import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="FitTrack AI - Gym Member Analytics",
    page_icon="🏋️‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 1.1rem;
    }
    
    /* KPI Cards */
    .kpi-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        transition: transform 0.3s ease;
    }
    
    .kpi-card:hover {
        transform: translateY(-5px);
    }
    
    .kpi-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #2d3748;
        margin: 0;
    }
    
    .kpi-label {
        font-size: 0.95rem;
        color: #718096;
        margin: 0.5rem 0 0 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Section headers */
    .section-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 1.5rem;
        font-weight: 600;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e2e8f0;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    
    /* Prediction result */
    .prediction-box {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        color: white;
        margin: 1rem 0;
    }
    
    .prediction-value {
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
    }
    
    .prediction-label {
        font-size: 1.1rem;
        opacity: 0.9;
        margin-top: 0.5rem;
    }
    
    /* Info boxes */
    .info-box {
        background: #f0f4ff;
        border-radius: 10px;
        padding: 1rem 1.5rem;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f4ff;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
</style>
""", unsafe_allow_html=True)


# --- LOAD DATA ---
@st.cache_data
def load_data():
    df = pd.read_csv("gym_members_exercise_tracking.csv")
    return df


def calculate_expected_calories(row):
    """Calculate expected calories based on user inputs using regression coefficients"""
    base = 200
    duration_factor = row['Session_Duration (hours)'] * 500
    weight_factor = row['Weight (kg)'] * 2
    age_factor = -row['Age'] * 0.5
    bpm_factor = row['Avg_BPM'] * 1.5
    
    workout_multipliers = {'HIIT': 1.3, 'Cardio': 1.1, 'Strength': 1.0, 'Yoga': 0.8}
    workout_mult = workout_multipliers.get(row['Workout_Type'], 1.0)
    
    experience_bonus = row['Experience_Level'] * 30
    
    calories = (base + duration_factor + weight_factor + age_factor + bpm_factor + experience_bonus) * workout_mult
    return max(100, min(2000, calories))


# --- SIDEBAR ---
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h2 style="color: #667eea; margin: 0;">🏋️‍♂️ FitTrack AI</h2>
        <p style="color: #a0aec0; font-size: 0.9rem;">Member Analytics Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation
    page = st.radio(
        "📍 Navigation",
        ["🏠 Dashboard", "🔮 Calorie Predictor", "📊 Data Explorer", "👥 Member Insights"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Quick filters
    st.markdown("### 🎯 Quick Filters")
    
    df = load_data()
    
    selected_workout = st.multiselect(
        "Workout Type",
        options=df['Workout_Type'].unique(),
        default=df['Workout_Type'].unique()
    )
    
    age_range = st.slider(
        "Age Range",
        min_value=int(df['Age'].min()),
        max_value=int(df['Age'].max()),
        value=(int(df['Age'].min()), int(df['Age'].max()))
    )
    
    experience_filter = st.multiselect(
        "Experience Level",
        options=sorted(df['Experience_Level'].unique()),
        default=sorted(df['Experience_Level'].unique()),
        format_func=lambda x: {1: "Beginner", 2: "Intermediate", 3: "Advanced"}.get(x, str(x))
    )
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 1rem; background: rgba(102,126,234,0.1); border-radius: 10px;">
        <p style="margin: 0; font-size: 0.85rem; color: #718096;">
            📈 Powered by Machine Learning<br>
            <span style="font-size: 0.75rem;">v2.0 | 973 Members Analyzed</span>
        </p>
    </div>
    """, unsafe_allow_html=True)


# --- FILTER DATA ---
filtered_df = df[
    (df['Workout_Type'].isin(selected_workout)) &
    (df['Age'] >= age_range[0]) &
    (df['Age'] <= age_range[1]) &
    (df['Experience_Level'].isin(experience_filter))
]


# --- MAIN CONTENT ---
if page == "🏠 Dashboard":
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🏋️‍♂️ FitTrack AI Dashboard</h1>
        <p>Real-time analytics for gym member performance and health tracking</p>
    </div>
    """, unsafe_allow_html=True)
    
    # KPI Cards
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <p class="kpi-value">{len(filtered_df):,}</p>
            <p class="kpi-label">Total Members</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_calories = filtered_df['Calories_Burned'].mean()
        st.markdown(f"""
        <div class="kpi-card">
            <p class="kpi-value">{avg_calories:,.0f}</p>
            <p class="kpi-label">Avg Calories Burned</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_duration = filtered_df['Session_Duration (hours)'].mean()
        st.markdown(f"""
        <div class="kpi-card">
            <p class="kpi-value">{avg_duration:.1f}h</p>
            <p class="kpi-label">Avg Session Duration</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        avg_bmi = filtered_df['BMI'].mean()
        st.markdown(f"""
        <div class="kpi-card">
            <p class="kpi-value">{avg_bmi:.1f}</p>
            <p class="kpi-label">Avg BMI</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        avg_freq = filtered_df['Workout_Frequency (days/week)'].mean()
        st.markdown(f"""
        <div class="kpi-card">
            <p class="kpi-value">{avg_freq:.1f}</p>
            <p class="kpi-label">Avg Days/Week</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Charts Row 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<p class="section-header">📊 Calories by Workout Type</p>', unsafe_allow_html=True)
        workout_calories = filtered_df.groupby('Workout_Type')['Calories_Burned'].mean().reset_index()
        fig = px.bar(
            workout_calories,
            x='Workout_Type',
            y='Calories_Burned',
            color='Workout_Type',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_title="",
            yaxis_title="Average Calories",
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown('<p class="section-header">👥 Gender Distribution</p>', unsafe_allow_html=True)
        gender_counts = filtered_df['Gender'].value_counts()
        fig = px.pie(
            values=gender_counts.values,
            names=gender_counts.index,
            color_discrete_sequence=['#667eea', '#f093fb'],
            hole=0.4
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Charts Row 2
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<p class="section-header">📈 Session Duration vs Calories</p>', unsafe_allow_html=True)
        fig = px.scatter(
            filtered_df,
            x='Session_Duration (hours)',
            y='Calories_Burned',
            color='Workout_Type',
            size='Experience_Level',
            color_discrete_sequence=px.colors.qualitative.Set2,
            opacity=0.7
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown('<p class="section-header">🎯 Experience Level Distribution</p>', unsafe_allow_html=True)
        exp_labels = {1: 'Beginner', 2: 'Intermediate', 3: 'Advanced'}
        exp_data = filtered_df['Experience_Level'].map(exp_labels).value_counts()
        fig = px.bar(
            x=exp_data.index,
            y=exp_data.values,
            color=exp_data.index,
            color_discrete_sequence=['#38ef7d', '#667eea', '#f093fb']
        )
        fig.update_layout(
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_title="Experience Level",
            yaxis_title="Number of Members",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)


elif page == "🔮 Calorie Predictor":
    st.markdown("""
    <div class="main-header">
        <h1>🔮 Calorie Burn Predictor</h1>
        <p>AI-powered prediction based on your workout parameters</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<p class="section-header">📝 Enter Your Details</p>', unsafe_allow_html=True)
        
        input_col1, input_col2 = st.columns(2)
        
        with input_col1:
            age = st.number_input("Age", min_value=18, max_value=80, value=30)
            weight = st.number_input("Weight (kg)", min_value=40.0, max_value=150.0, value=70.0)
            height = st.number_input("Height (m)", min_value=1.4, max_value=2.2, value=1.75)
        
        with input_col2:
            gender = st.selectbox("Gender", ["Male", "Female"])
            workout_type = st.selectbox("Workout Type", ["HIIT", "Cardio", "Strength", "Yoga"])
            experience = st.select_slider(
                "Experience Level",
                options=[1, 2, 3],
                format_func=lambda x: {1: "Beginner", 2: "Intermediate", 3: "Advanced"}[x],
                value=2
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        session_duration = st.slider("Session Duration (hours)", 0.5, 2.0, 1.0, 0.1)
        avg_bpm = st.slider("Average Heart Rate (BPM)", 100, 180, 140)
        water_intake = st.slider("Water Intake (liters)", 1.0, 4.0, 2.5, 0.1)
        
        predict_btn = st.button("🔮 Predict Calories", use_container_width=True, type="primary")
    
    with col2:
        st.markdown('<p class="section-header">📊 Prediction Result</p>', unsafe_allow_html=True)
        
        if predict_btn:
            user_data = {
                'Age': age,
                'Weight (kg)': weight,
                'Session_Duration (hours)': session_duration,
                'Avg_BPM': avg_bpm,
                'Workout_Type': workout_type,
                'Experience_Level': experience
            }
            
            predicted_calories = calculate_expected_calories(user_data)
            
            st.markdown(f"""
            <div class="prediction-box">
                <p class="prediction-value">🔥 {predicted_calories:,.0f}</p>
                <p class="prediction-label">Estimated Calories Burned</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Comparison chart
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Get average for same workout type
            type_avg = filtered_df[filtered_df['Workout_Type'] == workout_type]['Calories_Burned'].mean()
            overall_avg = filtered_df['Calories_Burned'].mean()
            
            comparison_data = pd.DataFrame({
                'Category': ['Your Prediction', f'{workout_type} Average', 'Overall Average'],
                'Calories': [predicted_calories, type_avg, overall_avg]
            })
            
            fig = px.bar(
                comparison_data,
                x='Category',
                y='Calories',
                color='Category',
                color_discrete_sequence=['#38ef7d', '#667eea', '#f093fb']
            )
            fig.update_layout(
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Insights
            if predicted_calories > type_avg:
                st.success(f"🎉 Great! You're burning {predicted_calories - type_avg:.0f} more calories than the average {workout_type} workout!")
            else:
                st.info(f"💡 Tip: Try increasing your session duration or intensity to burn more calories.")
        else:
            st.markdown("""
            <div class="info-box">
                <p style="margin: 0; color: #4a5568;">
                    👈 Fill in your details and click <strong>Predict Calories</strong> to see your estimated calorie burn.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Show placeholder chart
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### 📈 How predictions work:")
            st.markdown("""
            Our AI model considers:
            - **Session Duration** - Longer workouts burn more calories
            - **Workout Type** - HIIT burns the most, Yoga the least
            - **Heart Rate** - Higher intensity = more calories
            - **Experience Level** - Advanced users have better efficiency
            - **Body Metrics** - Weight and age affect metabolism
            """)


elif page == "📊 Data Explorer":
    st.markdown("""
    <div class="main-header">
        <h1>📊 Data Explorer</h1>
        <p>Deep dive into the gym member dataset</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📋 Raw Data", "📈 Distributions", "🔗 Correlations"])
    
    with tab1:
        st.markdown(f"**Showing {len(filtered_df)} records** (filtered from {len(df)} total)")
        
        # Column selector
        all_columns = filtered_df.columns.tolist()
        selected_columns = st.multiselect(
            "Select columns to display",
            options=all_columns,
            default=['Age', 'Gender', 'Weight (kg)', 'Workout_Type', 'Calories_Burned', 'Session_Duration (hours)', 'Experience_Level']
        )
        
        if selected_columns:
            st.dataframe(
                filtered_df[selected_columns].style.background_gradient(cmap='Blues', subset=['Calories_Burned'] if 'Calories_Burned' in selected_columns else []),
                use_container_width=True,
                height=500
            )
        
        # Download button
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            "📥 Download Filtered Data",
            csv,
            "gym_data_filtered.csv",
            "text/csv",
            use_container_width=True
        )
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Age Distribution")
            fig = px.histogram(
                filtered_df,
                x='Age',
                nbins=20,
                color_discrete_sequence=['#667eea']
            )
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("#### Weight Distribution")
            fig = px.histogram(
                filtered_df,
                x='Weight (kg)',
                nbins=25,
                color_discrete_sequence=['#38ef7d']
            )
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### Calories Burned Distribution")
            fig = px.histogram(
                filtered_df,
                x='Calories_Burned',
                nbins=25,
                color_discrete_sequence=['#f093fb']
            )
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("#### BMI Distribution")
            fig = px.histogram(
                filtered_df,
                x='BMI',
                nbins=20,
                color_discrete_sequence=['#764ba2']
            )
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.markdown("#### Correlation Heatmap")
        
        numeric_cols = filtered_df.select_dtypes(include=[np.number]).columns.tolist()
        corr_matrix = filtered_df[numeric_cols].corr()
        
        fig = px.imshow(
            corr_matrix,
            text_auto='.2f',
            color_continuous_scale='RdBu_r',
            aspect='auto'
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("#### Key Correlations with Calories Burned")
        calories_corr = corr_matrix['Calories_Burned'].drop('Calories_Burned').sort_values(ascending=False)
        
        fig = px.bar(
            x=calories_corr.values,
            y=calories_corr.index,
            orientation='h',
            color=calories_corr.values,
            color_continuous_scale='RdYlGn'
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_title="Correlation Coefficient",
            yaxis_title="",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)


elif page == "👥 Member Insights":
    st.markdown("""
    <div class="main-header">
        <h1>👥 Member Insights</h1>
        <p>Detailed analysis of gym member segments</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Segment analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<p class="section-header">🎯 Workout Type Analysis</p>', unsafe_allow_html=True)
        
        workout_stats = filtered_df.groupby('Workout_Type').agg({
            'Calories_Burned': 'mean',
            'Session_Duration (hours)': 'mean',
            'Age': 'mean',
            'Workout_Frequency (days/week)': 'mean'
        }).round(2)
        
        st.dataframe(workout_stats.style.background_gradient(cmap='YlOrRd'), use_container_width=True)
        
        # Radar chart
        categories = ['Calories', 'Duration', 'Frequency', 'Avg BPM']
        
        fig = go.Figure()
        
        for workout in filtered_df['Workout_Type'].unique():
            wk_data = filtered_df[filtered_df['Workout_Type'] == workout]
            values = [
                wk_data['Calories_Burned'].mean() / 20,
                wk_data['Session_Duration (hours)'].mean() * 50,
                wk_data['Workout_Frequency (days/week)'].mean() * 20,
                wk_data['Avg_BPM'].mean() / 2
            ]
            values.append(values[0])
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories + [categories[0]],
                name=workout,
                fill='toself',
                opacity=0.6
            ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown('<p class="section-header">📊 Experience Level Breakdown</p>', unsafe_allow_html=True)
        
        exp_stats = filtered_df.groupby('Experience_Level').agg({
            'Calories_Burned': ['mean', 'std'],
            'Session_Duration (hours)': 'mean',
            'Fat_Percentage': 'mean',
            'BMI': 'mean'
        }).round(2)
        
        exp_stats.index = exp_stats.index.map({1: 'Beginner', 2: 'Intermediate', 3: 'Advanced'})
        st.dataframe(exp_stats, use_container_width=True)
        
        # Box plot
        fig = px.box(
            filtered_df,
            x='Experience_Level',
            y='Calories_Burned',
            color='Workout_Type',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_title="Experience Level",
            height=400
        )
        fig.update_xaxes(ticktext=['Beginner', 'Intermediate', 'Advanced'], tickvals=[1, 2, 3])
        st.plotly_chart(fig, use_container_width=True)
    
    # Gender comparison
    st.markdown('<p class="section-header">⚖️ Gender Comparison</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    gender_stats = filtered_df.groupby('Gender').agg({
        'Calories_Burned': 'mean',
        'BMI': 'mean',
        'Fat_Percentage': 'mean'
    }).round(2)
    
    with col1:
        fig = px.bar(
            gender_stats.reset_index(),
            x='Gender',
            y='Calories_Burned',
            color='Gender',
            color_discrete_sequence=['#667eea', '#f093fb']
        )
        fig.update_layout(showlegend=False, title="Avg Calories Burned", height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(
            gender_stats.reset_index(),
            x='Gender',
            y='BMI',
            color='Gender',
            color_discrete_sequence=['#667eea', '#f093fb']
        )
        fig.update_layout(showlegend=False, title="Avg BMI", height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        fig = px.bar(
            gender_stats.reset_index(),
            x='Gender',
            y='Fat_Percentage',
            color='Gender',
            color_discrete_sequence=['#667eea', '#f093fb']
        )
        fig.update_layout(showlegend=False, title="Avg Fat %", height=300)
        st.plotly_chart(fig, use_container_width=True)

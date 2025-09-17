import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from prophet import Prophet

st.set_page_config(
    page_title="COVID-19 India Dashboard",
    layout="wide",  # <- This sets desktop (wide) mode
    initial_sidebar_state="expanded"
)
st.title("🦠 COVID-19 India Data Dashboard")


@st.cache_data
def load_data():
    df = pd.read_csv("covid_19_india.csv")
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    return df

data = load_data()

data = data[data['State/UnionTerritory'].str.contains(r'\*',na=False) == False ]
cleaned_india_data=data[['State/UnionTerritory','Date','Cured','Deaths','Confirmed']].copy()
cleaned_data = cleaned_india_data.groupby('Date')[['Cured','Deaths','Confirmed']].sum().reset_index()
cleaned_data['Recover Rate'] = cleaned_data['Cured'] / cleaned_data['Confirmed'] * 100


fig = make_subplots(
    rows=2,
    cols=2,
    shared_xaxes=True,
    vertical_spacing=0.1,
    horizontal_spacing=0.1,
    subplot_titles=(
        "<b>Confirmed Cases Over Time</b>",
        "<b>Death Cases Over Time</b>",
        "<b>Cured/Recovered Cases Over Time</b>",
        "<b>Recovery Rate Trend</b>"
    )
)

fig.add_trace(
    go.Scatter(
        x=cleaned_data['Date'],
        y=cleaned_data['Confirmed'],
        name='Confirmed',
        line=dict(color='#1f77b4', width=2.5),
        hovertemplate="<b>Date</b>: %{x|%Y-%m-%d}<br><b>Cases</b>: %{y:,}<extra></extra>"
    ),
    row=1, col=1
)

fig.add_trace(
    go.Scatter(
        x=cleaned_data['Date'],
        y=cleaned_data['Deaths'],
        name="Deaths",
        line=dict(color='#d62728', width=2.5),
        hovertemplate="<b>Date</b>: %{x|%Y-%m-%d}<br><b>Deaths</b>: %{y:,}<extra></extra>"
    ),
    row=1, col=2
)

fig.add_trace(
    go.Scatter(
        x=cleaned_data['Date'],
        y=cleaned_data['Cured'],
        name='Cured',
        line=dict(color='#2ca02c', width=2.5),
        hovertemplate="<b>Date</b>: %{x|%Y-%m-%d}<br><b>Cured</b>: %{y:,}<extra></extra>"
    ),
    row=2, col=1
)



fig.add_trace(
    go.Scatter(
        x=cleaned_data['Date'],
        y=cleaned_data['Recover Rate'],
        name='Recovery Rate',
        line=dict(color='#9467bd', width=2.5),
        hovertemplate="<b>Date</b>: %{x|%Y-%m-%d}<br><b>Rate</b>: %{y:.1f}%<extra></extra>"
    ),
    row=2, col=2
)

fig.update_layout(
    height=900,
    width=1300,
    title_text="<b>COVID-19 Trends Analysis Dashboard</b>",
    title_x=0.5,
    title_font=dict(size=24),
    showlegend=True,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    plot_bgcolor='#0e1117',
    paper_bgcolor='#0e1117',
    hovermode="x unified",
    margin=dict(t=100, b=80, l=80, r=80)
)

# Axis formatting
axis_style = dict(
    showline=True,
    linewidth=1,
    linecolor='gray',
    mirror=True,
    showgrid=True,
    gridcolor='rgba(211,211,211,0.5)'
)

# Update y-axes
fig.update_yaxes(
    title_text="<b>Case Count</b>",
    row=1, col=1,
    **axis_style
)
fig.update_yaxes(
    title_text="<b>Death Count</b>",
    row=1, col=2,
    **axis_style
)
fig.update_yaxes(
    title_text="<b>Cured Count</b>",
    row=2, col=1,
    **axis_style
)
fig.update_yaxes(
    title_text="<b>Percentage (%)</b>",
    range=[0, 100],
    row=2, col=2,
    **axis_style
)

# Update x-axes
fig.update_xaxes(
    title_text="<b>Date</b>",
    row=2, col=1,
    **axis_style
)
fig.update_xaxes(
    title_text="<b>Date</b>",
    row=2, col=2,
    **axis_style
)

# Add range slider to bottom plots
fig.update_xaxes(
    rangeslider_visible=True,
    rangeselector=dict(
        buttons=list([
            dict(count=7, label="1w", step="day", stepmode="backward"),
            dict(count=1, label="1m", step="month", stepmode="backward"),
            dict(count=3, label="3m", step="month", stepmode="backward"),
            dict(step="all")
        ])
    ),
    row=2, col=1
)

fig.update_xaxes(
    rangeslider_visible=True,
    row=2, col=2
)

# Add annotation with data source
fig.add_annotation(
    x=1, y=-0.15,
    xref="paper", yref="paper",
    showarrow=False,
    font=dict(size=10, color="gray")
)

st.plotly_chart(fig,use_container_width=True)

fig1 = go.Figure(data = [
    go.Scatter3d(
        x=cleaned_data['Date'],
        y=cleaned_data['Confirmed'],
        z=cleaned_data['Deaths'],
        mode='markers+lines',
        marker=dict(
            size=4,
            color=cleaned_data['Deaths'],
            colorscale='Reds',
            opacity=0.8
        ),
        hovertemplate="<b>Date</b>: %{x|%Y-%m-%d}<br><b>Cases</b>: %{y:,} <br> <b>Deaths</b> : %{z:,}<extra></extra>"
    ),
    ]
)
fig1.update_layout(
    title = "3D visualization Date vs Confirmed vs Deaths",
    scene = dict(
        xaxis_title = "Date",
        yaxis_title = "Confirmed",
        zaxis_title = "Deaths"
    )
)

st.subheader(f"Overall Data Visualization")
st.plotly_chart(fig1,use_container_width=True)


state_list = sorted(data['State/UnionTerritory'].unique())
selected_state = st.sidebar.selectbox("Select a State", state_list)


state_data = data[data['State/UnionTerritory'] == selected_state]
state_daily = state_data.groupby('Date')[['Confirmed', 'Cured', 'Deaths']].sum().reset_index()


st.header(f"📈 Daily Trends in {selected_state}")
fig = px.line(state_daily, x='Date', y=['Confirmed', 'Cured', 'Deaths'], markers=True)
fig.update_layout(title=f"Daily Confirmed, Cured, and Deaths - {selected_state}", xaxis_title="Date", yaxis_title="Count")
st.plotly_chart(fig, use_container_width=True)


st.subheader("📊 National Summary by State")
summary = data.groupby('State/UnionTerritory')[['Confirmed', 'Cured', 'Deaths']].sum().reset_index()
summary['Recovery Rate (%)'] = (summary['Cured'] / summary['Confirmed']) * 100

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(px.bar(summary.sort_values('Confirmed', ascending=False),
                           x='State/UnionTerritory', y='Confirmed', title='Total Confirmed Cases by State',
                           color='Confirmed', color_continuous_scale='Oranges'), use_container_width=True)
    st.plotly_chart(px.bar(summary.sort_values('Cured', ascending=False),
                           x='State/UnionTerritory', y='Cured', title='Total Recovered Cases by State',
                           color='Cured', color_continuous_scale='Greens'), use_container_width=True)
with col2:
    st.plotly_chart(px.bar(summary.sort_values('Deaths', ascending=False),
                           x='State/UnionTerritory', y='Deaths', title='Total Deaths by State',
                           color='Deaths', color_continuous_scale='Reds'), use_container_width=True)
    st.plotly_chart(px.bar(summary.sort_values('Recovery Rate (%)', ascending=False),
                           x='State/UnionTerritory', y='Recovery Rate (%)',
                           title='Recovery Rate (%) by State', color='Recovery Rate (%)',
                           color_continuous_scale='Viridis'), use_container_width=True)



st.subheader(f"🔮 Forecasting COVID-19 Cases for {selected_state}")

# Prophet forecasting
forecast_df = state_daily[['Date', 'Confirmed']].rename(columns={'Date': 'ds', 'Confirmed': 'y'})
model = Prophet()
model.fit(forecast_df)
future = model.make_future_dataframe(periods=30)
forecast = model.predict(future)

# Plot forecast
fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], name='Forecast', line=dict(color='blue')))
fig2.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_upper'], name='Upper Bound', line=dict(color='lightblue'), showlegend=False))
fig2.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_lower'], name='Lower Bound', line=dict(color='lightblue'), fill='tonexty', fillcolor='rgba(173, 216, 230, 0.2)', showlegend=False))
fig2.update_layout(title=f"30-Day Forecast of Confirmed Cases in {selected_state}", xaxis_title='Date', yaxis_title='Forecasted Cases')
st.plotly_chart(fig2, use_container_width=True)


st.caption("Data source: covid_19_india.csv | Built with Plotly, Prophet & Streamlit")

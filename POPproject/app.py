from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import folium
from folium.plugins import HeatMap
import random
import os

app = Flask(__name__) 
DATA_FILE = "data.csv"

if not os.path.exists(DATA_FILE):
    dummy_data = []

    for _ in range(50):  # creates 50 fake entries
        phq_score = random.randint(0, 27)

        income = random.choice(['low', 'medium', 'high'])
        insurance = random.choice(['Yes', 'No'])
        transport = random.choice(['Yes', 'No'])

        if phq_score >= 10 or (income == 'low' and insurance == 'No' and transport == 'No'):
            risk = "High"
        elif phq_score >= 5:
            risk = "Medium"
        else:
            risk = "Low"

        lat = 28.3 + random.uniform(-0.2, 0.2)
        lon = -99.7 + random.uniform(-0.2, 0.2)

        dummy_data.append({
            "name": "Test",
            "age": random.randint(18, 70),
            "income": income,
            "insurance": insurance,
            "gender": "N/A",
            "ethnicity": "N/A",
            "transport": transport,
            "internet": random.choice(['Yes', 'No']),
            "phq_score": phq_score,
            "risk": risk,
            "lat": lat,
            "lon": lon
        })

    df = pd.DataFrame(dummy_data)
    df.to_csv(DATA_FILE, index=False)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/form', methods=['GET','POST'])
def form():
    if request.method == 'POST':
        age = int(request.form['age'])

        if age < 18:
            return "Only 18+ allowed"

        phq_score = sum([int(request.form[f"q{i}"]) for i in range(1,10)])

        income = request.form['income']
        insurance = request.form['insurance']
        transport = request.form['transport']

        if phq_score >= 10 or (income == 'low' and insurance == 'No' and transport == 'No'):
            risk = "High"
        elif phq_score >= 5:
            risk = "Medium"
        else:
            risk = "Low"

        lat = 28.3 + random.uniform(-0.2,0.2)
        lon = -99.7 + random.uniform(-0.2,0.2)

        data = {
            "name": request.form['name'],
            "age": age,
            "income": income,
            "insurance": insurance,
            "gender": request.form['gender'],
            "ethnicity": request.form['ethnicity'],
            "transport": transport,
            "internet": request.form['internet'],
            "phq_score": phq_score,
            "risk": risk,
            "lat": lat,
            "lon": lon
        }

        df = pd.read_csv(DATA_FILE)
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)

        return redirect(url_for('dashboard'))

    return render_template('form.html')

@app.route('/dashboard')
def dashboard():
    df = pd.read_csv(DATA_FILE)

    if len(df) == 0:
        return "No data yet"

    counts = df['risk'].value_counts()
    counts.plot(kind='bar')
    plt.title("Risk Distribution")
    plt.savefig(os.path.join(app.root_path, 'static', 'graph.png'))
    plt.close()

    return render_template('dashboard.html', table=df.to_html())

@app.route('/map')
def map_view():
    df = pd.read_csv(DATA_FILE)

    m = folium.Map(location=[28.42, -99.76], zoom_start=10)

    heat_data = []

    for _, row in df.iterrows():
        weight = 1
        if row['risk'] == 'High':
            weight = 3
        elif row['risk'] == 'Medium':
            weight = 2

        heat_data.append([row['lat'], row['lon'], weight])

    HeatMap(heat_data).add_to(m)

    m.save(os.path.join(app.root_path, 'templates', 'map.html'))
    return render_template('map.html')

if __name__ == '__main__':
    app.run(debug=True)
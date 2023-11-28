import requests
from pymongo import *
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from flask import Flask, render_template, request
app = Flask(__name__)

# Assuming your MongoDB collection is already defined as 'collection'

@app.route('/', methods=['GET', 'POST'])

def index():
 if request.method == 'POST':
        city = request.form['city']
 else:
        # Utilisez une ville par défaut si le formulaire n'est pas soumis
        city = 'Agadir'
 api_key = '6be5558a1b845d134b4279b13fe45f1f'
 

 url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}'
 response = requests.get(url)
 data = response.json()

 data['main']['temp']=data['main']['temp']-273.15
 data['main']['temp_min']=data['main']['temp_min']-273.15
 data['main']['temp_max']=data['main']['temp_max']-273.15

 client = MongoClient('localhost', 27017)
 db = client['Weather']
 collection = db[city]
 collection.insert_one(data)
 last_doc = collection.find_one(sort=[('_id', -1)])

# Utilisez les données récupérées depuis MongoDB pour créer des graphiques


 temperature = last_doc['main']['temp']
 humidity = last_doc['main']['humidity']
 wind_speed = last_doc['wind']['speed']
 wind_degree = last_doc['wind']['deg']
 visibility = last_doc['visibility']
 try:
   wind_gust = last_doc['wind']['gust'] 
 except:
   wind_gust='not found' 
 

    # Create a figure with subplots for the bar chart and the table
 fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))

    # Plot bar chart
 ax1.bar(['Temperature', 'Humidity'], [temperature, humidity])
 ax1.set_ylabel('Values')
 ax1.set_title('Temperature and Humidity in {}'.format(last_doc['name']))

    # Create a table for wind and visibility
 table_data = [
        ['Wind Speed', '{} m/s'.format(wind_speed)],
        ['Wind Degree', '{}°'.format(wind_degree)],
        ['Gust', '{} m/s'.format(wind_gust)],
        ['Visibility', '{} meters'.format(visibility)]
    ] 

 table = ax2.table(cellText=table_data, loc='center', cellLoc='center', colLabels=['Metric', 'Value'])
 table.auto_set_font_size(False)
 table.set_fontsize(10)
 table.scale(1, 1.5)

    # Save the plot to a BytesIO object
 img = BytesIO()
 plt.savefig(img, format='png')
 img.seek(0)
 plot_url = base64.b64encode(img.getvalue()).decode()

 return render_template('index.html', V=plot_url)






if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, request, jsonify, render_template, Response
import networkx as nx
import pandas as pd
import requests

app = Flask(__name__)

graph = nx.read_graphml('graph.graphml')
df = pd.read_csv('data.csv')
nodes = list(graph.nodes)
# print(nodes)

@app.route('/classify', methods=['GET', 'POST'])
def classify():
    global df
    if request.method == 'POST':
        link = request.form['link']
        classification = request.form['classification']

        try:
            response = requests.get(f'https://{link}', timeout=5)
            response.raise_for_status()
            web_text = response.text.replace('\n', ' ').replace('\r', ' ').replace(',', ' ')
        except requests.RequestException as e:
            web_text = 'Failed to retrieve text'
            print(f'Error fetching {link}: {e}')
        
        # Update the DataFrame with the classification
        df = pd.concat([df, pd.DataFrame([{'link': link, 'classification': classification, 'text': web_text}])], ignore_index=True)
        df.to_csv('data.csv', index=False)
        
    if nodes:
        link = nodes.pop()
        while link in df['link'].values:
            link = nodes.pop()
        return render_template('classify.html', link=link, count=len(nodes))
    else:
        return 'No more links to classify' 
@app.route('/proxy/<path:url>')
def proxy(url):
    try:
        response = requests.get(f'https://{url}', timeout=5)
        response.raise_for_status()
        return Response(response.content, content_type=response.headers['Content-Type'])
    except requests.RequestException as e:
        return f'Error fetching {url}: {e}', 500

if __name__ == '__main__':
    app.run(debug=True)


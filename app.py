from flask import Flask, render_template, request, jsonify
import pandas as pd
import json
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    data = None
    if request.method == 'POST':
        file = request.files['file']
        if file:
            data = process_file(file)
    return render_template('index.html', data=data)

def process_file(file):
    # Read the uploaded file directly
    df = pd.read_csv(file)
    
    # Data processing
    hierarchy = {'name': 'Root', 'children': []}
    for _, row in df.iterrows():
        cluster, subcluster, page_title, volume, node_type, url = row['Cluster'], row['Subcluster'], row['Page Title'], row['Volume'], row['Type'], row['URL']
        if not cluster or not subcluster or not page_title:
            continue

        cluster_node = next((child for child in hierarchy['children'] if child['name'] == cluster), None)
        if cluster_node is None:
            cluster_node = {'name': cluster, 'children': [], 'type': node_type}
            hierarchy['children'].append(cluster_node)

        subcluster_node = next((child for child in cluster_node['children'] if child['name'] == subcluster), None)
        if subcluster_node is None:
            subcluster_node = {'name': subcluster, 'children': [], 'type': node_type}
            cluster_node['children'].append(subcluster_node)

        if not any(child['name'] == page_title for child in subcluster_node['children']):
            subcluster_node['children'].append({'name': page_title, 'value': volume, 'type': node_type, 'url': url})

    def assign_cumulative_values(node):
        if 'children' in node:
            total_value = sum(assign_cumulative_values(child) for child in node['children'])
            node['value'] = total_value
            return total_value
        else:
            return node.get('value', 1)

    assign_cumulative_values(hierarchy)

    return hierarchy

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

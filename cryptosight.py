
---

## 🧠 `cryptosight/analyzer.py`

```python
import os
import time
import requests
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()
RPC_URL = os.getenv("WEB3_PROVIDER")
web3 = Web3(Web3.HTTPProvider(RPC_URL))

ETH_THRESHOLD = Web3.toWei(50, 'ether')  # min transfer to be considered
WINDOW = 120  # seconds

class ClusterAnalyzer:
    def __init__(self):
        self.tx_history = []
        self.graph = nx.Graph()

    def fetch_latest_block(self):
        return web3.eth.get_block('latest', full_transactions=True)

    def process_block(self, block):
        now = time.time()
        for tx in block.transactions:
            if tx['value'] > ETH_THRESHOLD:
                from_addr = tx['from']
                to_addr = tx['to']
                self.tx_history.append({
                    'from': from_addr,
                    'to': to_addr,
                    'timestamp': now,
                    'value': tx['value']
                })
                self.graph.add_edge(from_addr, to_addr, weight=tx['value'])

        # Очищаем устаревшие транзакции
        self.tx_history = [tx for tx in self.tx_history if now - tx['timestamp'] < WINDOW]

    def detect_clusters(self):
        G = self.graph.copy()
        components = [c for c in nx.connected_components(G) if len(c) >= 3]
        return components

    def alert(self, clusters):
        for cluster in clusters:
            print(f"🔔 ALERT: Cluster of {len(cluster)} wallets simultaneously moved > 50 ETH.")
            self.visualize_cluster(cluster)

    def visualize_cluster(self, nodes):
        subgraph = self.graph.subgraph(nodes)
        plt.figure(figsize=(10, 8))
        nx.draw(subgraph, with_labels=True, node_color='skyblue', edge_color='gray')
        plt.title("Cluster Movement Detected")
        plt.savefig("cluster_graph.png")
        print("→ Graph saved to cluster_graph.png\n")

    def run(self):
        while True:
            try:
                block = self.fetch_latest_block()
                self.process_block(block)
                clusters = self.detect_clusters()
                if clusters:
                    self.alert(clusters)
                time.sleep(15)
            except Exception as e:
                print(f"[ERROR] {e}")
                time.sleep(30)

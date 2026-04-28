"""
17_export_network_snapshot.py
=============================
Exporta os artefatos de rede a partir dos snapshots de co-citacao locais,
sem chamar APIs externas.
"""

from pathlib import Path
import pandas as pd
import networkx as nx

BASE_DIR = Path(__file__).resolve().parents[2]
INTERIM_DIR = BASE_DIR / "data" / "interim"
NETWORK_DIR = BASE_DIR / "outputs" / "network"
NETWORK_DIR.mkdir(parents=True, exist_ok=True)

EDGES_IN = INTERIM_DIR / "07_cocitation_matrix_edges.csv"
REFS_IN = INTERIM_DIR / "07_nuclear_references.csv"

EDGES_OUT = NETWORK_DIR / "cocitation_edges.csv"
REFS_OUT = NETWORK_DIR / "nuclear_references.csv"
GRAPHML_OUT = NETWORK_DIR / "cocitation_graph.graphml"


def main() -> None:
    if not EDGES_IN.exists():
        print("Sem matriz de co-citacao local; rode 11_enrich_references.py para gerar.")
        return

    edges = pd.read_csv(EDGES_IN, dtype={"source": str, "target": str})
    edges.to_csv(EDGES_OUT, index=False, encoding="utf-8-sig")

    if REFS_IN.exists():
        refs = pd.read_csv(REFS_IN, dtype=str)
        refs.to_csv(REFS_OUT, index=False, encoding="utf-8-sig")

    graph = nx.Graph()
    for _, row in edges.iterrows():
        graph.add_edge(str(row["source"]), str(row["target"]), weight=int(row["weight"]))
    nx.write_graphml(graph, GRAPHML_OUT)

    print(f"Rede exportada: {EDGES_OUT}")
    print(f"GraphML exportado: {GRAPHML_OUT}")


if __name__ == "__main__":
    main()

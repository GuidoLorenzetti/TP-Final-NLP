import networkx as nx
import matplotlib.pyplot as plt
from rdflib import Graph, URIRef, RDF, RDFS
import urllib.parse
import os

def create_graph(datos_usuario, usuario):
    # Crear un grafo dirigido
    G = nx.DiGraph()

    # Agregar el nodo principal
    G.add_node(usuario, label="Usuario")

    # Agregar nodos secundarios y ejes con etiquetas
    for key, value in datos_usuario.items():
        # Convertir listas a cadenas
        if isinstance(value, list):
            value = '_'.join(value)
        
        G.add_node(value, label=key)
        G.add_edge(usuario, value, label=key)

    datos_usuario = obtain_non_consumible_ingredients(datos_usuario)

    value = '_'.join(datos_usuario['ingredientes_no_consumir'])
    value1 = '_'.join(datos_usuario['alergias'])
    G.add_node(value, label="Ingredientes no consumir")
    G.add_edge(datos_usuario['dieta'], value, label="Ingredientes no consumir")
    G.add_edge(datos_usuario['sensibilidad'], value, label="Ingredientes no consumir")
    G.add_edge(value1, value, label="Ingredientes no consumir")

    # Create an RDF graph
    rdf_graph = Graph()

    # Define vocabulary prefixes
    rdf_graph.bind("rdf", RDF)
    rdf_graph.bind("rdfs", RDFS)

    # Transform nodes to RDF resources
    for node in G.nodes:
        # Convert node to string
        node_str = str(node)
        encoded_node = urllib.parse.quote(node_str, safe='')
        subject_uri = URIRef(f"http://example.org/node/{encoded_node}")

        rdf_graph.add((subject_uri, RDF.type, URIRef("http://example.org/ontology/Node")))

    # Transform edges to RDF triples
    for edge in G.edges:
        # Convert nodes to strings
        subject_str = str(edge[0])
        object_str = str(edge[1])

        # Codify directly without the need for encode
        encoded_subject = urllib.parse.quote(subject_str, safe='')
        encoded_object = urllib.parse.quote(object_str, safe='')

        subject_uri = URIRef(f"http://example.org/node/{encoded_subject}")
        object_uri = URIRef(f"http://example.org/node/{encoded_object}")

        # Use the same relation label as in NetworkX (edge[2])
        relation_label = str(G[edge[0]][edge[1]]['label']) if 'label' in G[edge[0]][edge[1]] else "knows"

        # Replace spaces and commas with underscores in the relation label
        relation_label = relation_label.replace(' ', '_').replace(',', '_')

        rdf_graph.add((subject_uri, URIRef(f"http://example.org/ontology/{relation_label}"), object_uri))

    # Crear la carpeta si no existe
    repo_path = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(repo_path, 'graph_databases')
    os.makedirs(folder_path, exist_ok=True)

    # Serialise and print the RDF graph (Turtle format)
    rdf_graph.serialize(destination=os.path.join(folder_path, f'rdf_{usuario}_database.ttl'), format='turtle')

def obtain_non_consumible_ingredients(dict):
    dict['ingredientes_no_consumir'] = []

    if dict['dieta'] == 'Vegana':
        dict['ingredientes_no_consumir'].append('Productos_de_origen_animal')

    elif dict['dieta'] == 'Vegetariana':
        dict['ingredientes_no_consumir'].append('Carne')

    elif dict['dieta'] == 'Cetogenica':
        dict['ingredientes_no_consumir'].append('Carbohidratos')

    if dict['sensibilidad'] == 'Celiaquia':
        dict['ingredientes_no_consumir'].append('Ingredientes_con_gluten')

    if 'Ninguna' not in dict['alergias']:
        dict['ingredientes_no_consumir'].extend(dict['alergias'])

    return dict


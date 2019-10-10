import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from tqdm import tqdm
from sklearn.preprocessing import minmax_scale


def raw_matrix(data_loc='users/', period=None):
    period = str(period) if period else ''
    user_list = next(os.walk(data_loc))[1]
    file_names = data_loc + '{}/subreddits' + period + '.csv'
    df_list = []
    for user in tqdm(user_list):
        filename = file_names.format(user)
        try:
            df_list.append(pd.read_csv(filename, index_col=0, names=[user], header=0))
        except FileNotFoundError as e:
            print(e)
            continue
    raw_df = pd.concat(df_list, axis=1, sort=False).fillna(0)
    return raw_df


def modified_min_max_scaler(m, axis=0):
    m = m.astype('float')
    m[m == 0] = 'nan'
    if axis == 0:
        m = minmax_scale(m)
    else:
        m = minmax_scale(m.T).T
    m[np.isnan(m)] = 0
    return m


def AGM_matrix(raw_df, node_type='u', norm=None):
    users_list = list(raw_df)
    subs_list = list(raw_df.index)
    raw_matrix = raw_df.values
    if norm is not None:
        raw_matrix = modified_min_max_scaler(raw_matrix, norm)
    if node_type == 'r':
        raw_matrix = raw_matrix.T
    size = raw_matrix.shape[1]
    sim_matrix = np.zeros((size, size), dtype='float')
    for i in tqdm(range(size - 1)):
        for j in range(i, size):
            u = raw_matrix[:, i]
            v = raw_matrix[:, j]
            sim_matrix[i, j] = 1 - np.exp(-u@v)
            sim_matrix[j, i] = sim_matrix[i, j]
    column_names = users_list if node_type == 'u' else subs_list
    return pd.DataFrame(data=sim_matrix, index=column_names, columns=column_names)


def create_graph(sim_df):
    dist = -np.log(sim_df)
    G = nx.Graph()
    names = sim_df.index
    size = len(names)
    G.add_nodes_from(sim_df.index)
    for i in tqdm(range(size - 1)):
        for j in range(i + 1, size):
            u = names[i]
            v = names[j]
            weight = dist[u][v]
            if weight == np.inf:
                continue
            G.add_edge(u, v, weight=weight)
    return G


def nbr_subgraph(G, node, n=20):
    edges = sorted(list(G.edges(node, data=True)), key=lambda x: x[2]['weight'])
    sg = nx.Graph()
    sg.add_edges_from(edges[:n])
    return sg


def graph_with_length(G):
    pos = nx.spring_layout(G, weight='weight')
    nx.draw_networkx(G, pos=pos)


def save_output(name, out_loc='outputs/', data_loc='users/', period=None):
    x = name.split('/')
    raw_df = raw_matrix(data_loc, period)
    norm = 0 if x[0] is 'u' else 1
    sim_df = AGM_matrix(raw_df, node_type=x[0], norm=norm)
    G = create_graph(sim_df)
    sub = nbr_subgraph(G, x[1], 10)
    graph_with_length(sub)
    period = str(period) if period else ''
    fname = out_loc + period + '_'.join(x) + '.png'
    plt.savefig(fname, dpi=1000)


if __name__ == '__main__':
    pass

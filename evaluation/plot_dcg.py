import numpy as np
import matplotlib.pyplot as plt
import os

def readFile(filename):
    """
    Read the scores from a list of results
    """
    result = np.array([])
    with open(filename, 'r') as file:
        for line in file:
            line = line.rstrip()
            values = line.split("*")
            result = np.append(result, int(values[1]))
    return result

def compute_dcg(scores):
    """
    Compute the Discounted Cumulative Gain (DCG) for a list of scores
    """
    dcg = 0
    for i, score in enumerate(scores):
        dcg += score / np.log2(i + 2) # +2 because the log is 1-indexed
    return dcg

def bar_chart(dcg_values, labels, title, save_path=None):
    """
    Plot the DCG values as a bar chart
    """
    plt.bar(labels, dcg_values, alpha=1)
    plt.xlabel('Labels')
    plt.ylabel('DCG Values')
    plt.title(title)
    plt.xticks(rotation=90) # Rotate x-axis labels for better readability
    plt.tight_layout() # So that the labels fit on the image

    if save_path != None:
        plt.savefig(save_path) # Save plot to file
    plt.show()

path = "./evaluation/"
methods = ["BM25", "TF_IDF", "DFR", "LM_DIRICHLET"]
NUM_OF_QUERIES = 4
queries = []

for i in range(1,NUM_OF_QUERIES+1):
    newQueryFilenames = []
    for methodName in methods:
        newQueryFilenames.append(methodName+"/"+methodName+f"_query{i}_results.txt")
    queries.append(newQueryFilenames)

query_dcg_lists = []

for i, query_filenames in enumerate(queries, start=1):
    query_dcg = []

    for filename in query_filenames:
        scores = readFile(path + filename)
        dcg = compute_dcg(scores)
        query_dcg.append(dcg)
        print(f"Query {i}, {filename}: {dcg}")
    query_dcg_lists.append(query_dcg)

# Plot DCG for each query
for i, query_dcg in enumerate(query_dcg_lists, start=1):
    save_path = os.path.join(path, f"DCGs_Query{i}.png")
    bar_chart(query_dcg, methods, f"Bar Chart of Discounted Cumulative Gain for Query {i}", save_path)
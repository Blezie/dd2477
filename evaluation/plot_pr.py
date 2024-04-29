import numpy as np
import matplotlib.pyplot as plt
import os

def readFile(filename):
    """
    Read the scores from a list of results
    """
    result = np.array([])
    file = open(filename)
    print()
    for line in file:
        line = line.rstrip()
        values = line.split("*")
        result = np.append(result, int(values[1]))
    print(len(result))
    return result

def precision(array):
    return np.sum(array >  0) / len(array)

def recall(array):
    return np.sum(array >  0) /  100


path = "./evaluation/"
methods = ["BM25", "TF_IDF", "DFR", "LM_DIRICHLET"]
NUM_OF_QUERIES = 4
queries = []

for i in range(1,NUM_OF_QUERIES+1):
    newQueryFilenames = []
    for methodName in methods:
        newQueryFilenames.append(methodName+"/"+methodName+f"_query{i}_results.txt")
    queries.append(newQueryFilenames)

"""
# For individual curves
for i, query_filenames in enumerate(queries, start=1):
    for j in range(len(query_filenames)): # All methods for query_i
        filename = query_filenames[j]
        methodName = filename.split("/")[0] # Extract the method name from the filename
        results = readFile(path + filename)
        PRE = np.array([precision(results[:i]) for i in range(1, len(results)+1, 3)]) # 15 results
        REC = np.array([recall(results[:i]) for i in range(1, len(results)+1, 3)])
        
        print(f"Query {i}, {filename}: Precision {np.round(PRE * 100) / 100}, Recall {REC}")

        save_path = os.path.join(path, methodName, f"PR_curve_query{i}.png")
        
        plt.plot(REC, PRE, 'r-')
        plt.axis([np.min(REC), np.max(REC), 0, 1.1])
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title(f"Precision-Recall curve for Query {i}, Method {methods[j]}")

        plt.savefig(save_path) # Save plot to file

        plt.show()
"""

# All curves for 1 query in 1 plot
colors = plt.cm.get_cmap('tab10', len(methods))
for i, query_filenames in enumerate(queries, start=1):
    for j in range(len(query_filenames)): # All methods for query_i
        filename = query_filenames[j]
        methodName = filename.split("/")[0] # Extract the method name from the filename
        results = readFile(path + filename)
        PRE = np.array([precision(results[:i]) for i in range(1, len(results)+1, 3)]) # 15 results
        REC = np.array([recall(results[:i]) for i in range(1, len(results)+1, 3)])
        
        print(f"Query {i}, {filename}: Precision {np.round(PRE * 100) / 100}, Recall {REC}")

        plt.plot(REC, PRE, color=colors(j), label=methodName) # Plot with color and label
        
    plt.axis([np.min(REC), np.max(REC), 0, 1.1])
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title(f"Precision-Recall curve for Query {i}")
    plt.legend() # Add a legend to the plot

    save_path = os.path.join(path, f"PR_curve_query{i}.png")
    plt.savefig(save_path) # Save plot to file

    plt.show()
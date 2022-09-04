import pickle

with open("tools.dat", "rb") as f:
    tools = pickle.load(f)
    print(tools)

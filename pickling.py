import pickle

def load_obj(name ):
    with open(f"./data/{name}.pkl", "rb") as f:
        return pickle.load(f)

def save_obj(obj, name):    # Save object to a pickled file
    with open(f"./data/{name}.pkl", "wb") as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

load_obj("sim4_tldata")

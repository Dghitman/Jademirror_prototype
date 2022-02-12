import hashlib
import json
import os
import cloudpickle

class Graph:
    def __init__(self, json_dict):
        self.nodes = json_dict
        for _,n in self.nodes.items():
            if n["parents"] != []:
                for p in n["parents"]:
                    if "ready" not in self.nodes[p[0]]:
                        self.nodes[p[0]]["ready"] = []
                    self.nodes[p[0]]["ready"].append(p[1])

    def quick_inference(self, callback):
        nodes_to_add = {}
        for h,n in self.nodes.items():
            if "ready" in n:
                if callback.__class__.__name__ in n["ready"]:
                    continue
            for result in callback(n["type"], n["data"]):
                if result is None:
                    continue
                type, data, label = result
                parents = [[h, callback.__class__.__name__, label]]
                node_to_add = {
                    "data": data,
                    "type": type,
                    "parents": parents
                }
                node_hash = hashlib.sha256(json.dumps(node_to_add).encode("utf-8")).hexdigest()
                node_to_add["nodeHash"] = node_hash
                nodes_to_add[node_hash] = node_to_add
        return nodes_to_add

    def quick_distance(self, callback):
        nodes_to_add = {}
        for h1,n1 in self.nodes.items():
            for h2,n2 in self.nodes.items():
                if h1 == h2: continue
                result = callback(n1["type"], n1["data"], n2["type"], n2["data"])
                if result is None:
                    continue
                type, data = result
                parents = list(sorted([[h1, callback.__class__.__name__, ""], [h2, callback.__class__.__name__, ""]]))
                node_to_add = {
                    "data": data,
                    "type": type,
                    "parents": parents
                }
                node_hash = hashlib.sha256(json.dumps(node_to_add).encode("utf-8")).hexdigest()
                node_to_add["nodeHash"] = node_hash
                nodes_to_add[node_hash] = node_to_add
        return nodes_to_add

    def extend(self, nodes):
        self.nodes.update(nodes)

class Worker:

    def serialize(self):
        cloudpickle.dump(self, open("./worker.pkl", "wb"))
        print("Worker saved!")

class InferenceWorker(Worker):

    def __init__(self):
        pass

    def __call__(self):
        pass

class DistanceWorker(Worker):

    def __init__(self):
        pass

    def __call__(self):
        pass

class WorkerPool:

    def __init__(self):
        self.workers = []
        for d in os.listdir("workers"):
            p = f"workers/{d}/worker.pkl"
            if os.path.isfile(p):
                self.workers.append(cloudpickle.load(open(p, "rb")))

    def __call__(self, graph):
        request_graph = graph
        result_graph = Graph({})
        for worker in self.workers:
            if issubclass(worker.__class__, InferenceWorker):
                inference_result = request_graph.quick_inference(worker)
                result_graph.extend(inference_result)
                request_graph.extend(inference_result)
            elif issubclass(worker.__class__, DistanceWorker):
                distance_result = request_graph.quick_distance(worker)
                result_graph.extend(distance_result)
                request_graph.extend(distance_result)
        return result_graph.nodes
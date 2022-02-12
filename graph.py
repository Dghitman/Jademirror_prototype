import hashlib
import json
import os
import inspect
import workers

class Graph:
    def __init__(self, json_dict):
        self.nodes = json_dict

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
                node_to_add = {
                    "data": data,
                    "type": type,
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
                node_to_add = {
                    "data": data,
                    "type": type,
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
        for name, obj in inspect.getmembers(workers):
            if inspect.isclass(obj) and (("Inference" in name) or ("Distance" in name)):
                print(f"Loading {name}...")
                self.workers.append(obj())
        print("Workers loaded!")

    def __call__(self, graph):
        request_graph = graph
        result_graph = Graph({})
        for worker in self.workers:
            if "Inference" in worker.__class__.__name__:
                inference_result = request_graph.quick_inference(worker)
                result_graph.extend(inference_result)
                request_graph.extend(inference_result)
            elif "Distance" in worker.__class__.__name__:
                distance_result = request_graph.quick_distance(worker)
                result_graph.extend(distance_result)
                request_graph.extend(distance_result)
        return result_graph.nodes
from core import analyzer, element
from ui import run


element_type = {
    "Resistance": element.Resistance,
    "CurrentSource": element.CurrentSource,
    "VoltageSource": element.VoltageSource,
    "CCCS": element.CCCS,
    "VCCS": element.VCCS,
    "CCVS": element.CCVS,
    "VCVS": element.VCVS
}


def solve(data):
    try:
        node_count = data["node_count"]
        elements = []
        for tmp in data["elements"]:
            new_elem = element_type[tmp["name"]](*tmp["args"], **tmp["kwargs"])
            elements.append(new_elem)
        an = analyzer.Analyzer(node_count, elements)
        result = an.run()
        return analyzer.Analyzer.get_data(result)
    except:
        return None


if __name__ == "__main__":
    run.Run(800, 600, "Nodal analysis", solve).run()

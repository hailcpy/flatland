import json
from numpy.random import permutation

from flatland.lang.lisp import parse as parse_lisp


def rewrite_edge(edge, frandoms, is_l2=False, flowparams=[]):
    fnode, tnode = edge
    answer = []
    if "__randomize__" in fnode:  # randomizer parameter for upcoming flow
        parname, body = tnode
        frandoms.append(f"({parname} {body})")
    elif "(start" in fnode:  # define-flow open
        fname, fparams = fnode.split("(")
        paramfills = "".join(x for x in frandoms)
        fparams = fparams.replace("start", "(").replace("( ", "(")
        frandoms.clear()
        answer.append(f"(define-flow {fname} {fparams} ({paramfills}) (\n")
        tname, *tprops = tnode.split("(")
        tprops = "(".join(tprops)
        answer.append(f"(create-node {tname} {tprops}\n")
        answer.append(f"(create-entry {tname})\n")
    elif "{" in fnode:  # defining the main flow
        data = json.loads(fnode)
        x, y = data.get("position", (64, 64))
        theta = data.get("theta", 0)
        pos = f"{x} {y}"
        if "(" in tnode:
            ind = tnode.index("(")
            tname = tnode[:ind]
            tprops = tnode[ind + 1 :]
        else:
            tname = tnode
            tprops = "("
        if is_l2:
            flowparams.append(f"{tname} ({tprops}")
            return ""
        answer.append(f"(run-flow {tname} ({tprops} ({pos}) {theta})\n")
    elif "(end" in tnode:  # define-flow closed
        answer.append(f"(create-exit {fnode}))\n)\n")
    else:  # just an edge
        fname, *port = fnode.split(" ")
        if len(port) == 0:
            port = "out"
        else:
            port = port[0]

        if "(" in tnode:
            ind = tnode.index("(")
            tname = tnode[:ind]
            tprops = tnode[ind + 1 :]
            answer.append(f"(create-node {tname} {tprops}\n")
        else:
            tname = tnode

        if port == "out":
            answer.append(f"(create-link {fname} {tname})\n")
        else:
            answer.append(f"(create-link {fname}:{port} {tname})\n")
    return "".join(answer)


def fbp_to_lisp(program):
    lines = program.split("\n")

    def edge_cleaner(s):
        fnode, tnode = s.split("->")
        return fnode.strip(), tnode.strip()

    def param_cleaner(s):
        parset, body = s.split("}")
        parname = parset.split("{")[1]
        return "__randomize__", (parname.strip(), body.strip())

    edges = []
    imports = []
    rand_params = []
    for line in lines:
        if len(line) == 0:
            continue
        elif "@param" in line:
            rand_params.append(param_cleaner(line))
        elif "#include" in line:
            imports.append(f"({line})")
        else:
            edges.extend(rand_params)
            edges.append(edge_cleaner(line))
            rand_params.clear()
    # print("edges", edges)
    rand_params.clear()
    expr = (
        "(begin\n"
        + "\n".join(imports)
        + "".join(rewrite_edge(x, rand_params) for x in edges)
        + ")"
    )
    # print(expr)
    return expr


def fpb_to_lisp_mul(programs: list):
    expr_str = "(begin\n"
    imports = []
    flows = []
    flowparams = []
    for program in programs:
        edges = []
        lines = program.split("\n")

        def edge_cleaner(s):
            fnode, tnode = s.split("->")
            return fnode.strip(), tnode.strip()

        def param_cleaner(s):
            parset, body = s.split("}")
            parname = parset.split("{")[1]
            return "__randomize__", (parname.strip(), body.strip())

        rand_params = []
        for line in lines:
            if len(line) == 0:
                continue
            elif "@param" in line:
                rand_params.append(param_cleaner(line))
            elif "#include" in line:
                imports.append(f"({line})")
            else:
                edges.extend(rand_params)
                edges.append(edge_cleaner(line))
                rand_params.clear()
        rand_params.clear()
        flow = "".join(rewrite_edge(x, rand_params, is_l2=True, flowparams=flowparams) for x in edges)
        flows.append(flow)
    # randomly choose some flows and join them sequentially, leave the rest separate
    flowname = "random"
    expr_str += "\n".join(imports) + "".join(flow for flow in flows) + f"(define-flow {flowname} () () (\n"
    fname = ""
    for i, index in enumerate(permutation(len(flowparams))):
        # create node
        flowparam = flowparams[index]
        ind = flowparam.index('(')
        tname = flowparam[:ind].strip()
        tprops = flowparam[ind + 1:]
        nodename = tname + '1'
        expr_str += f"(create-node {nodename} {tname} {tprops}\n"
        if i == 0:
            # create entry
            expr_str += f"(create-entry {nodename})\n"
        else:
            # create link
            expr_str += f"(create-link {fname} {nodename})\n"
        fname = nodename
    expr = (
        expr_str
        + f"(create-exit {fname}))\n)\n"
        + f"(run-flow {flowname} () (64 64) {0}))"
    )
    return expr


def parse(program):
    if isinstance(program, str):
        expr = fbp_to_lisp(program)
    elif isinstance(program, list):
        expr = fpb_to_lisp_mul(program)
    else:
        raise TypeError("program should be either str or list")
    return parse_lisp(expr)

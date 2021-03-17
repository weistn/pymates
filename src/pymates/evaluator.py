from pymates.dom import Node, FunctionNode, SpanNode, StyleNode, DocumentNode
  
class Evaluator:
    def __init__(self):
        self.doc = None

    def evaluate(self, node, nspace):
        if isinstance(node, str):
            return
        elif isinstance(node, StyleNode):
            if hasattr(node.style, "pagesize"):
                self.doc.pagesize = getattr(node.style, "pagesize")
        elif isinstance(node, DocumentNode):
            self.doc = node
        self.evaluateNodes(node.children, nspace)

    def evaluateNodes(self, nodes, nspace):
        if nodes == None:
            return
        i = 0
        while i < len(nodes):
            node = nodes[i]
            if isinstance(node, FunctionNode):
                # Evaluate the DOM-arguments
                self.evaluateNodes(node.children, nspace)
                # Build argument list for function call
                args = []
                for arg in node.args:
                    value = eval(arg, nspace)
                    args.append(value)
                args.extend(node.children)
                kwargs = {}
                for k, arg in node.kwargs.items():
                    print(k)
                    print(arg)
                    value = eval(arg, nspace)
                    kwargs[k] = value
                # Call function
                print(f"Calling {node.func.__name__}")
                print(node)
                result = node.func(*args, **kwargs)
                nodes.pop(i)
                # Insert the result
                if isinstance(result, list):
                    for r in result:
                        if isinstance(r, str) or isinstance(r, Node):
                            r.indent = node.indent
                            nodes.insert(i, r)
                            i += 1
                        else:
                            raise BaseException(f"Wrong return type of function {node.func.__name__}")
                elif isinstance(result, str) or isinstance(result, Node):
                    result.indent = node.indent
                    nodes.insert(i, result)
                    i += 1
                else:
                    raise BaseException(f"Wrong return type of function {node.func.__name__}")
            else:
                self.evaluate(node, nspace)
                i += 1
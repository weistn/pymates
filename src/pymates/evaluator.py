from pymates.dom import Node, FunctionNode, SpanNode, StyleNode, DocumentNode
  
class Evaluator:
    def __init__(self):
        self.doc = None
        self.step = None

    def evaluate(self, node, nspace, step = None):
        if isinstance(node, str):
            return
        elif isinstance(node, StyleNode):
            if hasattr(node.style, "pagesize"):
                self.doc.pageSize = getattr(node.style, "pagesize")
        elif isinstance(node, DocumentNode):
            self.doc = node
            self.step = step
        self.evaluateNodes(node.children, nspace)

    def evaluateNodes(self, nodes, nspace):
        if nodes == None:
            return
        i = 0
        while i < len(nodes):
            node = nodes[i]
            if isinstance(node, FunctionNode):
                # Do not evaluate the function in the current step?
                if node.className != self.step:
                    i += 1
                    continue
                # Evaluate the DOM-arguments
                self.evaluateNodes(node.children, nspace)
                # Build argument list for function call
                if node.evaluateArgs:
                    args = []
                    for arg in node.args:
                        print(arg)
                        value = eval(arg, nspace)
                        args.append(value)
                else:
                    args = node.args
                args.extend(node.children)
                if node.evaluateArgs:
                    kwargs = {}
                    for k, arg in node.kwargs.items():
                        print(k)
                        print(arg)
                        value = eval(arg, nspace)
                        kwargs[k] = value
                else:
                    kwargs = node.kwargs
                # Call function
                print(f"Calling {node.func.__name__}")
                print(node)
                result = node.func(*args, **kwargs)
                nodes.pop(i)
                # A FunctionNode is substituted by another function node?
                # This happens when the @later decorator has been used.
                if isinstance(result, FunctionNode):
                    result.evaluateArgs = False
                    # Preserve the children
                    result.children = node.children
                    result.args = [result]
                    result.args.extend(args[:len(node.args)])
                # Insert the result
                if isinstance(result, list) or isinstance(result, tuple):
                    for r in result:
                        if isinstance(r, str):
                            nodes.insert(i, r)
                            i += 1
                        elif isinstance(r, Node):
                            r.indent = node.indent
                            nodes.insert(i, r)
                            i += 1
                        else:
                            raise BaseException(f"Wrong return type of function {node.func.__name__}")
                elif isinstance(result, str):
                    nodes.insert(i, result)
                    i += 1
                elif isinstance(result, Node):
                    result.indent = node.indent
                    nodes.insert(i, result)
                    i += 1
                else:
                    print(result)
                    raise BaseException(f"Wrong return type of function {node.func.__name__}")
            else:
                self.evaluate(node, nspace)
                i += 1
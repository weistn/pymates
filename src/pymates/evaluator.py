from pymates.dom import Node, FunctionNode, SpanNode, StyleNode, DocumentNode
  
class Evaluator:
    def __init__(self):
        self.doc = None
        self.step = None

    def evaluate(self, node, nspace, step = None):
        if isinstance(node, str):
            return
        #elif isinstance(node, StyleNode):
        #    if hasattr(node.style, "pagesize"):
        #        self.doc.pageSize = getattr(node.style, "pagesize")
        elif isinstance(node, DocumentNode):
            self.doc = node
            self.step = step
        self.evaluateChildren(node, nspace)

    def evaluateChildren(self, parent, nspace):
        nodes = parent.children
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
                print(f"Calling {node.func.__name__} {node.className}")
                # Evaluate the DOM-arguments
                self.evaluateChildren(node, nspace)
                # Build argument list for function call
                if node.evaluateArgs:
                    args = []
                    for arg in node.args:
                        print(arg)
                        value = eval(arg, nspace)
                        args.append(value)
                elif node.className != None:
                    # Functions decorated with @inline or @section
                    # expect their node as first argument.
                    args = [node]
                    args.extend(node.args)
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
                result = node.func(*args, **kwargs)
                nodes.pop(i)
                # A FunctionNode is substituted by another function node?
                # This happens when the @inline or @section decorator has been used.
                if isinstance(result, FunctionNode):
                    result.evaluateArgs = False
                    # Preserve the children
                    result.children = node.children
                    # result.args = [result]
                    # result.args.extend(args[:len(node.args)])
                # Insert the result
                if isinstance(result, list) or isinstance(result, tuple):
                    for r in result:
                        if isinstance(r, (str, int, float, bool)):
                            parent.insertChild(i, str(r))
                            i += 1
                        elif isinstance(r, Node):
                            r.indent = node.indent
                            parent.insertChild(i, r)
                            i += 1
                        else:
                            raise BaseException(f"Wrong return type of function {node.func.__name__}")
                elif isinstance(result, (str, int, float, bool)):
                    parent.insertChild(i, str(result))
                    i += 1
                elif isinstance(result, Node):
                    result.indent = node.indent
                    parent.insertChild(i, result)
                    i += 1
                elif result == None:
                    pass
                else:
                    print(result)
                    raise BaseException(f"Wrong return type of function {node.func.__name__}")
            else:
                self.evaluate(node, nspace)
                i += 1
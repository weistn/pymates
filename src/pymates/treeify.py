from pymates.dom import StyleNode, ParagNode, DocumentNode, FunctionNode, FunctionNodeMode

def treeify(doc):
    treeifyChildren(doc)

def treeifyChildren(parent):
    if parent.children == None:
        return
    i = 0
    section = parent
    doNotInline = False
    while i < len(parent.children):
        node = parent.children[i]
        if not doNotInline and (isinstance(node, (str, StyleNode)) or (isinstance(node, FunctionNode) and node.mode == FunctionNodeMode.Inline)):
            # TODO: Check that no ParagNodes became children of a StyleNode
            # if isinstance(section, DocumentNode):
            #    raise BaseException("Oooops")
            if section == parent:
                i += 1
            else:
                parent.children.pop(i)
                section.append(node)
        elif isinstance(node, ParagNode) or (isinstance(node, FunctionNode) and node.mode == FunctionNodeMode.Section):
            treeifyChildren(node)
            section = node
            i += 1
            doNotInline = False
        elif isinstance(node, FunctionNode) and node.mode == FunctionNodeMode.SectionOrInline:
            i += 1
            doNotInline = True
        else:
            i += 1

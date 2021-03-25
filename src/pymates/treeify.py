from pymates.dom import StyleNode, ParagNode, DocumentNode, FunctionNode, FunctionNodeMode, mergeStyle

def treeify(doc):
    treeifyChildren(doc)

def treeifyChildren(parent):
    if parent.children == None:
        return
    i = 0
    section = parent
    doNotInline = False
    hasText = False
    while i < len(parent.children):
        node = parent.children[i]
        if not doNotInline and (isinstance(node, (str, StyleNode)) or (isinstance(node, FunctionNode) and node.mode == FunctionNodeMode.Inline)):
            # TODO: Check that no ParagNodes became children of a StyleNode
            # if isinstance(section, DocumentNode):
            #    raise BaseException("Oooops")
            if isinstance(node, str) and node != "":
                hasText = True
            if isinstance(node, StyleNode) and not hasText:
                section.style = mergeStyle(section.style, node.style)
                parent.children.pop(i)
            elif section == parent:
                i += 1
            else:
                parent.children.pop(i)
                section.append(node)
        elif isinstance(node, ParagNode) or (isinstance(node, FunctionNode) and node.mode == FunctionNodeMode.Section):
            treeifyChildren(node)
            section = node
            i += 1
            doNotInline = False
            hasText = False
        elif isinstance(node, FunctionNode) and node.mode == FunctionNodeMode.SectionOrInline:
            i += 1
            doNotInline = True
        else:
            i += 1

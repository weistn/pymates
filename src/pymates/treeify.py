from pymates.dom import StyleNode, ParagNode, DocumentNode

def treeify(doc):
    treeifyChildren(doc)

def treeifyChildren(parent):
    if parent.children == None:
        return
    i = 0
    section = parent
    while i < len(parent.children):
        node = parent.children[i]
        if isinstance(node, (str, StyleNode)):
            # TODO: Check that no ParagNodes became children of a StyleNode
            if isinstance(section, DocumentNode):
                raise BaseException("Oooops")
            if section == parent:
                i += 1
            else:
                parent.children.pop(i)
                section.append(node)
        elif isinstance(node, ParagNode):
            treeifyChildren(node)
            section = node
            i += 1
        else:
            i += 1

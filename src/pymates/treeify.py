from pymates.dom import Node, StyleNode, ParagNode, DocumentNode, FunctionNode, FunctionNodeMode, mergeStyle

def treeify(doc):
    print("====================== TREE ================")
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
        print(f"node {i} {node.func if isinstance(node, Node) else '>' + node + '<'}")
        # Style nodes, strings and inline functions become children of the current section.
        if not doNotInline and (isinstance(node, (str, StyleNode)) or (isinstance(node, FunctionNode) and node.mode == FunctionNodeMode.Inline)):
            # TODO: Check that no ParagNodes became children of a StyleNode
            if isinstance(node, str) and node != "":
                hasText = True
            if isinstance(node, StyleNode) and not hasText:
                # Style nodes following a ParagNode and not preceeded by text are removed and their
                # style is merged with the ParagNode´s style.
                section.style = mergeStyle(section.style, node.style)
                parent.children.pop(i)
            elif section == parent:
                # The node is a child of ´section´ already.
                i += 1
            else:
                # Make `node`a parent of `section`.
                parent.children.pop(i)
                section.append(node)
        elif isinstance(node, ParagNode) or (isinstance(node, FunctionNode) and node.mode == FunctionNodeMode.Section):
            if node.indent == -1:
                node.indent = parent.indent
            if node.indent > section.indent:
                i, newNode = _makeChild(section, i, section, node)
            elif node.indent <= section.indent:
                p = section
                while p != parent:
                    if node.indent >= p.indent:
                        break
                    p = p.parent
                print(f"_makeChild {node.func} {i} of {node.parent.func}")
                i, newNode = _makeChild(parent, i, p, node)
                print(f"    returns {i}")
            else:
                i += 1
            # treeifyChildren(node)
            treeify(newNode)
            section = node
            doNotInline = False
            hasText = False
        elif isinstance(node, FunctionNode) and node.mode == FunctionNodeMode.SectionOrInline:
            i += 1
            doNotInline = True
        else:
            i += 1

def _makeChild(rootParent, index, parent, child):
    prevParent = child.parent
    childChain = _createIntermediatParents(child)
    if isinstance(childChain, DocumentNode):
        print(f"       doc anchor {prevParent} {rootParent}")
        # The `child` cannot be added to the closes container.
        indirectParent = child.parent
        c = child
        # Search in parent (and recursively in parent´s parent) for a node type that
        # appears in the childChain.
        # Start with the direct parent of `child` and work the way down
        # It must terminate, because at the end of the `childChain` there is a DocumentNode.
        # The same is true for the chain of parents starting at `parent`.
        while True:
            # Iterate down the chain of parents, starting at `parent`, and
            # look for an instance of `indirectParent`.
            newParent = parent
            while newParent != rootParent.parent:
                print(f"    testing child {c.func} {c} against {newParent.func} {newParent}")
                if indirectParent.func == newParent.func:
                    return _makeChildIntern(rootParent, index, newParent, prevParent, c)
                newParent = newParent.parent
            # Try the next node in the `childChain`.
            c = indirectParent
            indirectParent = indirectParent.parent
            if c == None:
                raise BaseException(f"Child {child} cannot live inside parent {rootParent}")

    # The loop must terminate because the document is a default container
    c = child
    while True:
        # Iterate down the chain of parents, starting at `parent`, and
        # look for an instance of `indirectParent`.
        newParent = parent
        while newParent != rootParent.parent:
            print(f"    testing {c.func} of parent {c.parent} against {newParent.func} {newParent.isDefaultContainer}")
            if c.parent != None and c.parent.func == newParent.func:
                return _makeChildIntern(rootParent, index, newParent, prevParent, c)
            if c.parentContainer == None and (newParent.isDefaultContainer or (newParent.isExplicitContainer and newParent.indent < child.indent)):
                return _makeChildIntern(rootParent, index, newParent, prevParent, c)
            newParent = newParent.parent
        c = c.parent
        if c == None:
            print(child.indent, parent.indent)
            raise BaseException(f"Child {child.func} cannot live inside parent {rootParent.func}")

def _makeChildIntern(rootParent, index, newParent, prevParent, newChild):
    if newParent == prevParent and newParent == rootParent:
        print(f"     replacing with {newChild.func} at {rootParent}")
        rootParent.children[index] = newChild
        newChild.parent = rootParent
        print(f"     new child {newChild} of parent {newChild.parent}")
        return index + 1, newChild
    print(f"     reparenting {newChild.func} to {newParent.func}")
    prevParent.children.pop(index)
    newParent.append(newChild)
    return index, newChild

def _createIntermediatParents(child):
    parentFunc = child.parentContainer
    while parentFunc != None:
        p = parentFunc()
        p.append(child)
        p.indent = child.indent
        child = p
        parentFunc = child.parentContainer    
    return child
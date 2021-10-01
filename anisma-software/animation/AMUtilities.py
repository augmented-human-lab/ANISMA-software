

def getInterpolatedPos(prevPos, nextPos, fraction):
    dirVec = [nextPos[0] - prevPos[0], nextPos[1] - prevPos[1]]
    return [prevPos[0] + fraction*dirVec[0], prevPos[1] + fraction*dirVec[1]]


def getFrameBetween(scene, startTime, endTime):
    fs = scene.getFrames()

    for f in fs:
        time = f.getTime()
        if time >= startTime and time <= endTime:
            return f

    return None

def getPreviousFrame(scene, time=None, frame=None):
    fs = scene.getFrames()
    result = None

    if frame is not None:
        time = frame.getTime()

    for f in fs:
        ftime = f.getTime()

        if ftime < time:
            result = f
        else:
            break

    return result

def getNextFrame(scene, time=None, frame=None):
    fs = scene.getFrames()

    if frame is not None:
        time = frame.getTime()

    for f in fs:
        ftime = f.getTime()

        if ftime > time:
            return f

    return None

def getNodeStateFromFrame(frame, node):
    for ns in frame.getNodeStates():
        if ns.getNode() is node:
            return ns

    return None

def getPrevNodeState(scene, time, node):
    fs = scene.getFrames()
    prevNodeState = None

    for f in fs:
        if f.getTime() < time:
            newNodeState = getNodeStateFromFrame(f, node)
            if newNodeState is not None:
                prevNodeState = newNodeState

    return prevNodeState

def getNextNodeState(scene, time, node):
    fs = scene.getFrames()
    nextNodeState = None

    for f in fs:
        if f.getTime() > time:
            nextNodeState = getNodeStateFromFrame(f, node)
            if nextNodeState is not None:
                break

    return nextNodeState


# Interface
class RenderingObject:

    __view = None
    isHighlighted = False

    def setView(self, view):
        self.__view = view

    def requestUpdate(self, objID):
        if self.__view is not None:
            self.__view.update(objID)

    def isInBounds(self, x, y):
        raise NotImplementedError()

    def update(self, zoomlevel):
        raise NotImplementedError()

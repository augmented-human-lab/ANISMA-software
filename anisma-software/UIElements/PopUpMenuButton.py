
class PopUpMenuButton:

    def __init__(self, title, callback):
        self._title = title
        self._callback = callback

    def onClick(self, obj=None):
        if obj is not None:
            self._callback(obj)
        else:
            self._callback()

    def getTitle(self):
        return self._title

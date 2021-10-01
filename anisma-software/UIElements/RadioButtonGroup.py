

class RadioButtonGroup:

    def __init__(self):
        self._buttons = []
        self._active = None

    def addButton(self, btn):
        self._buttons.append(btn)

    def setActive(self, button=None, btnNum=-1):
        for b in self._buttons:
            b.renderAsActivated(False)

        if button is not None:
            button.renderAsActivated(True)
            self._active = button
        elif btnNum > -1:
            self._buttons[btnNum].renderAsActivated(True)
            self._active = self._buttons[btnNum]
        else:
            self._active = None

    def getActiveButton(self):
        return self._active

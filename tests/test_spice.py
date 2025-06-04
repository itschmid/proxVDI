import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import types


# Create stub PyQt5.QtCore modules if PyQt5 is missing
if 'PyQt5' not in sys.modules:
    pyqt5 = types.ModuleType('PyQt5')
    qtcore = types.ModuleType('PyQt5.QtCore')
    class QObject:
        def __init__(self, *args, **kwargs):
            pass
    class QProcess:
        def startDetached(self, *args, **kwargs):
            return True
    qtcore.QObject = QObject
    qtcore.QProcess = QProcess
    pyqt5.QtCore = qtcore
    sys.modules['PyQt5'] = pyqt5
    sys.modules['PyQt5.QtCore'] = qtcore

from proxVDI.services.spice import Spice


def test_replace_hostname_in_url():
    spice = Spice()
    original = "http://example.com:8000/path"
    result = spice.replace_hostname_in_url(original, "1.2.3.4")
    assert result == "http://1.2.3.4:8000/path"

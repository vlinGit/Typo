import sys
sys.path.append('../serverFiles')
from typer import Typer

if __name__ == "__main__":
    t = Typer()
    print(t.generateText())
"""
UPDATE DATE OF THIS FILE

Yevgeniy Gennadijovic Palamarchuk
"""
from gui import AtemzugValidierungGUI


# Bedingung sorgt dafür, dass das Skript direkt ausgeführt wird (kein Import in anderem Skript)
if __name__ == "__main__":  # =true, wenn Skript direkt ausgeführt wird
    app = AtemzugValidierungGUI()
    app.mainloop()

# TEST MIT GITHUB
from gui import AtemzugValidierungGUI


def main():
    app = AtemzugValidierungGUI()
    app.mainloop()


# Bedingung sorgt dafür, dass das Skript direkt ausgeführt wird (kein Import in anderem Skript)
if __name__ == "__main__":  # =true, wenn Skript direkt ausgeführt wird
    main()

import random   

class TextDesign:
    
    def __init__(self):
        """
        * Creates a randomized list of options for the text 
        """

        # Randomize font + Style
        fonts = ["Gan CLM:bold", "Assistant:bold", "Assistant:normal", "MigdalHaemeq:normal", "Stam Ashkenaz CLM:normal", "Comix No2 CLM:bold"]
        self.font = random.choice(fonts)
        
        # Randomize color (#RRRGGGBBB)
        colorString = '0123456789ABCDEF'
        self.color = '#'

        for i in range(9):
            index = random.randint(0, len(colorString)-1)
            self.color = self.color + colorString[index]

        # Randomize x, y, font size and angle
        self.x = random.randint(100, 1000)
        self.y = random.randint(150, 500)
        if self.x < 250 or self.x > 850:
            self.fontSize = random.randint(10, 25)
        else:
            self.fontSize = random.randint(10, 40)
        if self.y > 400 or self.y < 250:
            self.angle = random.randint(-30, 40)
        else:
            self.angle = random.randint(-80, 80)

if __name__ == '__main__':
    TextDesign()


    
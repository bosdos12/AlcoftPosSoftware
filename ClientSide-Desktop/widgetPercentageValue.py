

def widgetPercentageValue(p, s, w):
    width = w.width()
    height = w.height()
    if (p > 0) and p <= 100:
        if s == "h":
            return int((p/100)*height)
        elif s == "w":
            return int((p/100)*width)

        else:
            print(f"Invalid argument, please enter either 'w' or 'h' as the second parameter,\n{str(s)} is invalid;") 
    else:
        print(f"Please enter a percentage value between 0 and 100,\n{str(p)} is invalid;")
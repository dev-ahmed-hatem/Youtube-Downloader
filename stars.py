def print_time_colck(width: int):
    for i in range(width, 0, -1):
        print(" " * (width - i) + ("* " * i))
    for i in range(2, width + 1):
        print(" " * (width - i) + ("* " * i))


print_time_colck(6)

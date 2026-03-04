source_file = "source.pas"

with open(source_file, 'r') as file:
    qtd_lines = 0
    
    for line in file:
        for char in line:
            if char == '\n': qtd_lines += 1
            print(char, end="")
            
            
            
            
source_file = "source.pas"

with open(source_file, 'r') as file:
    qtd_lines = 0
    
    for line in file:
        qtd_lines += 1
        for char in line:
            print(char, end="")
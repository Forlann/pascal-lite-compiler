class AnalisadorLexico:
    def __init__(self, source_code):
        self.code = source_code
        self.position = 0
        self.current_line = 1

    def next_char(self):
        char = self.peak_char()

        if char is not None:
            self.position += 1
            return char

        return None

    def peak_char(self, i=0):
        if self.position < len(self.code):
            return self.code[self.position + i]
        return None

    def skip_char(self):
        char = self.code[self.position]
        skip_chars = [' ', '\t', '\r', '\n']
        possible_comment = ['/', '(', '*', ')', '{', '}']

        comment_chars = [
            ['/', '/'], ['(', '*'], ['*', ')']
        ]

        while True:
            
            if char in skip_chars:
                if char == '\n':
                    self.current_line += 1

                next_char = self.peak_char(1)
                self.next_char()
                char = self.peak_char()

            elif char in possible_comment:
                next_char = self.peak_char(1)

                if [char, next_char] in comment_chars:
                    print('É um comentário')
                    while char != '\n':
                        self.next_char()
                        char = self.peak_char()

                    self.current_line += 1
                    char = self.peak_char()
                    print('Fim do comentário')
                else: 
                    break
            else: 
                break
        return char

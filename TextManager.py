class TextManager:
    @staticmethod
    def get_last_incident_index(text, character):
        """
            :param text: (String) Texto para análise.
            :param character: (String) Caractere para ser encontrado.
            :return: (Int) Índice de última incidência do caractere.
        """
        last_incidence = None
        i = len(text) - 1
        while i > 0:
            if character == text[i]:
                last_incidence = i
                break
            i -= 1
        return last_incidence

    def get_index_of_what_comes_last(self, text, characters):
        """
            :param text: (String) Texto para análise.
            :param characters: (Array) Lista de String com caracteres para comparação.
            :return: (Int) Índice do caractere que aparece por último.
        """

        # Seleciona dos caracteres passados apenas os contidos no texto.
        characters = [char for char in characters if char in text]

        last_char_index = None
        for char in characters:
            # Verifica a última incidência.
            index = self.get_last_incident_index(text, char)

            # Compara com o valor anterior, se for maior salva.
            if not last_char_index:
                last_char_index = index
            elif index > last_char_index:
                last_char_index = index
        return last_char_index

    def format_text(self, lines, max_length):
        """
            :param lines: (Array de Strings) Lista com as linhas de texto a serem formatadas.
            :param max_length: (Int) Número máximo de caracteres por linha.
            :return: (Array de Strings) Lista de linhas respeitando o comprimento máximo.
        """
        formatted_lines = []
        there_were_changes = True
        while there_were_changes:
            there_were_changes = False
            for i, line in enumerate(lines):
                line = line.strip()
                if len(line) > max_length:
                    there_were_changes = True

                    # Verifica onde pode cortar a linha
                    divider_index = self.get_index_of_what_comes_last(line[:max_length], [' ', ',', '.'])
                    if divider_index:
                        piece_that_fit = line[:divider_index + 1]
                        rest = line[divider_index + 1:]
                    else:
                        piece_that_fit = line[:max_length]
                        rest = line[max_length:]

                    # Adiciona partes cortadas
                    formatted_lines.append(piece_that_fit.strip())
                    rest = rest.strip()
                    if rest:
                        lines[i] = rest
                    else:
                        lines.pop(i)
                    break
                else:
                    # Linha está nas normas
                    formatted_lines.append(line)
        return formatted_lines

    @staticmethod
    def get_last_piece_of_path(path):
        """
            :param path: (String) Caminho completo para a pasta.
            :return: (String) Pedaço final do caminho.
        """
        seps = [r'\ '.strip(), '/']
        for sep in seps:
            if sep in path:
                return path.split(sep)[-1]

    @staticmethod
    def find_patterns(text, patterns, to_meet=1):
        """
            :param text: (String) Texto para análise.
            :param patterns: (Array de Strings) Padrões.
            :param to_meet: (Int) Quantidade de padrões necessários no mesmo arquivo.
            :return: (Boolean) True se atendeu a quantidade minima de padrões.
        """
        pattern_match = 0

        # Procura por padrões.
        for pattern in patterns:
            if pattern in text:
                pattern_match += 1

        # Verifica se atende aos requisitos.
        return pattern_match >= to_meet

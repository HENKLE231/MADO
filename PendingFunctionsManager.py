class PendingFunctionsManager:
    @staticmethod
    def remove_pending_function(queue, function):
        """
            :param queue: (Queue) Instância da Queue.
            :param function: (Array) Lista onde o primeiro ítem é o nome da função
            e o restante parâmetros a serem passados para ela.
            Retira a função passada da queue.
        """
        # Pega a função da lista de funções pendentes armazenada na queue.
        info = queue.get()

        # Remove função.
        info.remove(function)

        # Armazena o resultado na queue novamente.
        queue.put(info)

    @staticmethod
    def get_pending_functions(queue):
        """
            :param queue: (Queue) Instância da Queue.
            :return: (Array) Lista funções pendentes.
        """
        # Se há algo na queue, o valor é obtido, senão é criada uma lista.
        if queue.qsize() > 0:
            info = queue.get()
        else:
            info = []

        # Armazena novamente na queue.
        queue.put(info)

        # Devolve uma cópia da queue.
        return info

    @staticmethod
    def add_pending_function(queue, new_function):
        """
            :param queue: (Queue) Instância da Queue.
            :param new_function: (Array) Lista onde o primeiro ítem é o nome da função
            e o restante parâmetros a serem passados para ela.
            Adiciona a lista de funções pendentes armazenada na queue.
        """
        # Se há algo na queue, o valor é obtido, senão é criada uma lista.
        if queue.qsize() > 0:
            info = queue.get()
        else:
            info = []

        # Adiciona função na lista de funções pendentes.
        info.append(new_function)
        queue.put(info)

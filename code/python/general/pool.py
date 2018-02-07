import numpy as np
from json import loads as json_from_string
from sklearn.model_selection import train_test_split

class PoolError(Exception):
    pass

class Pool:
    def __init__(self, *args):
        self.POSITIONS = list(range(10)) + [100]
        if len(args) == 0:
            self.features = []
            self.positions = []
            self.probas = []
            self.labels = []
            self.queries = []
            self.prod_positions = []
        elif len(args) == 1:
            if type(args[0]) != str:
                raise PoolError("Wrong constructor arguments")
            else:
                with open(args[0]) as handler:
                    data = [json_from_string(line) for line in handler]
                self.features = np.array([line['factors'][:1052] for line in data])
                self.positions = np.array([
                    int(line['images_metric'][0]) if line['images_metric'] is not None else 100
                    for line in data
                ])
                self.probas = np.array([line['p'] for line in data])
                self.labels = np.array([
                    (line['images_metric'][2] - line['images_metric'][1])
                    if line['images_metric'] is not None else 0
                    for line in data
                ])
                self.queries = [
                    list(map(int, line['query'].split(' ')))
                    for line in data
                ]
                self.prod_positions = [
                    int(line['prod_pos'])
                    for line in data
                ]

    def set(self, features, positions, probas, labels, queries, prod_positions):
        self.features = features
        self.positions = positions
        self.probas = probas
        self.labels = labels
        self.queries = queries
        self.prod_positions = prod_positions

    def split_by_position(self):
        pools = [Pool() for position in self.POSITIONS]

        for feature, position, proba, label, queries, prod_positions in zip(self.features, self.positions, self.probas, self.labels, self.queries, self.prod_positions):
            index = position if position in list(range(10)) else 10
            pools[index].features.append(feature)
            pools[index].positions.append(position)
            pools[index].probas.append(proba)
            pools[index].labels.append(label)
            pools[index].queries.append(queries)
            pools[index].prod_positions.append(prod_positions)

        for pool in pools:
            pool.features = np.array(pool.features)
            pool.positions = np.array(pool.positions)
            pool.probas = np.array(pool.probas)
            pool.labels = np.array(pool.labels)
            pool.queries = np.array(pool.queries)
            pool.prod_positions = np.array(pool.prod_positions)

        return pools

    def train_test_split(self, test_size=0.3):
        features_train, features_test,\
        positions_train, positions_test,\
        labels_train, labels_test,\
        proba_train, proba_test,\
        queries_train, queries_test,\
        prod_positions_train, prod_positions_test = train_test_split(
            self.features, self.positions, self.labels, self.probas, self.queries, self.prod_positions, test_size=test_size, shuffle=True
        )

        test_pool, train_pool = Pool(), Pool()
        test_pool.set(features_test, positions_test, proba_test, labels_test, queries_test, prod_positions_test)
        train_pool.set(features_train, positions_train, proba_train, labels_train, queries_train, prod_positions_train)

        return train_pool, test_pool

    def split_by_queries(self):
        POOLS_NUMBER = 3
        words = {word for query in self.queries for word in query}
        words_wins = {word: [] for word in words}
        for label, query in zip(self.labels, self.queries):
            for word in query:
                words_wins[word].append(label)
        word_avarage_wins = {
            word: np.mean(words_wins[word])
            for word in words_wins
        }

        pools = [Pool() for i in range(POOLS_NUMBER)]

        for feature, position, proba, label, queries, prod_positions in zip(self.features, self.positions, self.probas, self.labels, self.queries, self.prod_positions):
            average_win = np.mean([word_avarage_wins[word] for word in queries])
            index = 0 if average_win < 0 else 1 if average_win == 0 else 2
            pools[index].features.append(feature)
            pools[index].positions.append(position)
            pools[index].probas.append(proba)
            pools[index].labels.append(label)
            pools[index].queries.append(queries)
            pools[index].prod_positions.append(prod_positions)

        for pool in pools:
            pool.features = np.array(pool.features)
            pool.positions = np.array(pool.positions)
            pool.probas = np.array(pool.probas)
            pool.labels = np.array(pool.labels)
            pool.queries = np.array(pool.queries)
            pool.prod_positions = np.array(pool.prod_positions)

        return pools
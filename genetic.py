from typing import List, Tuple
from random import shuffle, sample, randrange
from copy import deepcopy
from multiprocessing import Pool
from common import transform_result, save_result, Instance, Library, score, get_scanable_books
import itertools


class Chromosome:

    mutation_probability = 0.75

    def __init__(self, instance: Instance):
        self.days = instance.days
        self.libraries = shuffle(deepcopy(instance.libraries))  # initialize with random solution
        self.split = 0
        self.score = 0
        self.calculate_split_and_score()

    def calculate_split_and_score(self):
        start = 0
        sc = 0
        books_scanned = set()
        for it, _, library in enumerate(self.libraries):
            books = get_scanable_books(library, self.days, start, books_scanned)
            if not books:
                continue
            else:
                self.split = it + 1

            sc += sum(list(map(lambda x: x[1], books)))
            books_scanned = books_scanned.union(set(books))
            library.books_chosen_num = len(books)
            start += library.signup
        self.score = sc

    def mutate(self):
        """
        mutation strategy version 1
        swap single library from above and below split point
        at this point algorithm always tries to apply mutation (probability of mutation is 1)
        :return:
        """
        self.calculate_split_and_score()
        libs = self.libraries.copy()
        a = randrange(0, self.split)
        b = randrange(self.split, len(self.libraries))
        libs[a], libs[b] = libs[b], libs[a]
        sc = score(libs, self.days)
        if sc > self.score:
            self.libraries = libs


def tournament(chromosomes: List[Chromosome], k=4) -> Chromosome:
    chosen = sample(chromosomes, k)
    m = (0, 0)
    for it, c in enumerate(chosen):
        if c.score > m[1]:
            m = (it, c.score)
    return chosen[m[0]]


def crossover(a: Chromosome, b: Chromosome) -> Tuple[Chromosome, Chromosome]:
    a = deepcopy(a)
    b = deepcopy(b)
    # TODO
    return a, b


def tournament_and_crossover(chromosomes: List[Chromosome], k=4) -> Tuple[Chromosome, Chromosome]:
    a = tournament(chromosomes, k)
    b = tournament(chromosomes, k)
    return crossover(a, b)


def chromosome_factory(instance: Instance) -> Chromosome:
    return Chromosome(instance)


def flatten(pre_population: List[Tuple[Chromosome, Chromosome]]) -> List[Chromosome]:
    return list(itertools.chain.from_iterable(pre_population))


def mutate(c: Chromosome) -> Chromosome:
    c.mutate()
    c.calculate_split_and_score()
    return c


def genetic(instance: Instance, size=64, iterations=10**4, k=4) -> List[Tuple[int, Library]]:
    """
    genetic algorithm version 1
    :param instance: instance object
    :param size: population size
    :param iterations: number of iterations
    :param k: tournament size
    :return:
    """
    p = Pool()
    population = p.map(chromosome_factory, [instance for _ in range(size)])
    result = deepcopy(population[0])
    for iteration in range(iterations):
        pre = p.map(tournament_and_crossover, [(population, k) for _ in range(size//2)])
        population = flatten(pre)
        population = p.map(mutate, population)
        print(max(list(map(lambda x: x.score, population))))
        cb = 0
        for p in population:
            if p.score > cb:
                cb = p.score
            if p.score > result.score:
                result = deepcopy(p)
        print(iteration, result.score, cb, sep='\t')

    return result.libraries
    

if __name__ == '__main__':

    files = ['a_example.txt',
             'b_read_on.txt',
             'c_incunabula.txt',
             'd_tough_choices.txt',
             'e_so_many_books.txt',
             'f_libraries_of_the_world.txt']
    file = files[1]

    i = Instance(file)
    print(i.num_books)
    print(score(i.libraries, i.days))
    print('--------')

    r = genetic(i, size=64, iterations=100, k=4)

    print('--------')
    save_result(transform_result(r, i.days), 'output/' + file[0] + '_genetic.out')

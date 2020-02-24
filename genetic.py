from typing import List, Tuple
from random import shuffle, sample, randrange
from copy import deepcopy
from multiprocessing import Pool
from common import transform_result, save_result, Instance, Library, score, get_scanable_books
import itertools
from time import time


class Chromosome:

    mutation_probability = 0.75

    def __init__(self, instance: Instance):
        self.days = instance.days
        self.libraries = deepcopy(instance.libraries)  # initialize with random solution
        shuffle(self.libraries)
        self.split = 0
        self.score = 0
        self.calculate_split_and_score()

    def calculate_split_and_score(self):
        start = 0
        sc = 0
        books_scanned = set()
        for it, tup in enumerate(self.libraries):
            library = tup[1]
            books = get_scanable_books(library, self.days, start, books_scanned)
            if not books:
                library.books_chosen_num = 0
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
        b = randrange(self.split if self.split != len(self.libraries) else 0, len(self.libraries))
        libs[a], libs[b] = libs[b], libs[a]
        sc = score(libs, self.days)
        if sc > self.score:
            self.libraries = libs

    def reorder_libraries(self):
        """
        reorder libraries to move libraries with 0 books scanned to the end of the libraries list
        :return:
        """
        kickoffs = []
        for j in range(self.split):
            lib = self.libraries[j]
            if lib[1].books_chosen_num == 0:
                kickoffs.append(j)

        kickoffs.reverse()
        for j in kickoffs:
            self.libraries.append(self.libraries.pop(j))


def tournament(chromosomes: List[Chromosome], k=4) -> Chromosome:
    chosen = sample(chromosomes, k)
    m = (0, 0)
    for it, c in enumerate(chosen):
        if c.score > m[1]:
            m = (it, c.score)
    return chosen[m[0]]


def crossover(a: Chromosome, b: Chromosome) -> Tuple[Chromosome, Chromosome]:
    ap = deepcopy(a)
    bp = deepcopy(b)
    ap.reorder_libraries()
    bp.reorder_libraries()
    # choose split point
    split = min(ap.split, bp.split)
    point = randrange(1, split)

    a_libs = ap.libraries[:point]
    a_ids = set(map(lambda x: x[0], a_libs))
    b_libs = bp.libraries[:point]
    b_ids = set(map(lambda x: x[0], b_libs))

    for it, l in bp.libraries:
        if it not in a_ids:
            a_libs.append((it, l))
    for it, l in ap.libraries:
        if it not in b_ids:
            b_libs.append((it, l))

    assert len(a_libs) == len(b_libs) == len(ap.libraries) == len(bp.libraries)
    ap.libraries = a_libs
    bp.libraries = b_libs

    return ap, bp


def tournament_and_crossover(chromosomes: List[Chromosome], k=4) -> Tuple[Chromosome, Chromosome]:
    a = tournament(chromosomes, k)
    b = tournament(chromosomes, k)
    return crossover(a, b)


def chromosome_factory(instance: Instance) -> Chromosome:
    return Chromosome(instance)


def flatten(pre_population: List[Tuple[Chromosome, Chromosome]]) -> List[Chromosome]:
    return list(itertools.chain.from_iterable(pre_population))


def mutate(c: Chromosome) -> Chromosome:
    for _ in range(5):
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
    print('Setup done')
    for iteration in range(iterations):
        start = time()
        pre = p.starmap(tournament_and_crossover, [(population, k) for _ in range(size//2)])
        population = flatten(pre)
        population = p.map(mutate, population)
        # print(max(list(map(lambda x: x.score, population))))
        cb = 0
        for pop in population:
            if pop.score > cb:
                cb = pop.score
            if pop.score > result.score:
                result = deepcopy(pop)
        print(iteration, result.score, cb, len(set(map(lambda x: x.score, population))), time() - start, sep='\t')

    return result.libraries
    

if __name__ == '__main__':

    files = ['a_example.txt',
             'b_read_on.txt',
             'c_incunabula.txt',
             'd_tough_choices.txt',
             'e_so_many_books.txt',
             'f_libraries_of_the_world.txt']
    file = files[4]

    i = Instance('input/' + file)
    print(i.num_books)
    print(score(i.libraries, i.days))
    print('--------')

    r = genetic(i, size=24, iterations=100, k=4)

    print('--------')
    save_result(transform_result(r, i.days), 'output/' + file[0] + '_genetic.out')

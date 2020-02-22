from typing import List, Tuple
from random import shuffle
from copy import deepcopy
from multiprocessing import Pool
from common import transform_result, save_result, Instance, Library, score


def just_shuffle(instance: Instance):
    libraries = instance.libraries.copy()
    best_libra = libraries.copy()
    best_score = score(best_libra, instance.days)
    for _ in range(10**4):
        current = libraries.copy()
        shuffle(current)
        current_score = score(current, instance.days)
        # print(current_score)
        if current_score > best_score:
            best_libra = current
            best_score = current_score
            print(best_score)
    return best_libra


def just_shuffle_operation(instance: Instance):
    return transform_result(just_shuffle(instance), instance.days)


def do_nothing_operation(instance: Instance):
    return transform_result(instance.libraries.copy(), instance.days)


def perform_on_population(instance: Instance, size=16, func=do_nothing_operation):
    population = []
    for _ in range(size):
        dc = deepcopy(instance)
        population.append(dc)
    p = Pool()
    return p.map(func, population)
    

if __name__ == '__main__':

    files = ['a_example.txt',
             'b_read_on.txt',
             'c_incunabula.txt',
             'd_tough_choices.txt',
             'e_so_many_books.txt',
             'f_libraries_of_the_world.txt']
    file = files[2]

    instance = Instance(file)
    print(instance.books)
    print(score(instance.libraries, instance.days))
    print('--------')

    # instance.libraries[0][1].print()

    # result = just_shuffle(instance);

    results = perform_on_population(instance, size=4, func=just_shuffle)

    print('--------')
    # print(score(result, instance.days))
    print(list(map(lambda x: score(x, instance.days), results)))

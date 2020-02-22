from multiprocessing import Pool
from typing import List, Tuple
from common import Library, Instance, save_result, transform_result, score, get_scanable_books


def basic(instance: Instance) -> List[Tuple[int, Library]]:
    """
    Basic `sophisticated` heuristic approach.
    Works fast except instance D
    :param instance:
    :return:
    """
    ranking = []
    start = 0
    books_scanned = set()
    libraries_signed = list()
    while start < instance.days:
        lib_rank = []
        did_change = False
        for it, library in instance.libraries:
            if it in libraries_signed:
                continue
            if start + library.signup >= instance.days:
                continue
            did_change = True

            books = get_scanable_books(library, instance.days, start, books_scanned)
            sc = sum(list(map(lambda x: x[1], books)))

            lib_rank.append((it, sc))

        if not did_change:
            print('No change done')
            break

        lib_rank.sort(key=lambda x: x[1], reverse=True)

        chosen = instance.libraries[lib_rank[0][0]]

        temp_books = get_scanable_books(chosen[1], instance.days, start, books_scanned)
        books_scanned = books_scanned.union(set(temp_books))

        start += chosen[1].signup
        ranking.append(chosen)
        libraries_signed.append(lib_rank[0][0])

    return ranking


def sort_by_setup_time_desc(instance: Instance) -> List[Tuple[int, Library]]:
    libraries = instance.libraries.copy()
    libraries.sort(key=lambda x: x[1].signup)

    return libraries


def do_basic(filename: str):
    instance = Instance('input/' + filename)
    result = basic(instance)
    print(filename[0], score(result, instance.days))
    save_result(transform_result(result, instance.days), 'output/' + filename[0] + '_result.out')


if __name__ == '__main__':
    files = ['a_example.txt',
             'b_read_on.txt',
             'c_incunabula.txt',
             # 'd_tough_choices.txt',
             'e_so_many_books.txt',
             'f_libraries_of_the_world.txt']

    p = Pool()
    p.map(do_basic, files)
    print('done parallel')

    file_d = 'd_tough_choices.txt'

    i = Instance('input/' + file_d)
    r = sort_by_setup_time_desc(i)
    print('d', score(r, i.days))
    t = transform_result(r, i.days)
    save_result(t, 'output/d_result.out')
    print('done d')

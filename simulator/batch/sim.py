'''
2020 Mark Shui Hu, QuTech

www.github.com/watermarkhu/oop_surface_code
_____________________________________________

'''
import sys
import multiprocessing as mp
from .sql import writeline, get_columns, connect_database, create_table, insert_database


def multiple(
    path,
    database,
    graph,
    size,
    config,
    iters,
    paulix=0,
    worker=0,
    debug=True,
    **kwargs
):
    from ..main import init_random_seed, single, get_mean_var
    from ..info.decorators import debug as db


    """
    Runs the peeling decoder for a number of iterations. The graph is reused for speedup.
    """

    seeds = [init_random_seed(worker=worker, iteration=iter) for iter in range(iters)]

    options = dict(
        graph=graph,
        worker=worker,
        called=0,
        debug=True,
    )

    zipped = zip(range(iters), seeds)
    result = [single(size, config, paulix=paulix, iter=iter, seed=seed, **options, **kwargs) for iter, seed in zipped]

    output = dict(
        N       = iters,
        succes  = sum(result)
    )
    if debug:
        output.update(**get_mean_var(graph.matching_weight, "weight"))
        for key, value in graph.decoder.clist.items():
            output.update(**get_mean_var(value, key))
        db.reset_counters(graph)

    data = dict(L=size, p=paulix, **output)

    print(",".join([str(x) for x in data.values()]))

    # Write to csv file
    if path:
        values = [str(data[key]) for key in get_columns()]
        writeline(path, worker, ",".join(values))

    # Save to SQL database
    if database:
        table = f"N{worker}"
        con = connect_database(database)
        insert_database(con, table, data)
        con.close()


def multiprocess(
        path,
        database,
        graph,
        size,
        config,
        iters,
        processes,
        node=0,
        **kwargs
    ):
    """
    Runs the peeling decoder for a number of iterations, split over a number of processes
    """

    process_iters = iters // processes
    workers = []

    for i, g in enumerate(graph, int(node*processes)):
        workers.append(
            mp.Process(
                target=multiple,
                args=(path, database, g, size, config, process_iters),
                kwargs=dict(worker=i, **kwargs),
            )
        )
    print("Starting", processes, "workers.")

    for worker in workers:
        worker.start()

    for worker in workers:
        worker.join()


def sim_thresholds(
        decoder,
        node=0,
        lattice_type="toric",
        lattices = [],
        perror = [],
        iters = 0,
        processes=1,
        measurement_error=False,
        database="",
        outputfolder="",
        P_store=1000,
        debug=False,
        **kwargs
        ):
    '''
    ############################################
    '''
    from ..main import default_config, lattice_type as makegraph
    if measurement_error:
        from ..graph import graph_3D as go
    else:
        from ..graph import graph_2D as go

    sys.setrecursionlimit(100000)

    progressbar = kwargs.pop("progressbar")

    int_P = [int(p*P_store) for p in perror]
    config = default_config(**kwargs)


    # Create output files
    if outputfolder:
        path = outputfolder + "/" + database + "N"
        for i, _ in enumerate(range(processes), node*processes):
            writeline(path, i, ",".join(get_columns()), type="w")
    else:
        path = ""

    # Create SQL tables
    if database:
        con = connect_database(database)
        for i in range(processes):
            p = i + node*processes
            create_table(con, f"N{p}")
        con.close()


    # Simulate and save results to file
    for lati in lattices:

        graph = [makegraph(lattice_type, config, decoder, go, lati) for _ in range(processes)]

        for pi, int_p in zip(perror, int_P):

            print("Calculating for L = ", str(lati), "and p =", str(pi))

            oopsc_args = dict(
                paulix=pi,
                lattice_type=lattice_type,
                debug=debug,
                progressbar=progressbar
            )
            if measurement_error:
                oopsc_args.update(measurex=pi)

            multiprocess(path, database, graph, lati, config, iters, processes, node, **oopsc_args)

"""
GRASP (Greedy Randomized Adaptive Search Procedure).

Sa ka kohë:
  1. ndërtim greedy i rastësishëm me RCL (ndertimi.nderto_grasp), ku kostoja
     e çdo harku llogaritet me trigger-at e prefiksit;
  2. kërkim lokal deri në optimum lokal (levizjet.kerkim_lokal);
  3. ruhet zgjidhja më e mirë.

alfa zgjidhet rastësisht në [alfa_min, alfa_max] në çdo iteracion
("reactive" e thjeshtë), që të ketë edhe rrugë afër greedy, edhe më të ndryshme.
Iteracionet janë të pavarura nga njëra-tjetra.
"""
import random
import time

from kosto import Gjendja, vlereso_nga
from levizjet import kerkim_lokal
from ndertimi import nderto_grasp


def grasp(ktx, seed=1, koha_max=60.0, alfa_min=0.0, alfa_max=0.3,
          maks_segment=None, maks_iteracione=10**9):
    g = random.Random(seed)
    n = ktx.n
    if maks_segment is None:
        maks_segment = max(3, n // 4)    # lagje më e vogël = më shumë iteracione

    fillimi = time.perf_counter()
    koha_fund = fillimi + koha_max

    me_e_mira = None
    kosto_fillestare = None
    historia = []
    iteracione = 0
    deshtime = 0
    me_prerje = False

    while time.perf_counter() < koha_fund and iteracione < maks_iteracione:
        alfa = g.uniform(alfa_min, alfa_max)
        rruga = nderto_grasp(ktx, alfa, g, me_prerje=me_prerje)
        if rruga is None:
            deshtime += 1
            # Në grafe të rralla ndërtimi i thjeshtë mund të mos ketë sukses
            # asnjëherë: pas 200 dështimeve rresht pa asnjë rrugë, ndizet prerja.
            if not me_prerje and me_e_mira is None and deshtime >= 200:
                me_prerje = True
            continue

        gjendja = Gjendja(ktx, rruga)
        if kosto_fillestare is None:
            kosto_fillestare = gjendja.kosto

        kerkim_lokal(ktx, gjendja, g, maks_segment, koha_fund, vlereso_nga)
        iteracione += 1

        if me_e_mira is None or gjendja.kosto < me_e_mira.kosto - 1e-9:
            me_e_mira = gjendja
            historia.append((time.perf_counter() - fillimi, gjendja.kosto))

    if me_e_mira is None:
        raise RuntimeError("GRASP nuk ndërtoi asnjë rrugë të vlefshme brenda kohës.")

    return {
        "rruga": me_e_mira.nyjet,
        "kosto": me_e_mira.kosto,
        "kosto_fillestare": kosto_fillestare,
        "iteracione": iteracione,
        "deshtime": deshtime,
        "me_prerje": me_prerje,
        "historia": historia,
    }
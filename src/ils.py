"""
Iterated Local Search (ILS).

  1. nis nga rruga fillestare (backtracking) dhe bën kërkim lokal;
  2. sa ka kohë: perturbo zgjidhjen më të mirë me disa lëvizje të rastit,
     bëj kërkim lokal, dhe nëse rezultati është më i mirë, ruaje.

Perturbimi duhet të jetë mjaft i fortë për ta nxjerrë rrugën nga optimumi
lokal, por jo aq sa të humbë gjithë strukturën e mirë (3 lëvizje si parazgjedhje).
"""
import random
import time

from kosto import Gjendja, vlereso_nga
from levizjet import kerkim_lokal, perturbo


def iterated_local_search(ktx, rruga_fillestare, seed=1, koha_max=60.0,
                          forca_perturbimit=3, maks_segment=None,
                          maks_iteracione=10**9):
    g = random.Random(seed)
    n = ktx.n
    if maks_segment is None:
        maks_segment = n - 2             # lagje e plotë: segment me çdo gjatësi

    fillimi = time.perf_counter()
    koha_fund = fillimi + koha_max

    gjendja = Gjendja(ktx, rruga_fillestare)
    kosto_fillestare = gjendja.kosto
    kerkim_lokal(ktx, gjendja, g, maks_segment, koha_fund, vlereso_nga)
    me_e_mira = gjendja
    historia = [(time.perf_counter() - fillimi, me_e_mira.kosto)]
    iteracione = 1

    while time.perf_counter() < koha_fund and iteracione < maks_iteracione:
        nyjet = perturbo(me_e_mira.nyjet, ktx.hs, g, forca_perturbimit, maks_segment)
        gjendja = Gjendja(ktx, nyjet)
        kerkim_lokal(ktx, gjendja, g, maks_segment, koha_fund, vlereso_nga)
        iteracione += 1

        if gjendja.kosto < me_e_mira.kosto - 1e-9:
            me_e_mira = gjendja
            historia.append((time.perf_counter() - fillimi, me_e_mira.kosto))

    return {
        "rruga": me_e_mira.nyjet,
        "kosto": me_e_mira.kosto,
        "kosto_fillestare": kosto_fillestare,
        "iteracione": iteracione,
        "historia": historia,
    }

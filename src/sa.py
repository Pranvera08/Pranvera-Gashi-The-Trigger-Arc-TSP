"""
Simulated Annealing (versioni i përmirësuar).

Ndryshimet nga versioni i parë (ta_tsp.py):
- segmentet e insertion deri në n/2 nyje (jo vetëm 1-3);
- vlerësim i pjesshëm dhe ndërprerje e hershme.

Pranimi: një kandidat më i keq me ndryshim d pranohet me probabilitet e^(-d/T).
E njëjta gjë fitohet nëse zgjidhet u ~ U(0,1) PARA vlerësimit dhe pranohet
kandidati kur d <= -T * ln(u). Kështu dihet që më parë kufiri
kosto_aktuale - T * ln(u), dhe vlerësimi ndërpritet sapo e kalon atë.
"""
import math
import random
import time

from kosto import Gjendja, vlereso_nga
from levizjet import levizje_e_rastit


def simulated_annealing(ktx, rruga_fillestare, seed=1, koha_max=60.0,
                        iteracione=10**9, maks_segment=None,
                        kufiri_pa_permiresim=20000):
    g = random.Random(seed)
    hs = ktx.hs
    n = ktx.n
    if maks_segment is None:
        maks_segment = max(3, n // 2)

    aktuale = Gjendja(ktx, rruga_fillestare)
    me_e_mira = aktuale.kopje()
    kosto_fillestare = aktuale.kosto
    historia = [(0.0, me_e_mira.kosto)]

    # temperatura lidhet me koston mesatare të një harku
    T0 = ktx.kosto_mesatare * 0.5
    T1 = ktx.kosto_mesatare * 0.001
    T = T0

    fillimi = time.perf_counter()
    pa_permiresim = 0
    kryer = 0

    for it in range(iteracione):
        if it % 100 == 0:
            progresi = max(it / iteracione,
                           (time.perf_counter() - fillimi) / koha_max)
            if progresi >= 1:
                break
            T = T0 * (T1 / T0) ** progresi
        kryer = it + 1

        r = levizje_e_rastit(aktuale.nyjet, hs, g, maks_segment)
        if r is None:
            continue
        kandidati, s = r

        u = g.random()
        kufiri = aktuale.kosto - T * math.log(u) if u > 0 else math.inf
        rez = vlereso_nga(ktx, aktuale, kandidati, s, kufiri=kufiri)
        if rez is None:
            pa_permiresim += 1
        else:
            aktuale.prano(kandidati, rez)
            if aktuale.kosto < me_e_mira.kosto - 1e-9:
                me_e_mira = aktuale.kopje()
                historia.append((time.perf_counter() - fillimi, me_e_mira.kosto))
                pa_permiresim = 0
            else:
                pa_permiresim += 1

        # rinisje nga më e mira kur ngec gjatë
        if pa_permiresim > kufiri_pa_permiresim:
            aktuale = me_e_mira.kopje()
            pa_permiresim = 0

    return {
        "rruga": me_e_mira.nyjet,
        "kosto": me_e_mira.kosto,
        "kosto_fillestare": kosto_fillestare,
        "iteracione": kryer,
        "historia": historia,
    }

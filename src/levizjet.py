"""
Lëvizjet në hapësirën e zgjidhjeve dhe kërkimi lokal.

Rruga ka formën [0, v1, ..., v(n-1), 0]. Lëvizjet nuk e prekin nyjën 0
në fillim dhe në fund, prandaj rruga mbetet cikël Hamiltonian nga 0.

Secila lëvizje kthen (rruga_kandidate, s), ku s është pozita e harkut të parë
që ndryshoi. Kjo i lejon kosto.vlereso_nga() të mos i rillogarisë harqet 0 .. s-1.
Kthen None nëse lëvizja krijon një hark që nuk ekziston.

Insertion me segment të gjatë = 3-opt që e ruan drejtimin e harqeve.
Kjo ka rëndësi sepse grafi është i orientuar: 2-opt klasik e kthen mbrapsht
një segment dhe i ndryshon harqet.
"""
import time


def levizje_insertion(nyjet, hs, g, maks_segment):
    """Heq një segment me 1 .. maks_segment nyje dhe e fut në një pozitë tjetër."""
    n = len(nyjet) - 1
    gjatesia = g.randint(1, max(1, min(maks_segment, n - 2)))
    i = g.randint(1, n - gjatesia)

    segmenti = nyjet[i:i + gjatesia]
    pa_segment = nyjet[:i] + nyjet[i + gjatesia:]

    # harku që mbyll vendin nga u hoq segmenti
    if (pa_segment[i - 1], pa_segment[i]) not in hs:
        return None

    j = g.randint(1, len(pa_segment) - 1)      # segmenti futet para pa_segment[j]
    if j == i:
        return None
    if (pa_segment[j - 1], segmenti[0]) not in hs:
        return None
    if (segmenti[-1], pa_segment[j]) not in hs:
        return None

    return pa_segment[:j] + segmenti + pa_segment[j:], min(i, j) - 1


def levizje_swap(nyjet, hs, g):
    """Ndërron vendet e dy nyjeve."""
    n = len(nyjet) - 1
    p1, p2 = sorted(g.sample(range(1, n), 2))

    kandidati = nyjet[:]
    kandidati[p1], kandidati[p2] = kandidati[p2], kandidati[p1]

    for k in {p1 - 1, p1, p2 - 1, p2}:
        if (kandidati[k], kandidati[k + 1]) not in hs:
            return None

    return kandidati, p1 - 1


def levizje_e_rastit(nyjet, hs, g, maks_segment, gjasa_insertion=0.7):
    """70% insertion, 30% swap (si te versioni i parë i SA)."""
    if g.random() < gjasa_insertion:
        return levizje_insertion(nyjet, hs, g, maks_segment)
    return levizje_swap(nyjet, hs, g)


def perturbo(nyjet, hs, g, numri, maks_segment, maks_prova=10000):
    """Bën 'numri' lëvizje të rastit të vlefshme (përdoret nga ILS)."""
    kryer = 0
    for _ in range(maks_prova):
        if kryer == numri:
            break
        r = levizje_insertion(nyjet, hs, g, maks_segment)
        if r is not None:
            nyjet = r[0]
            kryer += 1
    return nyjet


def kerkim_lokal(ktx, gjendja, g, maks_segment, koha_fund, vlereso_nga):
    """
    First-improvement: provon lëvizjet në rend të rastit dhe e pranon
    përmirësimin e parë; përsërit derisa asnjë lëvizje të mos e përmirësojë
    rrugën (optimum lokal) ose të mbarojë koha.

    Lagjja: të gjitha insertion me segment 1 .. maks_segment dhe të gjitha swap.
    Falë ndërprerjes së hershme (kufiri = kostoja aktuale), shumica e
    kandidatëve të këqij refuzohen pa e llogaritur gjithë rrugën.
    Kthen numrin e përmirësimeve.
    """
    hs = ktx.hs
    n = ktx.n
    maks_segment = max(1, min(maks_segment, n - 2))
    permiresime = 0

    while time.perf_counter() < koha_fund:
        nyjet = gjendja.nyjet
        u_permiresua = False

        lista = [("ins", gj, i) for gj in range(1, maks_segment + 1)
                 for i in range(1, n - gj + 1)]
        lista += [("swap", a, 0) for a in range(1, n - 1)]
        g.shuffle(lista)

        for lloji, x, i in lista:
            if lloji == "ins":
                gj = x
                segmenti = nyjet[i:i + gj]
                pa_segment = nyjet[:i] + nyjet[i + gj:]
                if (pa_segment[i - 1], pa_segment[i]) not in hs:
                    continue
                for j in range(1, len(pa_segment)):
                    if j == i:
                        continue
                    if (pa_segment[j - 1], segmenti[0]) not in hs:
                        continue
                    if (segmenti[-1], pa_segment[j]) not in hs:
                        continue
                    kandidati = pa_segment[:j] + segmenti + pa_segment[j:]
                    r = vlereso_nga(ktx, gjendja, kandidati, min(i, j) - 1,
                                    kufiri=gjendja.kosto - 1e-9)
                    if r is not None:
                        gjendja.prano(kandidati, r)
                        u_permiresua = True
                        break
            else:
                a = x
                for b in range(a + 1, n):
                    kandidati = nyjet[:]
                    kandidati[a], kandidati[b] = kandidati[b], kandidati[a]
                    if any((kandidati[k], kandidati[k + 1]) not in hs
                           for k in (a - 1, a, b - 1, b)):
                        continue
                    r = vlereso_nga(ktx, gjendja, kandidati, a - 1,
                                    kufiri=gjendja.kosto - 1e-9)
                    if r is not None:
                        gjendja.prano(kandidati, r)
                        u_permiresua = True
                        break

            if u_permiresua or time.perf_counter() >= koha_fund:
                break

        if not u_permiresua:
            break
        permiresime += 1

    return permiresime

"""
Ndërtimi i rrugëve:
- nderto_rruge_fillestare: backtracking (greedy sipas kostos bazë + kthim pas),
  zgjidhja fillestare për SA dhe ILS;
- nderto_grasp: ndërtim greedy i rastësishëm me RCL, që përdor koston e
  VËRTETË me trigger-a (faza e parë e GRASP).
"""


def nderto_rruge_fillestare(n, harqet):
    """
    Kërkon një cikël fillestar, duke u kthyer pas kur ngec.
    Kërkimi bëhet me stivë (pa rekursion), që të mos kalohet
    kufiri i rekursionit të Python-it në instanca të mëdha.
    """

    harqet_nga_nyja = {}

    for harku in harqet.values():
        harqet_nga_nyja.setdefault(harku.prej, []).append(harku)

    # Provojmë fillimisht harqet me kosto më të ulët
    for lista in harqet_nga_nyja.values():
        lista.sort(key=lambda harku: harku.kosto)

    lidhjet = {
        (harku.prej, harku.deri)
        for harku in harqet.values()
    }

    rruga = [0]
    vizituar = [False] * n
    vizituar[0] = True

    # Për çdo nivel të kërkimit ruajmë indeksin e kandidatit të radhës
    stiva = [0]
    vizita = 0
    kufiri_i_kerkimit = 1_000_000

    while stiva and vizita < kufiri_i_kerkimit:
        vizita += 1
        nyja_aktuale = rruga[-1]

        if len(rruga) == n:
            # Të gjitha nyjet janë vizituar: duhet hark kthimi te 0
            if (nyja_aktuale, 0) in lidhjet:
                rruga.append(0)
                return rruga
        else:
            kandidatet = harqet_nga_nyja.get(nyja_aktuale, [])
            i = stiva[-1]

            while i < len(kandidatet) and vizituar[kandidatet[i].deri]:
                i += 1

            if i < len(kandidatet):
                stiva[-1] = i + 1
                nyja_tjeter = kandidatet[i].deri
                vizituar[nyja_tjeter] = True
                rruga.append(nyja_tjeter)
                stiva.append(0)
                continue

        # Kthehemi pas dhe provojmë një hark tjetër
        stiva.pop()
        nyja_e_hequr = rruga.pop()
        vizituar[nyja_e_hequr] = False

        if not rruga:
            break

    raise ValueError(
        "Nuk u gjet cikël fillestar brenda kufirit të kërkimit."
    )


def nderto_grasp(ktx, alfa, g):
    """
    Ndërton një rrugë nga nyja 0. Në çdo hap:
      1. për çdo fqinj të pavizituar llogaritet kostoja e harkut me trigger-at
         e prefiksit (prefiksi është tashmë i fiksuar, pra kostoja është e saktë);
      2. RCL = kandidatët me kosto <= c_min + alfa * (c_max - c_min);
      3. zgjidhet rastësisht një kandidat nga RCL.
    alfa = 0 -> greedy i pastër, alfa = 1 -> krejt i rastit.
    Kthen rrugën ose None nëse ndërtimi ngec (nuk ka vazhdim ose kthim te 0).
    """
    n = ktx.n
    hs = ktx.hs
    tabela = ktx.tabela
    baze = ktx.kostot_baze
    m = ktx.m

    rruga = [0]
    vizituar = [False] * n
    vizituar[0] = True
    rreshtat = []

    while len(rruga) < n:
        u = rruga[-1]
        kandidatet = []

        for v in ktx.fqinjet[u]:
            if vizituar[v]:
                continue
            # Nëse kjo është nyja e fundit, duhet të ketë hark kthimi te 0
            if len(rruga) == n - 1 and (v, 0) not in hs:
                continue
            i = hs[(u, v)]
            c = baze[i]
            for rr in reversed(rreshtat):
                vlera = tabela[rr + i]
                if vlera == vlera:
                    c = vlera
                    break
            kandidatet.append((c, v, i))

        if not kandidatet:
            return None

        c_min = min(k[0] for k in kandidatet)
        c_max = max(k[0] for k in kandidatet)
        pragu = c_min + alfa * (c_max - c_min)
        rcl = [k for k in kandidatet if k[0] <= pragu]

        _, v, i = g.choice(rcl)
        rruga.append(v)
        vizituar[v] = True
        rreshtat.append(i * m)

    rruga.append(0)
    return rruga

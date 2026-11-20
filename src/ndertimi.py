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

    # Në grafe të rralla (p.sh. grupi i dytë i instancave) kërkimi i thjeshtë
    # nuk gjen cikël; atëherë përdoret kërkimi me Warnsdorff dhe prerje.
    rruga = nderto_rruge_warnsdorff(n, harqet)
    if rruga is not None:
        return rruga

    raise ValueError(
        "Nuk u gjet cikël fillestar brenda kufirit të kërkimit."
    )


def nderto_rruge_warnsdorff(n, harqet, prova=200, kufiri_per_prove=20_000, seed=0):
    """
    Kërkim me kthim pas për grafe të rralla, me dy përmirësime:

    1. Rregulli i Warnsdorff-it: fillimisht provohet fqinji që ka më PAK
       vazhdime të lira (nyjet "e vështira" vizitohen sa kanë ende rrugë),
       me koston bazë si kriter të dytë.
    2. Prerja: një degë braktiset menjëherë nëse ndonjë nyje e pavizituar
       nuk ka më asnjë hyrje të mundshme, ose asnjë dalje të mundshme
       (drejt nyjeve të pavizituara ose drejt 0), ose nëse nuk ka mbetur
       asnjë nyje e pavizituar me hark kthimi te 0.

    Nëse një provë e kalon kufirin, nis provë e re me rend paksa të rastësuar.
    Kthen rrugën [0, ..., 0] ose None.
    """
    import random
    g = random.Random(seed)

    dalje = [[] for _ in range(n)]
    hyrje = [[] for _ in range(n)]
    kosto = {}
    for h in harqet.values():
        dalje[h.prej].append(h.deri)
        hyrje[h.deri].append(h.prej)
        kosto[(h.prej, h.deri)] = h.kosto
    kthim = {u for u in range(n) if 0 in dalje[u]}

    def e_mundshme(vizituar, aktuale, mbetur):
        if mbetur == 0:
            return True
        if not any(not vizituar[u] for u in kthim):
            return False
        for v in range(1, n):
            if vizituar[v]:
                continue
            # duhet të ketë hyrje nga një nyje e pavizituar ose nga nyja aktuale
            if not any((not vizituar[u]) or u == aktuale for u in hyrje[v]):
                return False
            # duhet të ketë dalje drejt një nyjeje të pavizituar, ose drejt 0
            # (vetëm nëse është e fundit)
            if not any((not vizituar[w]) or (w == 0 and mbetur == 1) for w in dalje[v]):
                return False
        return True

    for prova_nr in range(prova):
        zhurma = 0.0 if prova_nr == 0 else 0.5
        rruga = [0]
        vizituar = [False] * n
        vizituar[0] = True

        def rendit_kandidatet(u):
            kandidatet = [v for v in dalje[u] if not vizituar[v]]
            return sorted(kandidatet, key=lambda v: (
                sum(1 for w in dalje[v] if not vizituar[w]) + g.random() * zhurma * 2,
                kosto[(u, v)]))

        stiva = [rendit_kandidatet(0)]
        hapa = 0
        while stiva and hapa < kufiri_per_prove:
            hapa += 1
            if len(rruga) == n:
                if 0 in dalje[rruga[-1]]:
                    return rruga + [0]
                kandidatet = []
            else:
                kandidatet = stiva[-1]

            if kandidatet:
                v = kandidatet.pop(0)
                vizituar[v] = True
                rruga.append(v)
                if e_mundshme(vizituar, v, n - len(rruga)):
                    stiva.append(rendit_kandidatet(v))
                else:
                    vizituar[v] = False
                    rruga.pop()
                continue

            # kthim pas
            stiva.pop()
            if len(rruga) > 1:
                vizituar[rruga.pop()] = False
    return None


def _e_mundshme(ktx, vizituar, aktuale, mbetur):
    """
    Kontroll i shpejtë i prerjes: a mund të plotësohet ende cikli?
    False nëse ndonjë nyje e pavizituar nuk ka më hyrje ose dalje të mundshme,
    ose nëse nuk ka mbetur asnjë nyje e pavizituar me hark kthimi te 0.
    """
    if mbetur == 0:
        return (aktuale, 0) in ktx.hs
    hyrje, kthim = ktx._hyrje, ktx._kthim
    if not any(not vizituar[u] for u in kthim):
        return False
    for v in range(1, ktx.n):
        if vizituar[v]:
            continue
        if not any((not vizituar[u]) or u == aktuale for u in hyrje[v]):
            return False
        if not any((not vizituar[w]) or (w == 0 and mbetur == 1) for w in ktx.fqinjet[v]):
            return False
    return True


def _nderto_grasp_me_kthim(ktx, alfa, g, kufiri=None):
    """
    Ndërtimi GRASP për grafe të rralla: e njëjta zgjedhje me RCL dhe kosto të
    vërtetë me trigger-a, por me prerje dhe me kthim pas të kufizuar.
    Në çdo nivel provohen fillimisht kandidatët e RCL-së (në rend të rastit),
    pastaj të tjerët sipas kostos; nëse rruga ngec, kthehet një hap pas.
    """
    n, hs, tabela, baze, m = ktx.n, ktx.hs, ktx.tabela, ktx.kostot_baze, ktx.m
    kufiri = kufiri or 50 * n

    def kandidatet(rruga, vizituar, rreshtat):
        u = rruga[-1]
        lista = []
        for v in ktx.fqinjet[u]:
            if vizituar[v]:
                continue
            if len(rruga) == n - 1 and (v, 0) not in hs:
                continue
            vizituar[v] = True
            ok = _e_mundshme(ktx, vizituar, v, n - len(rruga) - 1)
            vizituar[v] = False
            if not ok:
                continue
            i = hs[(u, v)]
            c = baze[i]
            for rr in reversed(rreshtat):
                vlera = tabela[rr + i]
                if vlera == vlera:
                    c = vlera
                    break
            lista.append((c, v, i))
        if not lista:
            return []
        # Rregulli i Warnsdorff-it: fqinjët me më pak vazhdime të lira kanë
        # përparësi (përndryshe në grafe të rralla rruga ngec). RCL-ja sipas
        # kostos ndërtohet brenda fqinjëve me shkallë minimale (ose +1).
        shkalla = {v: sum(1 for w in ktx.fqinjet[v] if not vizituar[w]) for _, v, _ in lista}
        d_min = min(shkalla.values())
        te_veshtire = [k for k in lista if shkalla[k[1]] <= d_min + 1]
        c_min = min(k[0] for k in te_veshtire)
        c_max = max(k[0] for k in te_veshtire)
        pragu = c_min + alfa * (c_max - c_min)
        rcl = [k for k in te_veshtire if k[0] <= pragu]
        g.shuffle(rcl)
        tjeret = sorted((k for k in lista if k not in rcl),
                        key=lambda k: (shkalla[k[1]], k[0]))
        return rcl + tjeret

    rruga = [0]
    vizituar = [False] * n
    vizituar[0] = True
    rreshtat = []
    stiva = [kandidatet(rruga, vizituar, rreshtat)]
    hapa = 0
    while stiva and hapa < kufiri:
        hapa += 1
        if len(rruga) == n:
            return rruga + [0]
        if stiva[-1]:
            _, v, i = stiva[-1].pop(0)
            rruga.append(v)
            vizituar[v] = True
            rreshtat.append(i * m)
            if len(rruga) == n:
                return rruga + [0]
            stiva.append(kandidatet(rruga, vizituar, rreshtat))
            continue
        stiva.pop()
        if len(rruga) > 1:
            vizituar[rruga.pop()] = False
            rreshtat.pop()
    return None


def nderto_grasp(ktx, alfa, g, me_prerje=False):
    """
    Ndërton një rrugë nga nyja 0. Në çdo hap:
      1. për çdo fqinj të pavizituar llogaritet kostoja e harkut me trigger-at
         e prefiksit (prefiksi është tashmë i fiksuar, pra kostoja është e saktë);
      2. RCL = kandidatët me kosto <= c_min + alfa * (c_max - c_min);
      3. zgjidhet rastësisht një kandidat nga RCL.
    alfa = 0 -> greedy i pastër, alfa = 1 -> krejt i rastit.
    me_prerje = True: kandidatët që e bëjnë të pamundur plotësimin e ciklit
    hiqen paraprakisht (për grafe të rralla, ku ndërtimi i thjeshtë ngec).
    Kthen rrugën ose None nëse ndërtimi ngec (nuk ka vazhdim ose kthim te 0).
    """
    n = ktx.n
    hs = ktx.hs
    tabela = ktx.tabela
    baze = ktx.kostot_baze
    m = ktx.m

    if me_prerje and not hasattr(ktx, "_hyrje"):
        ktx._hyrje = [[] for _ in range(n)]
        for (a, b) in hs:
            ktx._hyrje[b].append(a)
        ktx._kthim = [u for u in range(n) if (u, 0) in hs]
    if me_prerje:
        return _nderto_grasp_me_kthim(ktx, alfa, g)

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
            if me_prerje:
                vizituar[v] = True
                ok = _e_mundshme(ktx, vizituar, v, n - len(rruga) - 1)
                vizituar[v] = False
                if not ok:
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
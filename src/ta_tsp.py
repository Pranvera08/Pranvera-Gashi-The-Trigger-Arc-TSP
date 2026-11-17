from dataclasses import dataclass

import csv
import math
import random
import time
from array import array
from pathlib import Path


@dataclass
class Harku:
    id: int
    prej: int
    deri: int
    kosto: float


def lexo_instancen(emri_skedarit):
    """
    Lexon nyjet, harqet dhe marrëdhëniet trigger nga skedari.

    Disa instanca (p.sh. grf15) kanë miliona marrëdhënie. Nëse secila
    ruhet si fjalor më vete, programi zë disa GB memorie dhe bëhet
    shumë i ngadalshëm. Prandaj marrëdhëniet ruhen në një tabelë kompakte:
    tabela[i_trigger * m + i_objektiv] = kosto e re
    ku i_trigger dhe i_objektiv janë pozitat e harqeve (0 .. m-1).
    Vlera NaN do të thotë që marrëdhënia nuk ekziston.
    """
    with open(emri_skedarit, "r", encoding="utf-8") as skedari:
        rreshtat = (
            rreshti.split()
            for rreshti in skedari
            if rreshti.strip() and not rreshti.lstrip().startswith("#")
        )

        try:
            koka = next(rreshtat)
        except StopIteration:
            raise ValueError("Skedari i instancës është bosh.")

        # Rreshti i parë: numri i nyjeve, harqeve dhe marrëdhënieve
        n, m, r = int(koka[0]), int(koka[1]), int(koka[2])

        harqet = {}

        # Rreshtat e harqeve: id, nyja prej, nyja deri, kostoja
        for _ in range(m):
            id_harku, prej, deri, kosto = next(rreshtat)
            id_harku = int(id_harku)
            harqet[id_harku] = Harku(
                id_harku, int(prej), int(deri), float(kosto)
            )

        # Pozita e çdo harku në tabelë (0 .. m-1)
        pozita_e_harkut = {
            id_harku: i for i, id_harku in enumerate(harqet)
        }

        tabela = array("d", [math.nan]) * (m * m)
        numri = 0

        # Rreshtat e marrëdhënieve trigger:
        # id, (id, prej, deri) e trigger-it, (id, prej, deri) e objektivit,
        # kosto e re. Na duhen vetëm id-të e harqeve dhe kostoja.
        for _ in range(r):
            rr = next(rreshtat)
            i_trigger = pozita_e_harkut[int(rr[1])]
            i_objektiv = pozita_e_harkut[int(rr[4])]
            tabela[i_trigger * m + i_objektiv] = float(rr[7])
            numri += 1

    marredheniet = {
        "tabela": tabela,
        "pozita_e_harkut": pozita_e_harkut,
        "numri": numri,
    }

    return n, harqet, marredheniet


def pergatit_indekset(harqet, marredheniet):
    """
    Përgatit hartat që përdoren gjatë kërkimit.
    Këto harta përgatiten një herë dhe ripërdoren.
    """
    pozita_e_harkut = marredheniet["pozita_e_harkut"]

    # (prej, deri) -> pozita e harkut në tabelë
    harku_sipas_nyjeve = {
        (harku.prej, harku.deri): pozita_e_harkut[id_harku]
        for id_harku, harku in harqet.items()
    }

    # kosto fillestare sipas pozitës së harkut
    kostot_baze = [0.0] * len(harqet)
    for id_harku, harku in harqet.items():
        kostot_baze[pozita_e_harkut[id_harku]] = harku.kosto

    return harku_sipas_nyjeve, kostot_baze


def llogarit_koston(
    n,
    harqet,
    marredheniet,
    rruga,
    indekset=None,
    kontrollo_rrugen=True,
):
    """
    Llogarit koston e rrugës duke zbatuar trigger-at sipas rendit.

    Për çdo hark të rrugës shikojmë harqet e kaluara para tij, nga i fundit
    drejt të parit. I pari që është trigger për këtë hark është
    "trigger-i i fundit i kaluar", pra ai përcakton koston.
    Nëse asnjë nuk është trigger, përdoret kostoja fillestare.
    Kështu nuk kalojmë nëpër të gjitha marrëdhëniet, por vetëm nëpër
    harqet e rrugës (afërsisht n*n/2 kontrolle).
    """

    if kontrollo_rrugen:
        if len(rruga) != n + 1 or rruga[0] != 0 or rruga[-1] != 0:
            raise ValueError(
                "Rruga duhet të fillojë dhe të përfundojë te nyja 0 "
                "dhe të ketë n + 1 nyje."
            )

        # Çdo nyje duhet të vizitohet saktësisht një herë
        if set(rruga[:-1]) != set(range(n)):
            raise ValueError("Rruga nuk është cikël Hamiltonian.")

    if indekset is None:
        indekset = pergatit_indekset(harqet, marredheniet)

    harku_sipas_nyjeve, kostot_baze = indekset
    tabela = marredheniet["tabela"]
    m = len(kostot_baze)

    # Kthejmë rrugën në listë harqesh
    harqet_e_rruges = []
    for prej, deri in zip(rruga, rruga[1:]):
        i_harku = harku_sipas_nyjeve.get((prej, deri))

        if i_harku is None:
            raise ValueError(
                f"Nuk ekziston harku nga nyja {prej} te nyja {deri}."
            )

        harqet_e_rruges.append(i_harku)

    kosto_totale = 0.0

    for p, i_objektiv in enumerate(harqet_e_rruges):
        kosto = kostot_baze[i_objektiv]

        # Kërkojmë trigger-in e fundit para pozitës p
        for k in range(p - 1, -1, -1):
            vlera = tabela[harqet_e_rruges[k] * m + i_objektiv]

            if vlera == vlera:      # NaN != NaN, pra kjo është marrëdhënie
                kosto = vlera
                break

        kosto_totale += kosto

    return kosto_totale


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


def levizje_insertion(rruga, harku_sipas_nyjeve, gjeneratori):
    """
    Heq një segment me 1–3 nyje dhe e fut në një pozitë tjetër.
    Kthen None nëse ndonjë nga harqet e reja nuk ekziston.
    """
    n = len(rruga) - 1
    gjatesia = gjeneratori.randint(1, min(3, n - 2))
    i = gjeneratori.randint(1, n - gjatesia)

    segmenti = rruga[i:i + gjatesia]
    pa_segment = rruga[:i] + rruga[i + gjatesia:]

    # Harku që mbyll vendin nga u hoq segmenti
    if (pa_segment[i - 1], pa_segment[i]) not in harku_sipas_nyjeve:
        return None

    # Segmenti futet para pozitës j
    j = gjeneratori.randint(1, len(pa_segment) - 1)

    if j == i:
        return None
    if (pa_segment[j - 1], segmenti[0]) not in harku_sipas_nyjeve:
        return None
    if (segmenti[-1], pa_segment[j]) not in harku_sipas_nyjeve:
        return None

    return pa_segment[:j] + segmenti + pa_segment[j:]


def levizje_swap(rruga, harku_sipas_nyjeve, gjeneratori):
    """
    Ndërron vendet e dy nyjeve.
    Kthen None nëse ndonjë nga harqet e reja nuk ekziston.
    """
    n = len(rruga) - 1
    pozita_1, pozita_2 = sorted(gjeneratori.sample(range(1, n), 2))

    rruga_kandidate = rruga[:]
    rruga_kandidate[pozita_1], rruga_kandidate[pozita_2] = (
        rruga_kandidate[pozita_2],
        rruga_kandidate[pozita_1],
    )

    # Kontrollojmë vetëm harqet që ndryshuan
    for k in {pozita_1 - 1, pozita_1, pozita_2 - 1, pozita_2}:
        lidhja = (rruga_kandidate[k], rruga_kandidate[k + 1])

        if lidhja not in harku_sipas_nyjeve:
            return None

    return rruga_kandidate


def simulated_annealing(
    n,
    harqet,
    marredheniet,
    iteracione=500000,
    seed=7,
    rruga_fillestare=None,
    indekset=None,
    koha_max=60.0,
):
    """
    Përpiqet ta përmirësojë rrugën fillestare.
    Ndalet kur mbarojnë iteracionet ose kur kalon koha_max (sekonda),
    cilado që ndodh e para. Kthen rrugën, koston dhe iteracionet e kryera.
    """
    gjeneratori = random.Random(seed)

    if indekset is None:
        indekset = pergatit_indekset(harqet, marredheniet)

    harku_sipas_nyjeve = indekset[0]

    if rruga_fillestare is None:
        rruga_fillestare = nderto_rruge_fillestare(n, harqet)

    rruga_aktuale = rruga_fillestare[:]

    kosto_aktuale = llogarit_koston(
        n,
        harqet,
        marredheniet,
        rruga_aktuale,
        indekset=indekset,
    )

    rruga_me_e_mire = rruga_aktuale[:]
    kosto_me_e_mire = kosto_aktuale

    if n <= 3:
        return rruga_me_e_mire, kosto_me_e_mire, 0

    # Temperatura lidhet me koston mesatare të një harku,
    # sepse një lëvizje ndryshon vetëm pak harqe.
    kosto_mesatare = (
        sum(harku.kosto for harku in harqet.values()) / len(harqet)
    )
    temperatura_fillim = kosto_mesatare * 0.5
    temperatura_fund = kosto_mesatare * 0.001
    temperatura = temperatura_fillim
    fillimi = time.perf_counter()

    # Nëse për shumë kohë nuk ka përmirësim, rinisim nga më e mira
    pa_permiresim = 0
    kufiri_pa_permiresim = 20000

    iteracione_kryer = 0

    for iteracioni in range(iteracione):
        iteracione_kryer = iteracioni + 1

        # Çdo 100 iteracione përditësojmë temperaturën sipas progresit
        # (pjesa e iteracioneve ose e kohës, cila është më e madhe).
        if iteracioni % 100 == 0:
            progresi = max(
                iteracioni / iteracione,
                (time.perf_counter() - fillimi) / koha_max,
            )

            if progresi >= 1:
                break

            temperatura = temperatura_fillim * (
                temperatura_fund / temperatura_fillim
            ) ** progresi

        # 70% insertion, 30% swap
        if gjeneratori.random() < 0.7:
            rruga_kandidate = levizje_insertion(
                rruga_aktuale, harku_sipas_nyjeve, gjeneratori
            )
        else:
            rruga_kandidate = levizje_swap(
                rruga_aktuale, harku_sipas_nyjeve, gjeneratori
            )

        # Lëvizja krijoi hark që nuk ekziston: e hedhim pa e vlerësuar
        if rruga_kandidate is None:
            continue

        # Lëvizjet ruajnë nyjet e ciklit Hamiltonian dhe harqet e reja
        # janë kontrolluar, prandaj nuk e përsërisim kontrollin e plotë.
        kosto_kandidate = llogarit_koston(
            n,
            harqet,
            marredheniet,
            rruga_kandidate,
            indekset=indekset,
            kontrollo_rrugen=False,
        )

        ndryshimi = kosto_kandidate - kosto_aktuale

        # Pranojmë përmirësimet dhe nganjëherë edhe zgjidhje më të kushtueshme.
        if ndryshimi <= 0 or gjeneratori.random() < math.exp(
            -ndryshimi / temperatura
        ):
            rruga_aktuale = rruga_kandidate
            kosto_aktuale = kosto_kandidate

        if kosto_kandidate < kosto_me_e_mire - 1e-9:
            rruga_me_e_mire = rruga_kandidate[:]
            kosto_me_e_mire = kosto_kandidate
            pa_permiresim = 0
        else:
            pa_permiresim += 1

        if pa_permiresim > kufiri_pa_permiresim:
            rruga_aktuale = rruga_me_e_mire[:]
            kosto_aktuale = kosto_me_e_mire
            pa_permiresim = 0

    return rruga_me_e_mire, kosto_me_e_mire, iteracione_kryer


def perditeso_permbledhjen_me_te_mirat(dosja_projektit):
    """Rindërton best_results.csv nga provat e solver-it të optimizuar."""
    rezultatet = dosja_projektit / "results" / "results_optimized.csv"
    permbledhja = dosja_projektit / "results" / "best_results.csv"
    sipas = {}
    if rezultatet.exists():
        with open(rezultatet, "r", newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                sipas.setdefault(row["instance"], []).append(row)
    fields = [
        "instance", "nodes", "arcs", "trigger_relationships", "baseline_cost",
        "best_cost", "improvement_percent", "best_algorithm", "best_seed",
        "iterations", "seconds", "official_validator_valid", "status",
    ]
    instancat = sorted(
        (dosja_projektit / "instances").glob("grf*.txt"),
        key=lambda p: int(p.stem[3:]) if p.stem[3:].isdigit() else 0,
    )
    with open(permbledhja, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for path in instancat:
            with open(path, "r", encoding="utf-8") as instance_file:
                header = next(line.split() for line in instance_file if line.strip() and not line.lstrip().startswith("#"))
            n, m, rel = map(int, header[:3])
            rows = sipas.get(path.stem, [])
            bases = [x for x in rows if x.get("algorithm") == "Backtracking construction"]
            runs = [x for x in rows if x.get("algorithm") == "Simulated Annealing (insertion+swap)"]
            base = min((float(x["cost"]) for x in bases), default=None)
            best = min(runs, key=lambda x: float(x["cost"])) if runs else None
            if best is not None and (base is None or float(best["cost"]) < base):
                cost = float(best["cost"]); alg = best["algorithm"]; seed = best["seed"]
                iterations = best["iterations"]; seconds = best["seconds"]
                official = best["official_validator_valid"]
            elif base is not None:
                cost = base; alg = "Backtracking construction"; seed = "0"
                iterations = "0"; seconds = ""; official = "not_checked"
            else:
                cost = None; alg = seed = iterations = seconds = official = ""
            improvement = ""
            if base is not None and best is not None:
                improvement = f"{max(0.0, (base - cost) / base * 100):.2f}"
            writer.writerow({
                "instance": path.stem, "nodes": n, "arcs": m,
                "trigger_relationships": rel,
                "baseline_cost": "" if base is None else f"{base:.2f}",
                "best_cost": "" if cost is None else f"{cost:.2f}",
                "improvement_percent": improvement, "best_algorithm": alg,
                "best_seed": seed, "iterations": iterations, "seconds": seconds,
                "official_validator_valid": official,
                "status": "not_run_with_optimized_code" if best is None else "not_checked_officially",
            })


if __name__ == "__main__":
    dosja_projektit = Path(__file__).resolve().parent.parent

    # Ndryshoje këtë emër kur dëshiron të provosh një instancë tjetër.
    emri_instancës = "grf11"

    skedari_instancës = (
        dosja_projektit / "instances" / f"{emri_instancës}.txt"
    )
    skedari_rezultateve = (
        dosja_projektit / "results" / "results_optimized.csv"
    )
    skedari_zgjidhjes = (
        dosja_projektit / "results" / f"{emri_instancës}_zgjidhja.txt"
    )

    # Lexojmë instancën dhe përgatitim indekset një herë.
    fillimi = time.perf_counter()
    n, harqet, marredheniet = lexo_instancen(skedari_instancës)
    indekset = pergatit_indekset(harqet, marredheniet)
    print(f"Leximi i instancës: {time.perf_counter() - fillimi:.1f} sekonda")

    print("Instanca:", emri_instancës)
    print("Numri i nyjeve:", n)
    print("Numri i harqeve:", len(harqet))
    print("Numri i marrëdhënieve:", marredheniet["numri"])

    kolonat = [
        "instance",
        "algorithm",
        "seed",
        "iterations",
        "cost",
        "seconds",
        "official_validator_valid",
    ]

    rezultatet = []

    # Gjejmë një rrugë fillestare me kërkim dhe kthim pas.
    fillimi = time.perf_counter()
    rruga_fillestare = nderto_rruge_fillestare(n, harqet)
    koha_fillestare = time.perf_counter() - fillimi

    kosto_fillestare = llogarit_koston(
        n,
        harqet,
        marredheniet,
        rruga_fillestare,
        indekset=indekset,
    )

    print("\nNdërtim me kthim pas:")
    print("Rruga:", rruga_fillestare)
    print(f"Kostoja: {kosto_fillestare:.2f}")

    rezultatet.append({
        "instance": emri_instancës,
        "algorithm": "Backtracking construction",
        "seed": 0,
        "iterations": 0,
        "cost": round(kosto_fillestare, 2),
        "seconds": round(koha_fillestare, 6),
        "official_validator_valid": "not_checked",
    })

    rruga_me_e_mire_gjithsej = rruga_fillestare
    kosto_me_e_mire_gjithsej = kosto_fillestare

    # Pesë prova të Simulated Annealing.
    iteracione = 500000
    koha_max = 60.0      # sekonda për çdo seed

    print("\nSimulated Annealing:")

    for seed in range(1, 6):
        fillimi = time.perf_counter()

        rruga, kosto, iteracione_kryer = simulated_annealing(
            n,
            harqet,
            marredheniet,
            iteracione=iteracione,
            seed=seed,
            rruga_fillestare=rruga_fillestare,
            indekset=indekset,
            koha_max=koha_max,
        )

        koha = time.perf_counter() - fillimi

        # Kontroll i plotë i rrugës përfundimtare
        llogarit_koston(n, harqet, marredheniet, rruga, indekset=indekset)

        print(
            f"Seed {seed}: rruga={rruga}, "
            f"kostoja={kosto:.2f}, koha={koha:.6f} sekonda"
        )

        rezultatet.append({
            "instance": emri_instancës,
            "algorithm": "Simulated Annealing (insertion+swap)",
            "seed": seed,
            "iterations": iteracione_kryer,
            "cost": round(kosto, 2),
            "seconds": round(koha, 6),
            "official_validator_valid": "not_checked",
        })

        if kosto < kosto_me_e_mire_gjithsej:
            rruga_me_e_mire_gjithsej = rruga
            kosto_me_e_mire_gjithsej = kosto

    # Shtojmë rezultatet në skedarin CSV.
    skedari_rezultateve.parent.mkdir(parents=True, exist_ok=True)

    ka_te_dhena = (
        skedari_rezultateve.exists()
        and skedari_rezultateve.stat().st_size > 0
    )

    with open(
        skedari_rezultateve,
        "a",
        newline="",
        encoding="utf-8",
    ) as skedari:
        shkruesi = csv.DictWriter(skedari, fieldnames=kolonat)

        if not ka_te_dhena:
            shkruesi.writeheader()

        shkruesi.writerows(rezultatet)

    # Ruaj rrugën e mëparshme nëse është më e mirë se kjo provë.
    if skedari_zgjidhjes.exists():
        try:
            with open(skedari_zgjidhjes, "r", encoding="utf-8") as f:
                route_old = [int(v) for v in f.read().split()]
            cost_old = llogarit_koston(n, harqet, marredheniet, route_old, indekset=indekset)
            if cost_old < kosto_me_e_mire_gjithsej:
                rruga_me_e_mire_gjithsej = route_old
                kosto_me_e_mire_gjithsej = cost_old
        except (ValueError, OSError):
            pass

    # Ruajmë rrugën më të mirë, që të mund të kontrollohet
    # ose të dorëzohet në portal.
    with open(skedari_zgjidhjes, "w", encoding="utf-8") as skedari:
        skedari.write(" ".join(str(nyja) for nyja in rruga_me_e_mire_gjithsej))
        skedari.write("\n")

    print(f"\nKostoja më e mirë: {kosto_me_e_mire_gjithsej:.2f}")
    print("\nRezultatet u ruajtën te:")
    print(skedari_rezultateve)
    print("Rruga më e mirë u ruajt te:")
    print(skedari_zgjidhjes)
    perditeso_permbledhjen_me_te_mirat(dosja_projektit)
    print("Përmbledhja best_results.csv u përditësua.")

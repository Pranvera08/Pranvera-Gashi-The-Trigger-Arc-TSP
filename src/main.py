"""
Ekzekuton algoritmet për Trigger Arc TSP dhe ruan rezultatet për secilin veç.

Shembuj:
    python src/main.py grf7                          # të tria algoritmet, 5 seed, 60 s
    python src/main.py grf7 grf9 --alg sa grasp      # vetëm SA dhe GRASP
    python src/main.py te_gjitha --koha 30 --procese 4
    python src/main.py grf1 --seeds 1 2 3 --koha 10

Rezultatet:
    results/<algoritmi>/provat.csv          çdo provë (instanca, seed, kosto, koha, ...)
    results/<algoritmi>/me_te_mirat.csv     për çdo instancë: më e mira, mesatarja, devijimi
    results/<algoritmi>/konvergjenca.csv    kostoja më e mirë me kalimin e kohës
    results/<algoritmi>/zgjidhjet/<inst>.txt rruga më e mirë e gjetur ndonjëherë
    results/krahasimi.csv                   krahasimi i algoritmeve për çdo instancë

Post-optimizimi (ILS nga zgjidhja më e mirë e njohur, rezultatet e algoritmeve nuk preken):
    python src/main.py te_gjitha --permireso --koha 60 --raunde 3
    -> results/me_te_mirat_e_njohura/ (rekordet, historia.csv, permbledhja.csv)
"""
import argparse
import csv
import math
import multiprocessing as mp
import os
import statistics
import time
from datetime import datetime
from pathlib import Path

from grasp import grasp
from ils import iterated_local_search
from instanca import ngarko
from kosto import llogarit_koston
from ndertimi import nderto_rruge_fillestare
from sa import simulated_annealing
import permireso

DOSJA = Path(__file__).resolve().parent.parent
INSTANCAT = DOSJA / "instances"
REZULTATET = DOSJA / "results"
ALGORITMET = ["sa", "grasp", "ils"]
INSTANCA_PARAZGJEDHUR = "grf1"      # ndryshoje këtu nëse e nis pa argumente
EMRAT = {"sa": "Simulated Annealing", "grasp": "GRASP", "ils": "Iterated Local Search"}

# Instanca e ngarkuar në çdo proces (ngarkohet një herë për proces)
_KTX = None
_RRUGA_FILLESTARE = None
_SKEDARI = None


def _pergatit(skedari):
    global _KTX, _RRUGA_FILLESTARE, _SKEDARI
    if _SKEDARI != skedari:
        _KTX = ngarko(skedari)
        _RRUGA_FILLESTARE = nderto_rruge_fillestare(_KTX.n, _KTX.harqet)
        _SKEDARI = skedari


def _nje_prove(detyra):
    skedari, algoritmi, seed, koha = detyra
    _pergatit(skedari)
    fillimi = time.perf_counter()

    if algoritmi == "sa":
        rez = simulated_annealing(_KTX, _RRUGA_FILLESTARE, seed=seed, koha_max=koha)
    elif algoritmi == "grasp":
        rez = grasp(_KTX, seed=seed, koha_max=koha)
    elif algoritmi == "ils":
        rez = iterated_local_search(_KTX, _RRUGA_FILLESTARE, seed=seed, koha_max=koha)
    else:
        raise ValueError(algoritmi)

    rez["sekonda"] = time.perf_counter() - fillimi
    # Kontroll i plotë i pavarur: rruga e vlefshme dhe kostoja e saktë
    kontrolli = llogarit_koston(_KTX, rez["rruga"])
    if abs(kontrolli - rez["kosto"]) > 1e-6:
        raise RuntimeError(f"Kostoja nuk përputhet: {kontrolli} != {rez['kosto']}")
    rez["algoritmi"] = algoritmi
    rez["seed"] = seed
    return rez


def _shto_csv(skedari, kolonat, rreshtat):
    skedari.parent.mkdir(parents=True, exist_ok=True)
    ka_koke = skedari.exists() and skedari.stat().st_size > 0
    with open(skedari, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=kolonat)
        if not ka_koke:
            w.writeheader()
        w.writerows(rreshtat)


def _ruaj_zgjidhjen(ktx, skedari, rruga, kosto):
    """Ruan rrugën vetëm nëse është më e mirë se ajo që është ruajtur më parë."""
    skedari.parent.mkdir(parents=True, exist_ok=True)
    if skedari.exists():
        try:
            e_vjetra = [int(v) for v in skedari.read_text(encoding="utf-8").split()]
            if llogarit_koston(ktx, e_vjetra) <= kosto + 1e-9:
                return False
        except (ValueError, OSError):
            pass
    skedari.write_text(" ".join(map(str, rruga)) + "\n", encoding="utf-8")
    return True


def _rendit(emri):
    pjesa = emri[3:] if emri.startswith("grf") else ""
    return (0, int(pjesa)) if pjesa.isdigit() else (1, emri)


def _fituesi(d, kolona):
    """Algoritmi me vlerën më të vogël; 'barazim: sa+ils' nëse janë disa."""
    me_e_vogla = min(float(d[a][kolona]) for a in d)
    fituesit = [a for a in ALGORITMET if a in d and float(d[a][kolona]) <= me_e_vogla + 1e-9]
    return fituesit[0] if len(fituesit) == 1 else "barazim: " + "+".join(fituesit)


def perditeso_permbledhjet():
    """Rindërton me_te_mirat.csv për çdo algoritëm dhe krahasimi.csv nga provat.csv."""
    te_gjitha = {}
    for alg in ALGORITMET:
        provat = REZULTATET / alg / "provat.csv"
        if not provat.exists():
            continue
        sipas = {}
        with open(provat, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                sipas.setdefault((r["instanca"], r["koha_max"]), []).append(r)

        rreshtat = []
        for (inst, koha), lista in sorted(sipas.items(), key=lambda x: (_rendit(x[0][0]), float(x[0][1]))):
            kostot = [float(r["kosto"]) for r in lista]
            me_e_mira = min(lista, key=lambda r: float(r["kosto"]))
            rresht = {
                "instanca": inst,
                "koha_max": koha,
                "provat": len(lista),
                "kosto_me_e_mire": f"{min(kostot):.2f}",
                "kosto_mesatare": f"{statistics.mean(kostot):.2f}",
                "devijimi": f"{statistics.pstdev(kostot):.2f}",
                "seed_me_i_mire": me_e_mira["seed"],
                "kosto_fillestare": me_e_mira["kosto_fillestare"],
                "iteracione_mesatare": f"{statistics.mean(float(r['iteracione']) for r in lista):.0f}",
            }
            rreshtat.append(rresht)
            te_gjitha.setdefault((inst, koha), {})[alg] = rresht

        kolonat = ["instanca", "koha_max", "provat", "kosto_me_e_mire", "kosto_mesatare",
                   "devijimi", "seed_me_i_mire", "kosto_fillestare", "iteracione_mesatare"]
        with open(REZULTATET / alg / "me_te_mirat.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=kolonat)
            w.writeheader()
            w.writerows(rreshtat)

    kolonat = ["instanca", "koha_max"]
    for alg in ALGORITMET:
        kolonat += [f"{alg}_me_e_mira", f"{alg}_mesatarja"]
    kolonat += ["fituesi_me_e_mira", "fituesi_mesatarja"]
    rreshtat = []
    for (inst, koha), d in sorted(te_gjitha.items(), key=lambda x: (_rendit(x[0][0]), float(x[0][1]))):
        r = {"instanca": inst, "koha_max": koha}
        for alg in ALGORITMET:
            r[f"{alg}_me_e_mira"] = d[alg]["kosto_me_e_mire"] if alg in d else ""
            r[f"{alg}_mesatarja"] = d[alg]["kosto_mesatare"] if alg in d else ""
        if len(d) > 1:
            r["fituesi_me_e_mira"] = _fituesi(d, "kosto_me_e_mire")
            r["fituesi_mesatarja"] = _fituesi(d, "kosto_mesatare")
        rreshtat.append(r)
    REZULTATET.mkdir(exist_ok=True)
    with open(REZULTATET / "krahasimi.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=kolonat)
        w.writeheader()
        w.writerows(rreshtat)


def ekzekuto_instancen(emri, algoritmet, seeds, koha, procese):
    skedari = str(INSTANCAT / f"{emri}.txt")
    fillimi = time.perf_counter()
    _pergatit(skedari)                       # në procesin kryesor (edhe për fork)
    ktx = _KTX
    print(f"\n=== {emri}: n={ktx.n}, harqe={ktx.m}, "
          f"marrëdhënie={ktx.marredheniet['numri']} "
          f"(leximi {time.perf_counter() - fillimi:.1f} s)")

    detyrat = [(skedari, alg, seed, koha) for alg in algoritmet for seed in seeds]
    if procese > 1:
        with mp.Pool(processes=procese, initializer=_pergatit, initargs=(skedari,)) as pool:
            rezultatet = pool.map(_nje_prove, detyrat)
    else:
        rezultatet = [_nje_prove(d) for d in detyrat]

    data = datetime.now().strftime("%Y-%m-%d %H:%M")
    for alg in algoritmet:
        te_algoritmit = [r for r in rezultatet if r["algoritmi"] == alg]
        provat = []
        konvergjenca = []
        for r in te_algoritmit:
            provat.append({
                "instanca": emri, "algoritmi": EMRAT[alg], "seed": r["seed"],
                "koha_max": koha, "kosto_fillestare": f"{r['kosto_fillestare']:.2f}",
                "kosto": f"{r['kosto']:.2f}", "iteracione": r["iteracione"],
                "sekonda": f"{r['sekonda']:.2f}", "data": data,
                "validuar_zyrtarisht": "jo",
            })
            for sek, k in r["historia"]:
                konvergjenca.append({"instanca": emri, "seed": r["seed"], "koha_max": koha,
                                     "sekonda": f"{sek:.3f}", "kosto": f"{k:.2f}"})
        _shto_csv(REZULTATET / alg / "provat.csv", list(provat[0].keys()), provat)
        _shto_csv(REZULTATET / alg / "konvergjenca.csv",
                  ["instanca", "seed", "koha_max", "sekonda", "kosto"], konvergjenca)

        me_e_mira = min(te_algoritmit, key=lambda r: r["kosto"])
        u_ruajt = _ruaj_zgjidhjen(ktx, REZULTATET / alg / "zgjidhjet" / f"{emri}.txt",
                                  me_e_mira["rruga"], me_e_mira["kosto"])
        kostot = [r["kosto"] for r in te_algoritmit]
        print(f"{EMRAT[alg]:<22} më e mira {min(kostot):8.2f} | mesatarja "
              f"{statistics.mean(kostot):8.2f} | kostot: "
              + " ".join(f"{k:.2f}" for k in kostot)
              + ("  (rekord i ri, u ruajt)" if u_ruajt else ""))


def main():
    p = argparse.ArgumentParser(description="Trigger Arc TSP: SA, GRASP, ILS")
    p.add_argument("instancat", nargs="*",
                   help="emrat e instancave (p.sh. grf7 grf9) ose 'te_gjitha'")
    p.add_argument("--alg", nargs="+", choices=ALGORITMET, default=ALGORITMET)
    p.add_argument("--seeds", nargs="+", type=int, default=[1, 2, 3, 4, 5])
    p.add_argument("--koha", type=float, default=60.0, help="sekonda për çdo provë")
    p.add_argument("--procese", type=int, default=max(1, (os.cpu_count() or 1)),
                   help="sa prova njëherësh (bërthama CPU)")
    p.add_argument("--permireso", action="store_true",
                   help="post-optimizim: ILS nga zgjidhja më e mirë e njohur")
    p.add_argument("--raunde", type=int, default=3,
                   help="(me --permireso) sa raunde maksimalisht për instancë")
    a = p.parse_args()

    # Kur ekzekutohet pa argumente (p.sh. me Run në PyCharm), përdoret kjo instancë.
    if not a.instancat:
        a.instancat = [INSTANCA_PARAZGJEDHUR]
        print(f"Asnjë instancë nuk u dha; po përdoret {INSTANCA_PARAZGJEDHUR}.")

    if a.instancat == ["te_gjitha"]:
        emrat = sorted((f.stem for f in INSTANCAT.glob("grf*.txt")), key=_rendit)
    else:
        emrat = a.instancat

    if a.permireso:
        for emri in emrat:
            permireso.permireso_instancen(emri, INSTANCAT, REZULTATET, a.koha, a.raunde, a.procese)
            permireso.perditeso_permbledhjen(REZULTATET)
        print(f"\nRekordet u ruajtën te: {REZULTATET / 'me_te_mirat_e_njohura'}")
        return

    for emri in emrat:
        ekzekuto_instancen(emri, a.alg, a.seeds, a.koha, a.procese)
        perditeso_permbledhjet()

    print(f"\nRezultatet u ruajtën te: {REZULTATET}")


if __name__ == "__main__":
    main()

# Trigger Arc TSP

Projekt për lëndën Dizajni dhe Analiza e Algoritmeve.

## Qëllimi

Të gjejmë një cikël Hamiltonian me kosto sa më të vogël në një graf të drejtuar.
Kostoja e një harku mund të ndryshojë kur kalohet një hark tjetër që është
përcaktuar si trigger. Vlen vetëm trigger-i i fundit i kaluar para harkut.

## Algoritmet

| Algoritmi | Skedari | Ideja |
|---|---|---|
| Simulated Annealing (SA) | `src/sa.py` | Lëvizje të rastit (insertion + swap); pranon edhe zgjidhje më të këqija me probabilitet e^(-Δ/T) |
| GRASP | `src/grasp.py` | Ndërtim greedy i rastësishëm me RCL (me kosto të vërtetë me trigger-a) + kërkim lokal, i përsëritur |
| Iterated Local Search (ILS) | `src/ils.py` | Kërkim lokal → perturbim → kërkim lokal, duke ruajtur më të mirën |

Zgjidhja fillestare për SA dhe ILS ndërtohet me backtracking (`src/ndertimi.py`).

## Struktura

- `src/main.py`: pika hyrëse; ekzekuton algoritmet dhe ruan rezultatet
- `src/instanca.py`: leximi i instancës (tabela kompakte e trigger-ave) dhe përgatitja e indekseve
- `src/kosto.py`: llogaritja e kostos (vlerësim i pjesshëm + ndërprerje e hershme)
- `src/levizjet.py`: lëvizjet insertion/swap, perturbimi dhe kërkimi lokal
- `src/ndertimi.py`: backtracking dhe ndërtimi i GRASP
- `src/sa.py`, `src/grasp.py`, `src/ils.py`: algoritmet
- `instances/`: instancat (`grf15.txt` dhe `grf16.txt` janë shumë të mëdha dhe nuk ruhen në Git)
- `results/<algoritmi>/`: rezultatet për secilin algoritëm veç e veç (shih më poshtë)
- `results/krahasimi.csv`: krahasimi i tre algoritmeve për çdo instancë
- `results/sa_v1/`: rezultatet e versionit të parë (kodi i tij gjendet në historinë e Git-it)
- `notebooks/`: analizë dhe grafikë

## Si ekzekutohet

Nevojitet Python 3.10+; nuk ka paketa shtesë.

```bash
python src/main.py grf7                          # të tria algoritmet, 5 seed-e, 60 s për provë
python src/main.py grf7 grf9 --alg sa grasp      # vetëm disa algoritme
python src/main.py te_gjitha --koha 30           # të gjitha instancat grf*
python src/main.py grf1 --seeds 1 2 3 --koha 10 --procese 4
```

- `--koha`: sekonda për çdo provë (seed); të gjitha algoritmet marrin kohë të barabartë
- `--seeds`: cilat seed-e (parazgjedhje 1 2 3 4 5)
- `--procese`: sa prova ekzekutohen paralelisht (parazgjedhje: numri i bërthamave)

## Rezultatet

Për secilin algoritëm (`results/sa/`, `results/grasp/`, `results/ils/`):

- `provat.csv`: çdo provë: instanca, seed, koha, kostoja fillestare, kostoja, iteracionet
- `me_te_mirat.csv`: për çdo instancë: kostoja më e mirë, mesatarja, devijimi standard
- `konvergjenca.csv`: kostoja më e mirë me kalimin e kohës (për grafikë)
- `zgjidhjet/<instanca>.txt`: rruga më e mirë e gjetur ndonjëherë (zëvendësohet vetëm nëse gjendet më e mirë)

Çdo rrugë kontrollohet para ruajtjes: cikël Hamiltonian, harqe që ekzistojnë, kosto e rillogaritur.

# Trigger Arc TSP

Projekt për lëndën Dizajni dhe Analiza e Algoritmeve.

## Qëllimi

Të gjejmë një cikël Hamiltonian me kosto sa më të vogël në një graf të drejtuar.
Kostoja e një harku mund të ndryshojë kur kalohet një hark tjetër që është
përcaktuar si trigger.

## Struktura

- src/ta_tsp.py — kodi i vetëm kryesor, me lexim kompakt të trigger-ave dhe Simulated Annealing me insertion/swap
- instances/ — instancat; grf15.txt dhe grf16.txt ruhen lokalisht dhe përjashtohen nga Git
- results/results_template.csv — rezultatet historike të versionit të vjetër
- results/results_optimized.csv — provat e versionit të optimizuar
- results/best_results.csv — kostoja më e mirë, përmirësimi, seed-i dhe statusi i validimit
- results/<grf>_zgjidhja.txt — rruga më e mirë e ruajtur për dorëzim/kontroll
- notebooks/Trigger_Arc_TSP_Kaggle.ipynb — analizë dhe grafikë për rezultatet; nuk përmban kopje të solver-it


# Zgjidhja heuristike për Trigger Arc TSP

**Lënda:** Dizajni dhe Analiza e Algoritmeve  
**Studentja:** [Emri yt]  
**Data:** [Data e dorëzimit]

## Përmbledhje

Ky projekt trajton Trigger Arc Travelling Salesman Problem (TA-TSP), ku kostoja e një harku mund të ndryshojë kur kalohet një hark tjetër, i quajtur trigger. U implementua një program në Python që lexon instancat, llogarit koston e një cikli dhe kërkon zgjidhje me Simulated Annealing.

Eksperimentet u kryen në dy instanca, `grf1` dhe `grf2`. Në të dyja, Simulated Annealing gjeti zgjidhje më të mira se ndërtimi fillestar me kthim pas. Kostoja më e mirë ishte 111.34 për `grf1` dhe 49.88 për `grf2`.

## 1. Përshkrimi i problemit

Jepet një graf i drejtuar. Kërkohet një cikël që nis te depoja 0, viziton çdo nyje një herë dhe kthehet në nyjën 0.

Një marrëdhënie trigger përmban një hark shkaktar, një hark objektiv dhe një kosto të re. Kur kalohet trigger-i, kostoja e harkut objektiv ndryshon nëse objektivi nuk është kaluar ende. Kostoja përfundimtare e rrugës varet nga rendi në të cilin kalohen harqet.

## 2. Përfaqësimi dhe llogaritja e kostos

Programi lexon numrin e nyjeve, harqeve dhe marrëdhënieve nga skedari i instancës. Harqet ruhen me identifikuesin, nyjën fillestare, nyjën përfundimtare dhe koston. Kostot lexohen si numra dhjetorë.

Funksioni i vlerësimit kontrollon nëse rruga është cikël Hamiltonian dhe nëse ekziston çdo hark i përdorur. Gjatë kalimit nëpër rrugë, ai mban koston aktuale të secilit hark dhe zbaton ndryshimet nga trigger-at sipas rendit të kalimit.

## 3. Algoritmet

### Ndërtimi fillestar me kthim pas

Ndërtimi fillon në nyjën 0 dhe provon fillimisht harqet me kosto më të ulët. Nëse një zgjedhje e çon rrugën në qorrsokak, algoritmi kthehet pas dhe provon një hark tjetër. Kështu kërkon një cikël fillestar të vlefshëm. Në implementim është vendosur kufi prej 1 000 000 thirrjesh kërkimi.

### Simulated Annealing

Simulated Annealing nis nga cikli fillestar dhe krijon rrugë kandidate duke ndërruar ose përmbysur pozita të nyjeve. Rrugët që përdorin harqe që mungojnë refuzohen. Përmirësimet pranohen; disa zgjidhje më të kushtueshme mund të pranohen gjatë kërkimit për të shmangur ngecjen në një zgjidhje lokale. Algoritmi ruan rrugën më të mirë që gjen.

## 4. Analiza e kompleksitetit

Vlerësimi i një rruge në implementimin aktual kushton deri në `O(m + r + n)`, ku `m` është numri i harqeve, `r` numri i marrëdhënieve trigger dhe `n` numri i nyjeve. Kjo përfshin ndërtimin e indekseve dhe kalimin nëpër rrugë.

Për `K` iteracione të Simulated Annealing, koha e kërkimit është deri në `O(K(m + r + n))`. Kërkimi fillestar me kthim pas mund të shqyrtojë shumë rrugë në rastin më të keq; programi e kufizon numrin e thirrjeve të kërkimit në 1 000 000.

## 5. Eksperimentet dhe rezultatet

Eksperimentet u ekzekutuan me Python 3.12. Për secilën instancë, Simulated Annealing u ekzekutua me 10 000 iteracione për pesë seed-e.

### Instanca `grf1`

Instanca `grf1` ka 20 nyje, 300 harqe dhe 5651 marrëdhënie trigger. Ndërtimi fillestar dha kosto 123.44.

| Metoda | Seed | Iteracione | Kostoja | Koha (sekonda) |
|---|---:|---:|---:|---:|
| Ndërtim me kthim pas | 0 | — | 123.44 | — |
| Simulated Annealing | 1 | 10000 | 113.77 | 12.308572 |
| Simulated Annealing | 2 | 10000 | 111.77 | 11.043739 |
| Simulated Annealing | 3 | 10000 | 117.18 | 11.022068 |
| Simulated Annealing | 4 | 10000 | 113.41 | 10.864203 |
| Simulated Annealing | 5 | 10000 | 111.34 | 10.879109 |
| **Mesatarja e Simulated Annealing** | — | **10000** | **113.49** | **11.223538** |

Rezultati më i mirë për `grf1` ishte 111.34 me seed 5, rreth 9.8% më i ulët se kostoja e ndërtimit fillestar.

Rruga më e mirë e gjetur për `grf1` ishte:

`0 → 4 → 15 → 8 → 3 → 6 → 13 → 5 → 14 → 18 → 19 → 1 → 11 → 9 → 16 → 17 → 10 → 7 → 12 → 2 → 0`

### Instanca `grf2`

Instanca `grf2` ka 20 nyje, 300 harqe dhe 5708 marrëdhënie trigger. Ndërtimi fillestar dha kosto 65.80.

| Metoda | Seed | Iteracione | Kostoja | Koha (sekonda) |
|---|---:|---:|---:|---:|
| Ndërtim me kthim pas | 0 | — | 65.80 | — |
| Simulated Annealing | 1 | 10000 | 51.28 | 10.790711 |
| Simulated Annealing | 2 | 10000 | 49.88 | 10.972626 |
| Simulated Annealing | 3 | 10000 | 52.39 | 10.898019 |
| Simulated Annealing | 4 | 10000 | 53.63 | 10.834851 |
| Simulated Annealing | 5 | 10000 | 58.46 | 10.908603 |
| **Mesatarja e Simulated Annealing** | — | **10000** | **53.13** | **10.880962** |

Rezultati më i mirë për `grf2` ishte 49.88 me seed 2, rreth 24.2% më i ulët se kostoja e ndërtimit fillestar.

Rruga më e mirë e gjetur për `grf2` ishte:

`0 → 2 → 12 → 9 → 14 → 19 → 5 → 15 → 8 → 18 → 4 → 3 → 10 → 13 → 6 → 1 → 17 → 7 → 11 → 16 → 0`

## 6. Diskutim dhe kufizime

Në të dy instancat, Simulated Annealing gjeti rrugë me kosto më të ulët se ndërtimi fillestar në të pesë provat. Rezultatet ndryshuan sipas seed-it, çka tregon ndikimin e rastësisë në kërkim.

Deri tani janë provuar vetëm dy instanca. Prandaj rezultatet nuk mjaftojnë për përfundime për të gjitha instancat TA-TSP. Rrugët nuk janë kontrolluar ende me validuesin zyrtar, ndaj vlefshmëria zyrtare mbetet e pakontrolluar. Simulated Annealing nuk garanton optimumin global, ndërsa kërkimi fillestar me kthim pas ka kufi prej 1 000 000 thirrjesh.

## 7. Përfundim

U implementua një zgjidhës që lexon instancat, zbaton kostot dinamike të trigger-ave, ndërton një cikël fillestar dhe përpiqet ta përmirësojë me Simulated Annealing. Në `grf1` dhe `grf2`, Simulated Annealing gjeti kosto më të ulëta se ndërtimi fillestar. Për vlerësim më të plotë duhen provuar instanca të tjera dhe kontrolluar zgjidhjet me validuesin zyrtar.

## Referenca

Cerrone, C., Cerulli, R., Ceschia, S. dhe Schaerf, A. *Metaheuristics Summer School Competition: The Trigger Arc TSP*, MESS 2024, prezantimi i dhënë për projektin.
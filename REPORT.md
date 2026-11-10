# Zgjidhja heuristike për Trigger Arc TSP

**Lënda:** Dizajni dhe Analiza e Algoritmeve  
**Studentja:** [Emri yt]  
**Data:** [Data e dorëzimit]

## Përmbledhje

Ky projekt trajton Trigger Arc Travelling Salesman Problem (TA-TSP), ku kostoja e një harku mund të ndryshojë kur kalohet një hark tjetër, i quajtur trigger. U implementua një program në Python që lexon instancën, llogarit koston e një cikli dhe kërkon zgjidhje me Simulated Annealing.

Eksperimentet u kryen në instancën `grf1`, e cila ka 20 nyje, 300 harqe dhe 5651 marrëdhënie trigger. Ndërtimi fillestar dha kosto 123.44. Simulated Annealing, me pesë seed-e dhe nga 10 000 iteracione, arriti koston mesatare 113.49 dhe rezultatin më të mirë 111.34.

## 1. Përshkrimi i problemit

Jepet një graf i drejtuar. Kërkohet një cikël që nis te depoja 0, viziton çdo nyje një herë dhe kthehet në nyjën 0.

Një marrëdhënie trigger përmban një hark shkaktar, një hark objektiv dhe një kosto të re. Kur kalohet trigger-i, kostoja e harkut objektiv ndryshon nëse objektivi nuk është kaluar ende. Kostoja përfundimtare e rrugës varet nga rendi në të cilin kalohen harqet.

## 2. Përfaqësimi dhe llogaritja e kostos

Programi lexon numrin e nyjeve, harqeve dhe marrëdhënieve nga skedari i instancës. Harqet ruhen me identifikuesin, nyjën fillestare, nyjën përfundimtare dhe koston. Kostot lexohen si numra dhjetorë, sepse instanca `grf1` përmban vlera si `8.62`.

Funksioni i vlerësimit kontrollon nëse rruga është cikël Hamiltonian dhe nëse ekziston çdo hark i përdorur. Gjatë kalimit nëpër rrugë, ai mban koston aktuale të secilit hark dhe zbaton ndryshimet nga trigger-at në rendin e duhur.

## 3. Algoritmet

### Ndërtimi fillestar me kthim pas

Ndërtimi fillon në nyjën 0 dhe provon fillimisht harqet me kosto më të ulët. Nëse një zgjedhje e çon rrugën në qorrsokak, algoritmi kthehet pas dhe provon një hark tjetër. Kështu kërkon një cikël fillestar të vlefshëm.

### Simulated Annealing

Simulated Annealing nis nga cikli fillestar dhe krijon rrugë kandidate duke ndërruar ose përmbysur pozita të nyjeve. Rrugët që përdorin harqe që mungojnë refuzohen. Përmirësimet pranohen; disa zgjidhje më të kushtueshme mund të pranohen gjatë kërkimit për të shmangur ngecjen në një zgjidhje lokale. Algoritmi ruan rrugën më të mirë që gjen.

## 4. Analiza e kompleksitetit

Vlerësimi i një rruge në implementimin aktual kushton deri në `O(m + r + n)`, ku `m` është numri i harqeve, `r` numri i marrëdhënieve trigger dhe `n` numri i nyjeve. Kjo përfshin ndërtimin e indekseve dhe kalimin nëpër rrugë.

Për `K` iteracione të Simulated Annealing, koha e kërkimit është deri në `O(K(m + r + n))`. Ndërtimi me kthim pas mund të shqyrtojë shumë rrugë në rastin më të keq; në program është vendosur kufi prej 1 000 000 thirrjesh kërkimi.

## 5. Eksperimentet dhe rezultatet

Eksperimentet u ekzekutuan në Python 3.12 me instancën `grf1` dhe 10 000 iteracione për secilin nga pesë seed-et. Ndërtimi fillestar dha kosto 123.44.

| Metoda | Seed | Iteracione | Kostoja | Koha (sekonda) |
|---|---:|---:|---:|---:|
| Simulated Annealing | 1 | 10000 | 113.77 | 12.308572 |
| Simulated Annealing | 2 | 10000 | 111.77 | 11.043739 |
| Simulated Annealing | 3 | 10000 | 117.18 | 11.022068 |
| Simulated Annealing | 4 | 10000 | 113.41 | 10.864203 |
| Simulated Annealing | 5 | 10000 | 111.34 | 10.879109 |
| **Mesatarja** | — | **10000** | **113.49** | **11.223538** |

Rezultati më i mirë ishte 111.34, i gjetur me seed 5. Ky është rreth 9.8% më i ulët se kostoja fillestare 123.44.

Rruga më e mirë e gjetur ishte:

`0 → 4 → 15 → 8 → 3 → 6 → 13 → 5 → 14 → 18 → 19 → 1 → 11 → 9 → 16 → 17 → 10 → 7 → 12 → 2 → 0`

## 6. Diskutim dhe kufizime

Në këtë instancë, Simulated Annealing gjeti rrugë me kosto më të ulët se ndërtimi fillestar në të pesë provat. Rezultatet ndryshuan sipas seed-it, çka tregon ndikimin e rastësisë në kërkim.

Eksperimentet janë kryer vetëm në instancën `grf1`; prandaj nuk mjaftojnë për të nxjerrë përfundime për të gjitha instancat TA-TSP. Rruga më e mirë nuk është kontrolluar ende me validuesin zyrtar, ndaj vlefshmëria zyrtare shënohet si e pakontrolluar. Gjithashtu, metoda me kthim pas ka kufi kërkimi dhe Simulated Annealing nuk garanton optimumin global.

## 7. Përfundim

U implementua zgjidhës që lexon instancën `grf1`, zbaton kostot dinamike të trigger-ave dhe kërkon cikël Hamiltonian. Në këtë instancë, Simulated Annealing përmirësoi koston nga 123.44 në 111.34. Për vlerësim më të plotë duhen provuar instanca të tjera dhe kontrolluar zgjidhjet me validuesin zyrtar.

## Referenca

Cerrone, C., Cerulli, R., Ceschia, S. dhe Schaerf, A. *Metaheuristics Summer School Competition: The Trigger Arc TSP*, MESS 2024, prezantimi i dhënë për projektin.
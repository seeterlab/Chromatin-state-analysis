#!/usr/bin/env python3
#
# Copyright (c) 2017 Michel TERESE
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


CHROMOSOME_COUNT = 5

import sys
from bisect import bisect

# Vérifie les arguments
if len(sys.argv) -1 != 2 :
    print( "syntax: ", sys.argv[0], 
"""chrom_states_file data_file

INPUT:

chrom_states_file doit contenir l'enchaînement des états:

Chrom	From	To	State
1	1	1200	8
1	1201	3150	4
1	3151	4650	2
1	4651	6450	6
...

data_file doit avoir 5 colonnes séparées par des tabulations.
exemple:

1       AT1G01010       3631    5899    +
1       AT1G01020       6788    9130    -
1       AT1G03987       11101   11372   +
1       AT1G01030       11649   13714   -
1       AT1G01040       23121   31227   +
1       AT1G03993       23312   24099   -
...

OUTPUT:

Le contenu du fichier data_file avec 1 colonne supplémentaire contenant la liste des états

1       AT1G01010       3631    5899    +        26
1       AT1G01020       6788    9130    -        42137
1       AT1G03987       11101   11372   +        5
1       AT1G01030       11649   13714   -        25
1       AT1G01040       23121   31227   +        137
1       AT1G03993       23312   24099   -        31
...

"""
)
    sys.exit(1)

chrom_states_file = sys.argv[1]
data_file = sys.argv[2]

# Les 3 tableaux ci-dessous seront indexés par le n° de chromosome (de 1 à n)
# Chaque éléments des tableaux sera une liste de position ou d'état pour le chromosome concerné
# L'indice zéro sera initialisé à None car non utilisé
a_start = []
a_end = []
a_state = []

# Initialise les 3 tableaux
for i in range(0, CHROMOSOME_COUNT +1) :
    a_start.append(i)
    a_start[i] = [] if i > 0 else None
    a_end.append(i)
    a_end[i] = [] if i > 0 else None
    a_state.append(i)
    a_state[i] = [] if i > 0 else None

# Lit le fichier des états et initialise les tableaux a_start, a_end et a_state
with open( chrom_states_file ) as f:
    line_nb = 0
    for line in f :
        line_nb += 1
        # saute la 1ère ligne (en-tête)
        if line_nb == 1 :
            continue
        (chrom, start, end, state) = line.split()
        chrom = int(chrom)
        a_start[chrom].append( int(start) )
        a_end[chrom].append( int(end) )
        a_state[chrom].append( state )

# DEBUG: affiche les tableaux
# for chrom in range(1, CHROMOSOME_COUNT+1) :
#     print( chrom, a_end[chrom][-1] )
#     for i in range(0, len(a_start[chrom])) :
#         print( chrom, a_start[chrom][i], a_end[chrom][i], a_state[chrom][i] )

def generate_state_list( chrom, start, end, direction ):
    "génère la liste des états pour l'intervalle"

    # Recherche l'état corespondant à la position de départ du gene courant
    i = bisect(a_start[chrom], start) -1
    state_list = a_state[chrom][i]

    # Recherche les états suivants dans l'intervalle
    for j in range(i +1, len(a_start[chrom])) :
        if a_start[chrom][j] > end :
            break
        # state est une chaîne de caractère !
        state_list = state_list + a_state[chrom][j]

    # Si la direction du gène est négative, il faut inverser la liste des états
    if direction == "-":
        state_list = state_list[::-1]

    return state_list


# Previous end position
prev_end = 0

# Previous chomosom
prev_chrom = 1

# Lit le fichier de données
with open( data_file ) as f:
    for line in f :
        fields = line.split()
        chrom     = int(fields[0])
        start     = int(fields[2])
        end       = int(fields[3])
        direction = fields[4]

        # Si on est passé à un nouveau chromosome
        if chrom != prev_chrom :
#             # Affiche la dernière ligne intergénique du chromosome précédent
#             print( prev_chrom, "\t.      \t", prev_end +1, "\t", a_end[prev_chrom][-1], "\t+")
            prev_chrom = chrom
            # Réinit de prev_end pour le prochain chromosome
            prev_end = 0

        # S'il y a un espace intergénique (pas de chevauchement)
        if start > prev_end :
            # Affiche la ligne intergénique
            inter_gene_start = prev_end + 1
            inter_gene_end   = start - 1
            state_list = generate_state_list( chrom, inter_gene_start, inter_gene_end, direction )
#             print( chrom, "\t.       \t", inter_gene_start, "\t", inter_gene_end, "\t+\t", state_list )

        # Affiche la ligne avec la liste des états en dernière colonne
        state_list = generate_state_list( chrom, start, end, direction )
        print( line.rstrip(), "\t", state_list )

        prev_end = end


# Affiche la dernière ligne intergénique du dernier chromosome
# print( prev_chrom, "\t.      \t", prev_end +1, "\t", a_end[prev_chrom][-1], "\t+")


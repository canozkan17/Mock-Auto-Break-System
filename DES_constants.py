"""
This module defines the constant tables and permutations used in the
Data Encryption Standard (DES) algorithm. These include:
- S-boxes (Substitution Boxes)
- PC-1 (Permuted Choice 1)
- PC-2 (Permuted Choice 2)
- IP (Initial Permutation)
- E (Expansion Table or E-box)
- P (Permutation Function Table or P-box)
- FP (Final Permutation, which is the inverse of IP)

These constants are critical for the various stages of DES encryption and
decryption, such as key generation, round function computations, and initial/final
data block transformations.
"""

# S-BOXES
s_box_main =  [
"""
S-boxes (Substitution Boxes) for DES.
There are 8 S-boxes, each taking a 6-bit input and producing a 4-bit output.
The input's first and last bits select the row, and the middle four bits select the column.
`s_box_main` is a list of 8 S-boxes (S1 to S8). Each S-box is a list of 4 rows,
and each row is a list of 16 string values (0-15) representing the 4-bit output.
For example, `s_box_main[0]` is S1, `s_box_main[0][0]` is the first row of S1,
and `s_box_main[0][0][0]` is the value in the first row, first column of S1.
"""
#S1
[
['14','4','13','1','2','15','11','8','3','10','6','12','5','9','0','7'],
['0','15','7','4','14','2','13','1','10','6','12','11','9','5','3','8'],
['4','1','14','8','13','6','2','11','15','12','9','7','3','10','5','0'],
['15','12','8','2','4','9','1','7','5','11','3','14','10','0','6','13']
],
#S2
[
['15','1','8','14','6','11','3','4','9','7','2','13','12','0','5','10'],
['3','13','4','7','15','2','8','14','12','0','1','10','6','9','11','5'],
['0','14','7','11','10','4','13','1','5','8','12','6','9','3','2','15'],
['13','8','10','1','3','15','4','2','11','6','7','12','0','5','14','9']
],
#S3
[
['10','0','9','14','6','3','15','5','1','13','12','7','11','4','2','8'],
['13','7','0','9','3','4','6','10','2','8','5','14','12','11','15','1'],
['13','6','4','9','8','15','3','0','11','1','2','12','5','10','14','7'],
['1','10','13','0','6','9','8','7','4','15','14','3','11','5','2','12']
],
#S4
[
['7','13','14','3','0','6','9','10','1','2','8','5','11','12','4','15'],
['13','8','11','5','6','15','0','3','4','7','2','12','1','10','14','9'],
['10','6','9','0','12','11','7','13','15','1','3','14','5','2','8','4'],
['3','15','0','6','10','1','13','8','9','4','5','11','12','7','2','14']
],
#S5
[
['2','12','4','1','7','10','11','6','8','5','3','15','13','0','14','9'],
['14','11','2','12','4','7','13','1','5','0','15','10','3','9','8','6'],
['4','2','1','11','10','13','7','8','15','9','12','5','6','3','0','14'],
['11','8','12','7','1','14','2','13','6','15','0','9','10','4','5','3']
],
#S6
[
['12','1','10','15','9','2','6','8','0','13','3','4','14','7','5','11'],
['10','15','4','2','7','12','9','5','6','1','13','14','0','11','3','8'],
['9','14','15','5','2','8','12','3','7','0','4','10','1','13','11','6'],
['4','3','2','12','9','5','15','10','11','14','1','7','6','0','8','13']
],
#S7
[
['4','11','2','14','15','0','8','13','3','12','9','7','5','10','6','1'],
['13','0','11','7','4','9','1','10','14','3','5','12','2','15','8','6'],
['1','4','11','13','12','3','7','14','10','15','6','8','0','5','9','2'],
['6','11','13','8','1','4','10','7','9','5','0','15','14','2','3','12']
],
#S8
[
['13','2','8','4','6','15','11','1','10','9','3','14','5','0','12','7'],
['1','15','13','8','10','3','7','4','12','5','6','11','0','14','9','2'],
['7','11','4','1','9','12','14','2','0','6','10','13','15','3','5','8'],
['2','1','14','7','4','10','8','13','15','12','9','0','3','5','6','11']
]
]


PC_1 = [
"""
Permuted Choice 1 (PC-1) table.
Used in the DES key schedule to select 56 bits from the initial 64-bit key,
discarding the 8 parity bits (every 8th bit).
The values indicate the position of the bit from the original 64-bit key
(1-indexed) that forms the new 56-bit key.
"""
    57, 49,	41,	33,	25,	17,	9,
    1, 58,	50,	42,	34,	26,	18,
    10,	2,	59,	51,	43,	35,	27,
    19,	11,	3,	60,	52,	44,	36,
    63,	55,	47,	39,	31,	23,	15,
    7,	62,	54,	46,	38,	30,	22,
    14,	6,	61,	53,	45,	37,	29,
    21,	13,	5,	28,	20,	12,	4
    ]

PC_2 = [
"""
Permuted Choice 2 (PC-2) table.
Used in the DES key schedule after the left shifts. It selects 48 bits
from the 56-bit shifted key (CnDn) to form each 48-bit round subkey.
The values indicate the position of the bit from the 56-bit CnDn
(1-indexed) that forms the 48-bit subkey.
"""
        14, 17, 11, 24, 1, 5,
        3, 28, 15, 6, 21, 10,
        23, 19, 12, 4, 26, 8,
        16, 7, 27, 20, 13, 2,
        41, 52, 31, 37, 47, 55,
        30, 40, 51, 45, 33, 48,
        44, 49, 39, 56, 34, 53,
        46, 42, 50, 36, 29, 32 
    ]

IP = [
"""
Initial Permutation (IP) table.
This table defines the initial permutation of each 64-bit data block at the
beginning of the DES encryption/decryption process.
The values indicate the new position (1-indexed, read row by row) for the bit
that was originally at that position. For example, the bit at position 58 in the
input block moves to position 1, the bit at position 50 moves to position 2, and so on.
"""
58,	50,	42,	34,	26,	18,	10,	2,
60,	52,	44,	36,	28,	20,	12,	4,
62,	54,	46,	38,	30,	22,	14,	6,
64,	56,	48,	40,	32,	24,	16,	8,
57,	49,	41,	33,	25,	17,	9,  1,
59,	51,	43,	35,	27,	19,	11,	3,
61,	53,	45,	37,	29,	21,	13,	5,
63,	55,	47,	39,	31,	23,	15,	7
]

expension_table = [
"""
Expansion (E) table, also known as the E-box or E-bit selection table.
Used in the DES round function (Feistel function) to expand the 32-bit right half (R)
of the data to 48 bits, allowing it to be XORed with a 48-bit round subkey.
The values indicate the position of the bit from the 32-bit R_n-1 half (1-indexed)
that is used to form the expanded 48-bit block. Some bits are duplicated.
"""
32,	1,	2,	3,	4,	5,
4,	5,	6,	7,	8,	9,
8,	9,	10,	11,	12,	13,
12,	13,	14,	15,	16,	17,
16,	17,	18,	19,	20,	21,
20,	21,	22,	23,	24,	25,
24,	25,	26,	27,	28,	29,
28,	29,	30,	31,	32,	1
]

f_permutation_table = [
"""
Permutation (P) table, also known as the P-box.
Used in the DES round function (Feistel function) after the S-box substitution.
It permutes the 32-bit output of the S-boxes.
The values indicate the new position (1-indexed) for the bit that was originally
at that position in the 32-bit S-box output.
"""
16,	7,	20,	21,	29,	12,	28,	17,
1,	15,	23,	26,	5,	18,	31,	10,
2,	8,	24,	14,	32,	27,	3,	9,
19,	13,	30,	6,	22,	11,	4,	25
]

final_permutation_table = [
"""
Final Permutation (FP) table, also denoted as IP^-1.
This table defines the final permutation of each 64-bit data block at the end
of the DES encryption/decryption process. It is the inverse of the Initial
Permutation (IP).
The values indicate the new position (1-indexed, read row by row) for the bit
that was originally at that position in the (L16R16_swapped) block.
"""
40,	8,	48,	16,	56,	24,	64,	32,
39,	7,	47,	15,	55,	23,	63,	31,
38,	6,	46,	14,	54,	22,	62,	30,
37,	5,	45,	13,	53,	21,	61,	29,
36,	4,	44,	12,	52,	20,	60,	28,
35,	3,	43,	11,	51,	19,	59,	27,
34,	2,	42,	10,	50,	18,	58,	26,
33,	1,	41,	9,	49,	17,	57,	25
] 
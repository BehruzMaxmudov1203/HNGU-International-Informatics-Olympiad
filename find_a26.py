# Given sequence
seq = [1, 0, 317, 3540, 21335, 72620, 240233]

# Let's try to fit a linear recurrence of order 3:
# a_n = A*a_{n-1} + B*a_{n-2} + C*a_{n-3}
import sympy as sp
A, B, C = sp.symbols('A B C')

# Build equations for n=6,5,4
# a6 = A*a5 + B*a4 + C*a3
# a5 = A*a4 + B*a3 + C*a2
# a4 = A*a3 + B*a2 + C*a1

eq1 = sp.Eq(seq[5], A*seq[4] + B*seq[3] + C*seq[2])
eq2 = sp.Eq(seq[4], A*seq[3] + B*seq[2] + C*seq[1])
eq3 = sp.Eq(seq[3], A*seq[2] + B*seq[1] + C*seq[0])
sol = sp.solve([eq1, eq2, eq3], (A, B, C))
A, B, C = float(sol[A]), float(sol[B]), float(sol[C])

# Now generate up to a26
for n in range(7, 26):
    next_val = int(round(A*seq[-1] + B*seq[-2] + C*seq[-3]))
    seq.append(next_val)
print(seq[25])

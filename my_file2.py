import math
import numpy as np
mm = 0.001
cm = 10 *mm
N = 1
kN = 1000 * N
MPa = N/mm**2
m = 1000 * mm
π = math.pi
b = 230 * cm
print("b = ",  b)
h = 170 * cm
print("h = ",  h)
cc = 75 * mm
print("cc = ",  cc)
fc = 40 * MPa
print("fc = ",  fc)
fy = 520 * MPa
print("fy = ",  fy)
Es = 200000 * MPa
print("Es = ",  Es)
Pu = 1008 * kN
print("Pu = ",  Pu)
Mu = 1172 * kN*m
print("Mu = ",  Mu)
D_1 = 32 * mm
print("D_1 = ",  D_1)
n_1 = 13
print("n_1 = ",  n_1)
D_2 = 32 * mm
print("D_2 = ",  D_2)
n_2 = 11
print("n_2 = ",  n_2)
D_3 = 8 * mm
print("D_3 = ",  D_3)
n_3 = 0
print("n_3 = ",  n_3)
D_4 = 8 * mm
print("D_4 = ",  D_4)
n_4 = 0
print("n_4 = ",  n_4)
D_5 = 8 * mm
print("D_5 = ",  D_5)
n_5 = 0
print("n_5 = ",  n_5)
s_v = 35 * mm
print("s_v = ",  s_v)
D_top = 32 * mm
print("D_top = ",  D_top)
n_top = 0
print("n_top = ",  n_top)
D_w = 20 * mm
print("D_w = ",  D_w)
Seism = 0
print("Seism = ",  Seism)
β_1 = np.where(fc < 28 * MPa, 0.85, np.where(fc > 55 * MPa, 0.65, (1.05 - (0.20 * fc) / (28 * MPa))))

print("β_1 = ",  β_1)
As_top = (n_top * π * D_top ** 2) / 4
print("As_top = ",  As_top)
As_1 = (n_1 * π * D_1 ** 2) / 4
print("As_1 = ",  As_1)
As_2 = (n_2 * π * D_2 ** 2) / 4
print("As_2 = ",  As_2)
As_3 = (n_3 * π * D_3 ** 2) / 4
print("As_3 = ",  As_3)
As_4 = (n_4 * π * D_4 ** 2) / 4
print("As_4 = ",  As_4)
As_5 = (n_5 * π * D_5 ** 2) / 4
print("As_5 = ",  As_5)
As = As_1 + As_2 + As_3 + As_4 + As_5
print("As = ",  As)
d_top = cc + D_w + D_top / 2
print("d_top = ",  d_top)
d_t1 = h - cc - D_w - D_1 / 2
print("d_t1 = ",  d_t1)
d_t2 = d_t1 - s_v - D_1 / 2 - D_2 / 2
print("d_t2 = ",  d_t2)
d_t3 = d_t2 - s_v - D_2 / 2 - D_3 / 2
print("d_t3 = ",  d_t3)
d_t4 = d_t3 - s_v - D_3 / 2 - D_4 / 2
print("d_t4 = ",  d_t4)
d_t5 = d_t4 - s_v - D_4 / 2 - D_5 / 2
print("d_t5 = ",  d_t5)
d_t = (d_t1 * As_1 + d_t2 * As_2 + d_t3 * As_3 + d_t4 * As_4 + d_t4 * As_5) / As
print("d_t = ",  d_t)
ε_s = 0
print("ε_s = ",  ε_s)
c = (0.003 * d_t1) / (ε_s + 0.003)
print("c = ",  c)
a = β_1 * c
print("a = ",  a)
ε_y = fy / Es
print("ε_y = ",  ε_y)
ε_u = 0.003
print("ε_u = ",  ε_u)
ε_s_top = ε_u * (c - d_top) / c
print("ε_s_top = ",  ε_s_top)
ε_s1 = ε_s
print("ε_s1 = ",  ε_s1)
ε_s2 = ε_u * (c - d_t2) / c
print("ε_s2 = ",  ε_s2)
ε_s3 = ε_u * (c - d_t3) / c
print("ε_s3 = ",  ε_s3)
ε_s4 = ε_u * (c - d_t4) / c
print("ε_s4 = ",  ε_s4)
ε_s5 = ε_u * (c - d_t5) / c
print("ε_s5 = ",  ε_s5)
Cc = 0.85 * fc * b * a
print("Cc = ",  Cc)
Cs = np.where(ε_s_top < ε_y, As_top * Es * ε_s_top, (As_top * fy))

print("Cs = ",  Cs)
T_1 = np.where(abs(ε_s1) < ε_y, As_1 * Es * ε_s1, (-(As_1) * fy))

print("T_1 = ",  T_1)
T_2 = np.where(abs(ε_s2) < ε_y, As_2 * Es * ε_s2, (-(As_2) * fy))

print("T_2 = ",  T_2)
T_3 = np.where(abs(ε_s3) < ε_y, As_3 * Es * ε_s3, (-(As_3) * fy))

print("T_3 = ",  T_3)
T_4 = np.where(abs(ε_s4) < ε_y, As_4 * Es * ε_s4, (-(As_4) * fy))

print("T_4 = ",  T_4)
T_5 = np.where(abs(ε_s5) < ε_y, As_5 * Es * ε_s5, (-(As_5) * fy))

print("T_5 = ",  T_5)
T = T_1 + T_2 + T_3 + T_4 + T_5
print("T = ",  T)
P_n1 = Cc + Cs - T
print("P_n1 = ",  P_n1)
M_n1 = Cc * (h / 2 - a / 2) + Cs * (h / 2 - d_top) - T * (d_t - h / 2)
print("M_n1 = ",  M_n1)
Φ = np.where(ε_s1 < 0.002, 0.65, np.where(ε_s1 > 0.005, 0.90, (0.65 + (ε_s1 - 0.002) * 250 / 3)))

print("Φ = ",  Φ)
P_d1 = Φ * P_n1
print("P_d1 = ",  P_d1)
M_d1 = Φ * M_n1
print("M_d1 = ",  M_d1)
e_1 = M_d1 / P_d1
print("e_1 = ",  e_1)
ε_y = fy / Es
print("ε_y = ",  ε_y)
ε_s = 0.5 * ε_y
print("ε_s = ",  ε_s)
c = (0.003 * d_t1) / (ε_s + 0.003)
print("c = ",  c)
a = β_1 * c
print("a = ",  a)
ε_u = 0.003
print("ε_u = ",  ε_u)
ε_s_top = ε_u * (c - d_top) / c
print("ε_s_top = ",  ε_s_top)
ε_s1 = -(ε_s)
print("ε_s1 = ",  ε_s1)
ε_s2 = ε_u * (c - d_t2) / c
print("ε_s2 = ",  ε_s2)
ε_s3 = ε_u * (c - d_t3) / c
print("ε_s3 = ",  ε_s3)
ε_s4 = ε_u * (c - d_t4) / c
print("ε_s4 = ",  ε_s4)
ε_s5 = ε_u * (c - d_t5) / c
print("ε_s5 = ",  ε_s5)
Cc = 0.85 * fc * b * a
print("Cc = ",  Cc)
Cs = np.where(ε_s_top < ε_y, As_top * Es * ε_s_top, (As_top * fy))

print("Cs = ",  Cs)
T_1 = np.where(abs(ε_s1) < ε_y, As_1 * Es * ε_s1, (-(As_1) * fy))

print("T_1 = ",  T_1)
T_2 = np.where(abs(ε_s2) < ε_y, As_2 * Es * ε_s2, (-(As_2) * fy))

print("T_2 = ",  T_2)
T_3 = np.where(abs(ε_s3) < ε_y, As_3 * Es * ε_s3, (-(As_3) * fy))

print("T_3 = ",  T_3)
T_4 = np.where(abs(ε_s4) < ε_y, As_4 * Es * ε_s4, (-(As_4) * fy))

print("T_4 = ",  T_4)
T_5 = np.where(abs(ε_s5) < ε_y, As_5 * Es * ε_s5, (-(As_5) * fy))

print("T_5 = ",  T_5)
T = T_1 + T_2 + T_3 + T_4 + T_5
print("T = ",  T)
P_n2 = Cc + Cs + T
print("P_n2 = ",  P_n2)
M_n2 = Cc * (h / 2 - a / 2) + Cs * (h / 2 - d_top) - T * (d_t - h / 2)
print("M_n2 = ",  M_n2)
Φ = np.where(abs(ε_s1) < 0.002, 0.65, np.where(abs(ε_s1) > 0.005, 0.90, (0.65 + (abs(ε_s1) - 0.002) * 250 / 3)))

print("Φ = ",  Φ)
P_d2 = Φ * P_n2
print("P_d2 = ",  P_d2)
M_d2 = Φ * M_n2
print("M_d2 = ",  M_d2)
e_2 = M_d2 / P_d2
print("e_2 = ",  e_2)
ε_y = fy / Es
print("ε_y = ",  ε_y)
ε_s = ε_y
print("ε_s = ",  ε_s)
c = (0.003 * d_t1) / (ε_s + 0.003)
print("c = ",  c)
a = β_1 * c
print("a = ",  a)
ε_u = 0.003
print("ε_u = ",  ε_u)
ε_s_top = ε_u * (c - d_top) / c
print("ε_s_top = ",  ε_s_top)
ε_s1 = -(ε_s)
print("ε_s1 = ",  ε_s1)
ε_s2 = ε_u * (c - d_t2) / c
print("ε_s2 = ",  ε_s2)
ε_s3 = ε_u * (c - d_t3) / c
print("ε_s3 = ",  ε_s3)
ε_s4 = ε_u * (c - d_t4) / c
print("ε_s4 = ",  ε_s4)
ε_s5 = ε_u * (c - d_t5) / c
print("ε_s5 = ",  ε_s5)
Cc = 0.85 * fc * b * a
print("Cc = ",  Cc)
Cs = np.where(ε_s_top < ε_y, As_top * Es * ε_s_top, (As_top * fy))

print("Cs = ",  Cs)
T_1 = np.where(abs(ε_s1) < ε_y, As_1 * Es * ε_s1, (-(As_1) * fy))

print("T_1 = ",  T_1)
T_2 = np.where(abs(ε_s2) < ε_y, As_2 * Es * ε_s2, (-(As_2) * fy))

print("T_2 = ",  T_2)
T_3 = np.where(abs(ε_s3) < ε_y, As_3 * Es * ε_s3, (-(As_3) * fy))

print("T_3 = ",  T_3)
T_4 = np.where(abs(ε_s4) < ε_y, As_4 * Es * ε_s4, (-(As_4) * fy))

print("T_4 = ",  T_4)
T_5 = np.where(abs(ε_s5) < ε_y, As_5 * Es * ε_s5, (-(As_5) * fy))

print("T_5 = ",  T_5)
T = T_1 + T_2 + T_3 + T_4 + T_5
print("T = ",  T)
P_n3 = Cc + Cs + T
print("P_n3 = ",  P_n3)
M_n3 = Cc * (h / 2 - a / 2) + Cs * (h / 2 - d_top) - T * (d_t - h / 2)
print("M_n3 = ",  M_n3)
Φ = np.where(abs(ε_s1) < 0.002, 0.65, np.where(abs(ε_s1) > 0.005, 0.90, (0.65 + (abs(ε_s1) - 0.002) * 250 / 3)))

print("Φ = ",  Φ)
P_d3 = Φ * P_n3
print("P_d3 = ",  P_d3)
M_d3 = Φ * M_n3
print("M_d3 = ",  M_d3)
e_3 = M_d3 / P_d3
print("e_3 = ",  e_3)
ε_y = fy / Es
print("ε_y = ",  ε_y)
ε_s = 0.005
print("ε_s = ",  ε_s)
c = (0.003 * d_t1) / (ε_s + 0.003)
print("c = ",  c)
a = β_1 * c
print("a = ",  a)
ε_u = 0.003
print("ε_u = ",  ε_u)
ε_s_top = ε_u * (c - d_top) / c
print("ε_s_top = ",  ε_s_top)
ε_s1 = -(ε_s)
print("ε_s1 = ",  ε_s1)
ε_s2 = ε_u * (c - d_t2) / c
print("ε_s2 = ",  ε_s2)
ε_s3 = ε_u * (c - d_t3) / c
print("ε_s3 = ",  ε_s3)
ε_s4 = ε_u * (c - d_t4) / c
print("ε_s4 = ",  ε_s4)
ε_s5 = ε_u * (c - d_t5) / c
print("ε_s5 = ",  ε_s5)
Cc = 0.85 * fc * b * a
print("Cc = ",  Cc)
Cs = np.where(ε_s_top < ε_y, As_top * Es * ε_s_top, (As_top * fy))

print("Cs = ",  Cs)
T_1 = np.where(abs(ε_s1) < ε_y, As_1 * Es * ε_s1, -((As_1 * fy)))

print("T_1 = ",  T_1)
T_2 = np.where(abs(ε_s2) < ε_y, As_2 * Es * ε_s2, (-(As_2) * fy))

print("T_2 = ",  T_2)
T_3 = np.where(abs(ε_s3) < ε_y, As_3 * Es * ε_s3, (-(As_3) * fy))

print("T_3 = ",  T_3)
T_4 = np.where(abs(ε_s4) < ε_y, As_4 * Es * ε_s4, (-(As_4) * fy))

print("T_4 = ",  T_4)
T_5 = np.where(abs(ε_s5) < ε_y, As_5 * Es * ε_s5, (-(As_5) * fy))

print("T_5 = ",  T_5)
T = T_1 + T_2 + T_3 + T_4 + T_5
print("T = ",  T)
P_n4 = Cc + Cs + T
print("P_n4 = ",  P_n4)
M_n4 = Cc * (h / 2 - a / 2) + Cs * (h / 2 - d_top) - T * (d_t - h / 2)
print("M_n4 = ",  M_n4)
Φ = np.where(abs(ε_s1) < 0.002, 0.65, np.where(abs(ε_s1) > 0.005, 0.90, (0.65 + (abs(ε_s1) - 0.002) * 250 / 3)))

print("Φ = ",  Φ)
P_d4 = Φ * P_n4
print("P_d4 = ",  P_d4)
M_d4 = Φ * M_n4
print("M_d4 = ",  M_d4)
e_4 = M_d4 / P_d4
print("e_4 = ",  e_4)
P_n0 = 0.85 * fc * (b * h - As - As_top) + fy * (As + As_top)
print("P_n0 = ",  P_n0)
P_nmax = 0.8 * P_n0
print("P_nmax = ",  P_nmax)
Φ = 0.65
print("Φ = ",  Φ)
P_d0 = Φ * P_n0
print("P_d0 = ",  P_d0)
P_dmax = Φ * P_nmax
print("P_dmax = ",  P_dmax)
T_n0 = -((As + As_top)) * fy
print("T_n0 = ",  T_n0)
Φ = 0.9
print("Φ = ",  Φ)
T_d0 = Φ * T_n0
print("T_d0 = ",  T_d0)
a = (As * fy) / (0.85 * b * fc)
print("a = ",  a)
c = a / β_1
print("c = ",  c)
ε_s = ((d_t - c)) / c * 0.003
print("ε_s = ",  ε_s)
M_n0 = As * fy * (d_t - a / 2)
print("M_n0 = ",  M_n0)
Φ = 0.9
print("Φ = ",  Φ)
M_d0 = Φ * M_n0
print("M_d0 = ",  M_d0)
def M1(x):
	 return M_n1 / (P_n1 - P_n0) * (x - P_n0)
def M2(x):
	 return (M_n2 - M_n1) / (P_n2 - P_n1) * (x - P_n1) + M_n1
def M3(x):
	 return (M_n3 - M_n2) / (P_n3 - P_n2) * (x - P_n2) + M_n2
def M4(x):
	 return (M_n4 - M_n3) / (P_n4 - P_n3) * (x - P_n3) + M_n3
def M5(x):
	 return (M_n0 - M_n4) / (0 - P_n4) * (x - P_n4) + M_n4
def M6(x):
	 return (0 - M_n0) / T_n0 * (x - 0) + M_n0
def Md1(x):
	 return M_d1 / (P_d1 - P_d0) * (x - P_d0)
def Md2(x):
	 return (M_d2 - M_d1) / (P_d2 - P_d1) * (x - P_d1) + M_d1
def Md3(x):
	 return (M_d3 - M_d2) / (P_d3 - P_d2) * (x - P_d2) + M_d2
def Md4(x):
	 return (M_d4 - M_d3) / (P_d4 - P_d3) * (x - P_d3) + M_d3
def Md5(x):
	 return (M_d0 - M_d4) / (0 - P_d4) * (x - P_d4) + M_d4
def Md6(x):
	 return (0 - M_d0) / T_d0 * (x - 0) + M_d0
def MU1(x):
	 return (M_n1 / (1 * kN * m)) / (((P_n1 - P_n0) / (1 * kN))) * (x - P_n0 / (1 * kN))
def MU2(x):
	 return ((M_n2 - M_n1) / (1 * kN * m)) / (((P_n2 - P_n1) / (1 * kN))) * (x - P_n1 / (1 * kN)) + M_n1 / (1 * kN * m)
def MU3(x):
	 return ((M_n3 - M_n2) / (1 * kN * m)) / (((P_n3 - P_n2) / (1 * kN))) * (x - P_n2 / (1 * kN)) + M_n2 / (1 * kN * m)
def MU4(x):
	 return ((M_n4 - M_n3) / (1 * kN * m)) / (((P_n4 - P_n3) / (1 * kN))) * (x - P_n3 / (1 * kN)) + M_n3 / (1 * kN * m)
def MU5(x):
	 return ((M_n0 - M_n4) / (1 * kN * m)) / (((0 - P_n4) / (1 * kN))) * (x - P_n4 / (1 * kN)) + M_n4 / (1 * kN * m)
def MU6(x):
	 return ((0 - M_n0) / (1 * kN * m)) / (T_n0 / (1 * kN)) * (x - 0) + M_n0 / (1 * kN * m)
def MUd1(x):
	 return (M_d1 / (1 * kN * m)) / (((P_d1 - P_d0) / (1 * kN))) * (x - P_d0 / (1 * kN))
def MUd2(x):
	 return ((M_d2 - M_d1) / (1 * kN * m)) / (((P_d2 - P_d1) / (1 * kN))) * (x - P_d1 / (1 * kN)) + M_d1 / (1 * kN * m)
def MUd3(x):
	 return ((M_d3 - M_d2) / (1 * kN * m)) / (((P_d3 - P_d2) / (1 * kN))) * (x - P_d2 / (1 * kN)) + M_d2 / (1 * kN * m)
def MUd4(x):
	 return ((M_d4 - M_d3) / (1 * kN * m)) / (((P_d4 - P_d3) / (1 * kN))) * (x - P_d3 / (1 * kN)) + M_d3 / (1 * kN * m)
def MUd5(x):
	 return ((M_d0 - M_d4) / (1 * kN * m)) / (((0 - P_d4) / (1 * kN))) * (x - P_d4 / (1 * kN)) + M_d4 / (1 * kN * m)
def MUd6(x):
	 return ((0 - M_d0) / (1 * kN * m)) / (T_d0 / (1 * kN)) * (x - 0) + M_d0 / (1 * kN * m)
def MUd(x):
	MUd = np.where(T_d0 / (1 * kN) <= x < 0, MUd6(x), np.where(0 <= x < P_d4 / (1 * kN), MUd5(x), np.where(P_d4 / (1 * kN) <= x < P_d3 / (1 * kN), MUd4(x), np.where(P_d3 / (1 * kN) <= x < P_d2 / (1 * kN), MUd3(x), np.where(P_d2 / (1 * kN) <= x < P_d1 / (1 * kN), MUd2(x), np.where(P_d1 / (1 * kN) <= x <= P_dmax / (1 * kN), MUd1(x), 0))))))
	return MUd
def M(x):
	M = np.where(T_n0 <= x < 0 * kN, M6(x), np.where(0 * kN <= x < P_n4, M5(x), np.where(P_n4 <= x < P_n3, M4(x), np.where(P_n3 <= x < P_n2, M3(x), np.where(P_n2 <= x < P_n1, M2(x), np.where(P_n1 <= x <= P_nmax, M1(x), 0))))))
	return M
def Md(x):
	Md = np.where(T_d0 <= x < 0 * kN, Md6(x), np.where(0 * kN <= x < P_d4, Md5(x), np.where(P_d4 <= x < P_d3, Md4(x), np.where(P_d3 <= x < P_d2, Md3(x), np.where(P_d2 <= x < P_d1, Md2(x), np.where(P_d1 <= x <= P_dmax, Md1(x), 0))))))
	return Md
def MU(x):
	MU = np.where(T_n0 / (1 * kN) <= x < 0, MU6(x), np.where(0 <= x < P_n4 / (1 * kN), MU5(x), np.where(P_n4 / (1 * kN) <= x < P_n3 / (1 * kN), MU4(x), np.where(P_n3 / (1 * kN) <= x < P_n2 / (1 * kN), MU3(x), np.where(P_n2 / (1 * kN) <= x < P_n1 / (1 * kN), MU2(x), np.where(P_n1 / (1 * kN) <= x <= P_nmax / (1 * kN), MU1(x), 0))))))
	return MU
Pmax = P_n0 / (1 * kN)
print("Pmax = ",  Pmax)
Pmin = T_n0 / (1 * kN)
print("Pmin = ",  Pmin)
Mmax = (M_n3 + 50 * kN * m) / (1 * kN * m)
print("Mmax = ",  Mmax)
Nu = Pu / (1 * kN)
print("Nu = ",  Nu)
MU = Mu / (1 * kN * m)
print("MU = ",  MU)
Md = Md(Pu)
print("Md = ",  Md)
Result = np.where(Mu <= Md, "ok", "not ok")

print("Result = ",  Result)
s = (b - 2 * cc - 2 * D_w - n_1 * D_1) / (n_1 - 1)
print("s = ",  s)
fs = (2 * fy) / 3
print("fs = ",  fs)
s_max = min([380 * mm * (280 * MPa) / fs - 2.5 * cc,300 * mm * (280 * MPa) / fs])
print("s_max = ",  s_max)
Result1 = np.where(s <= s_max, "ok", "not ok")

print("Result1 = ",  Result1)
s_min = max([25 * mm,D_1])
print("s_min = ",  s_min)
Result2 = np.where(s >= s_min, "ok", "not ok")

print("Result2 = ",  Result2)
As_min = max([(0.25 * np.sqrt(1 * MPa) * np.sqrt(fc)) / fy * b * d_t,(1.4 * MPa) / fy * b * d_t])
print("As_min = ",  As_min)
Result3 = np.where(As >= As_min, "ok", "not ok")

print("Result3 = ",  Result3)
As_max = 0.08 * b * h
print("As_max = ",  As_max)
Result4 = np.where(As <= As_max, "ok", "not ok")

print("Result4 = ",  Result4)
Type = np.where(Pu <= b * h * fc / 10, "Flexural members", "Column behaviour")

print("Type = ",  Type)
CheckFc = np.where((fc >= 21 * MPa) | (Seism == 0), "ok", "not ok !!! --> fc must be greater than 21MPa")

print("CheckFc = ",  CheckFc)
CheckAg1 = np.where((min([b,h]) >= 300 * mm) | (Seism == 0), "ok", "not ok !!! --> b and h must be greater than 30cm !!!")

print("CheckAg1 = ",  CheckAg1)
CheckAg1 = np.where(Type != "Column behaviour", "ok", CheckAg1)

print("CheckAg1 = ",  CheckAg1)
CheckAg2 = np.where((min([b / h,h / b]) >= 0.4) | (Seism == 0), "ok", "not ok !!! --> ratiob/h and h/b must be greater than 0,4 !!!")

print("CheckAg2 = ",  CheckAg2)
CheckAg2 = np.where(Type != "Column behaviour", "ok", CheckAg2)

print("CheckAg2 = ",  CheckAg2)
CheckBw = np.where((b >= min([0.3 * h,250 * mm])) | (Seism == 0), "ok", "not ok !!! --> increase b !!!")

print("CheckBw = ",  CheckBw)
CheckBw = np.where(Type != "Flexural members", "ok", CheckBw)

print("CheckBw = ",  CheckBw)
As_max = np.where((Seism == 1) & (Type == "Column behaviour"), 0.06 * b * h, np.where((Seism == 1) & (Type == "Flexural members"), (0.025 * b * h), As_max))

print("As_max = ",  As_max)
Result4 = np.where(As <= As_max, "ok", "not ok")

print("Result4 = ",  Result4)

import numpy as np
# input data
ins = [[831600.3,816239.1], [831587.1,815578.1], [832562.3,816239.9]]  # <- points
out = [[1113,766], [1113, 0], [0, 766]] # <- mapped to
# calculations
l = len(ins)
B = np.vstack([np.transpose(ins), np.ones(l)])
D = 1.0 / np.linalg.det(B)
entry = lambda r,d: np.linalg.det(np.delete(np.vstack([r, B]), (d+1), axis=0))
M = [[(-1)**i * D * entry(R, i) for i in range(l)] for R in np.transpose(out)]
A, t = np.hsplit(np.array(M), [l-1])
t = np.transpose(t)[0]
# output
print("Affine transformation matrix:\n", A)
print("Affine transformation translation vector:\n", t)
# unittests
print("TESTING:")
for p, P in zip(np.array(ins), np.array(out)):
  image_p = np.dot(A, p) + t
  result = "[OK]" if np.allclose(image_p, P) else "[ERROR]"
  print(p, " mapped to: ", image_p, " ; expected: ", P, result)
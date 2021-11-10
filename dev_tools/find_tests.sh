find . -type d \(                      \
  -path ./build -o                     \
  -path ./recirq/qaoa -o               \
  -path ./recirq/hfvqe -o              \
  -path ./recirq/optimize -o           \
  -path ./recirq/otoc -o               \
  -path ./recirq/fermi_hubbard         \
\) -prune -o -name '*_test.py' -print

import numpy as np

class ComplexLinearSolver:
    # initialize empty matrices and solution
    def __init__(self, rows, cols, name):
        self.A, self.B, self.solution= None, None, None
        self.rows = rows
        self.cols = cols
        self.name = name
    # runs whenever class is called

    def get_complex_matrix(self, rows, cols, name):
        # Create a complex matrix with given dimensions
        matrix = np.zeros((rows, cols), dtype=complex)
        print(f"\nEnter values for matrix {name} ({rows}x{cols})")
        print("Each entry should be two numbers (real and imaginary) separated by space (e.g. 2 3 for 2+3j)\n")

        count = 1
        for i in range(rows):
            for j in range(cols):
                while True:
                    try:
                        user_input = input(f"{name}[{i + 1}][{j + 1}] (real imag) #{count}: ").split()
                        if len(user_input) != 2:
                            raise ValueError("Please enter exactly two numbers.")
                        real, imag = map(float, user_input)
                        matrix[i, j] = complex(real, imag)
                        count += 1
                        break
                    except ValueError as e:
                        print(f"Invalid input: {e}")
        return matrix
    # matrices' sizes
    def input_matrices(self, get_complex_matrix):
        self.A = get_complex_matrix(2, 2, "A")
        self.B = get_complex_matrix(2, 1, "B")

    # display matrices
    def display_matrices(self):
        # Print matrices A and B
        print("\nMatrix A:", self.A)
        print("\nMatrix B:", self.B)

    # solve the equation
    def solve(self):
        try:
            self.solution = np.linalg.inv(self.A) @ self.B # inverse of A * B
            print("\nSolution (x, y):\n", self.solution)
        except np.linalg.LinAlgError:
            print("\nMatrix A is not invertible. Cannot solve the system.")
            self.solution = None

    # check if the computed solution satisfies A * x ≈ B
    def verify_solution(self):
        if self.solution is not None:
            if np.allclose(self.A @ self.solution, self.B):
                print("\nThe solution is correct (A @ x ≈ B).")
            else:
                print("\nThe solution is not correct (A @ x ≠ B).")

    # run all steps in order
    def run(self):
        self.input_matrices(self.get_complex_matrix)
        self.display_matrices()
        self.solve()
        self.verify_solution()



import numpy as np

class MatrixOperations:
    #constructor -> gives initial values to variables
    def __init__(self):
        self.matrix1 = None
        self.matrix2 = None
    # runs everytime you call the class

    # check if input is a number
    @staticmethod #decorator -> independent method but related to class
    def check_valid_int_input(prompt): #prompt -> message that will be printed to the screen before asking a data
        while True:
            try: #might give error
                return list(map(int, input(prompt).split()))  # convert into integer to every input
            except ValueError: #what will program do if error occurs
                print("Please enter valid integer(s) only.")

    # create two matrices
    def create_matrices(self):
        m, n = self.check_valid_int_input("Enter rows and columns for Matrix A (e.g. 2 3): ")
        # can't be called with its name directly
        # className.method or self.method

        print(f"\nEnter Matrix A ({m}x{n}):")
        print(f"Each row must contain {n} values, separated by space:")

        self.matrix1 = self.get_matrix_input(m, n, "Matrix A")

        p = self.check_valid_int_input(f"\nEnter number of columns for Matrix B (rows will be {n}): ")[0]

        print(f"\nEnter Matrix B ({n}x{p}):")
        print(f"Each row must contain {p} values, separated by space:")

        self.matrix2 = self.get_matrix_input(n, p, "Matrix B")
        print("\nTwo matrices are created!")

    # get matrix input row by row
    def get_matrix_input(self, rows, cols, name="Matrix"):
        matrix = []
        for i in range(rows):
            row = self.check_valid_int_input(f"{name} - Row {i + 1}: ")
            while len(row) != cols:  # check if row's length is equal to column number
                print(f"\nYou must enter exactly {cols} values.")
                row = self.check_valid_int_input(f"{name} - Row {i + 1} (try again): ")
            matrix.append(row)
        return np.array(matrix)

    # multiply matrices using numpy
    def multiply(self):
        print(f"\nMultiplication of matrices is:\n{self.matrix1 @ self.matrix2}")
        # @ -> multiplies two matrices at numpy

    # add matrices if their shapes are the same
    def add(self):
        if self.matrix1.shape == self.matrix2.shape:  # sizes must be equal to add two matrices
            print(f"\nSum of matrices:\n{self.matrix1 + self.matrix2}")
        else:
            print("\nSince sizes aren't equal, adding can't be done.")

    # get transpose of each matrix
    def transpose(self):
        print(f"\nTranspose of Matrix A:\n{self.matrix1.T}")  # find matrix's transpose using numpy
        print(f"\nTranspose of Matrix B:\n{self.matrix2.T}")

    # calculate row-wise and column-wise means
    def mean(self):
        print(f"\nMean of Matrix A's rows: {self.matrix1.mean(axis=1)}")  # calculate mean of numbers at rows
        print(f"Mean of Matrix A's columns: {self.matrix1.mean(axis=0)}")  # calculate mean of numbers at columns
        print(f"\nMean of Matrix B's rows: {self.matrix2.mean(axis=1)}")
        print(f"Mean of Matrix B's columns: {self.matrix2.mean(axis=0)}")

    # calculate determinant and inverse if square matrix
    def determinant(self):
        #loop makes it faster, no duplicate code
        for name, matrix in [("Matrix A", self.matrix1), ("Matrix B", self.matrix2)]:
            if matrix.shape[0] == matrix.shape[1]:  # check if it's a square matrix
                det = np.linalg.det(matrix)  # calculate determinant using numpy
                print(f"\nDeterminant of {name}:\n{det}")
                if abs(det) >= 1e-10:  # check if number's absolute value is not close or equal to zero
                    inv = np.linalg.inv(matrix)  # find inverse of matrix using numpy
                    print(f"\nInverse of {name}:\n{inv}")
                else:
                    print(f"\n{name} is singular or nearly singular, inverse not available.")
            else:
                print(f"\n{name} is not a square matrix, determinant and inverse can't be calculated.")


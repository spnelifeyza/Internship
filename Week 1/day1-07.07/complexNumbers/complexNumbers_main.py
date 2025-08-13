from day1.complexNumbers.complexNumbers import ComplexLinearSolver

def main():
    # instantiate and run the solver directly
    solver = ComplexLinearSolver(rows=None, cols=None, name=None)
    solver.run()

# run only if this file is executed directly
if __name__ == "__main__":
    main()

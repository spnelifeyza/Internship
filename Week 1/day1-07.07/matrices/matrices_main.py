from matrices import MatrixOperations

def main():
    #creating object from a class
    var = MatrixOperations()
    var.create_matrices() #creating matrices

    #asking user choice
    while True:
        print("\n=== Matrix Operations Menu ===")
        print("1. Multiply the matrices")
        print("2. Add the matrices")
        print("3. Transposes of matrices")
        print("4. Means of rows and columns of matrices")
        print("5. Determinant and inverse of matrices")
        print("q. Quit")

        choice = input("Select an option: ").lower()

        match choice:
            case '1':
                var.multiply()
            case '2':
                var.add()
            case '3':
                var.transpose()
            case '4':
                var.mean()
            case '5':
                var.determinant()
            case 'q':
                print("\nExiting program...")
                break
            case _:
                print("Invalid input. Please try again.")

#if file runs directly, executes
#if file is imported, doesn't work
if __name__ == "__main__":
    main()
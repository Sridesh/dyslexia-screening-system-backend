with open("test_execution.txt", "w") as f:
    f.write("Execution successful at " + str(__import__('datetime').datetime.now()))
print("Test file written")

import llvmlite
import llvmlite.binding as llvm

# Check llvmlite version to determine if initialization is needed
version = [int(p) for p in llvmlite.__version__.split('.')[:2]]

if version < [0, 45]:
    # Older versions require explicit initialization
    llvm.initialize()
    print("intialized")
else:
    print("not intialized")

# No initialization needed for version 0.45+

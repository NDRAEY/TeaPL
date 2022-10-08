# TeaPL

TeaPL - hobby programming language.

It's remake of CharmeleonPL

Currently, it transpiles code into C source.

# Features

- [x] Standard types
	- [x] Numerals (uint, int, short, ...)
	- [x] String
	- [ ] Own types creation
- [x] Variables
	- [x] Assign
	- [x] Reassign
- [x] Functions
	- [ ] Value-Returnable
		- [ ] Return any value
	- [x] Non-Value-Returnable
- [x] Control flow
	- [x] if
	- [x] elif
	- [x] else
- [ ] Loops
	- [x] while
	- [ ] for
	- [ ] endless
	- [ ] break / continue
- [ ] Standard library
- [ ] String concatenation
- [ ] Arrays
	- [x] Single-type
	- [x] Multi-dimensional arrays
	- [ ] Indexing
	- [ ] Indexing and assigning
	- [ ] Multi-type
- [ ] Dictionaries
- [ ] Overflow prevention
- [ ] Pointers
- [ ] Memory safety
- [ ] FFI
	- [x] Minimal

# Installation (for Linux)

Make sure `clang` or `gcc` installed

1. Clone repository:
	```bash
	git clone https://github.com/NDRAEY/TeaPL
	```

2. Enter directory and install package:
	```bash
	cd TeaPL
	python3 setup.py install
	```

3. Now, you have the `teapl` program installed!

# Usage

```bash
teapl program.tea
```

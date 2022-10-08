from shutil import which

def find():
	supported = [
		"gcc",
		"clang"
	]

	for i in supported:
		for j in range(11, 16):
			if compiler := which(i+"-"+str(j)):
				return compiler

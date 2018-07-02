gen:
	@ python psim.py > tmp/main.cpp 2>&1

run: gen
	@ g++ -o tmp/main.exe tmp/main.cpp
	@ tmp/main.exe
pretty:
	@ python psim.py > tmp/temp.cpp 2>&1
	@ astyle -n -F -xe tmp/temp.cpp >/dev/null
	@ cat -s tmp/temp.cpp > tmp/main.cpp
	@ rm tmp/temp.cpp

gen:
	@ python psim.py > tmp/main.cpp

run: pretty compile
	@ tmp/main.exe

compile:
	@ g++ -fdiagnostics-color=always -o tmp/main.exe tmp/main.cpp

rerun: compile
	@ tmp/main.exe

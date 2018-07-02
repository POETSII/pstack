gen:
	@ python psim.py > tmp/main.cpp 2>&1

pretty:
	@ python psim.py > tmp/temp.cpp 2>&1
	@ astyle -n -F -xe tmp/temp.cpp >/dev/null
	@ cat -s tmp/temp.cpp > tmp/main.cpp
	@ rm tmp/temp.cpp

run: pretty
	@ g++ -o tmp/main.exe tmp/main.cpp
	@ tmp/main.exe
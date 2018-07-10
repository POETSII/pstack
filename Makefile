POETS_XML="tmp/output.xml"
GEN_SRC_FILE="tmp/main.cpp"
GEN_OBJ_FILE="tmp/main.exe"

sim:
	@ python psim.py --output $(GEN_SRC_FILE) $(POETS_XML)

pretty: gen
	@ astyle -n -F -xe $(GEN_SRC_FILE) >/dev/null

gen:
	@ python psim.py --norun --output $(GEN_SRC_FILE) $(POETS_XML)

compile:
	@ g++ -fdiagnostics-color=always -o $(GEN_OBJ_FILE) $(GEN_SRC_FILE)

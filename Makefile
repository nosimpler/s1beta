# Makefile for nrn
# v 0.1
# rev 2012-07-10
# last rev:

# macros
ECHO = /bin/echo
MV = /bin/mv
UNAME := $(shell uname)

PROJ = nrntest

MOD = ar.mod ca.mod cad.mod cat.mod kca.mod km.mod

vpath %.mod mod/

# make rules
x86_64/special : mod
	nrnivmodl $<
	# $(MV) bin/$@ bin/$@.autobak
	# $(CC) $(CFLAGS) -o bin/$@ $+
	@$(ECHO) '-------------------------------------------------------'
	@$(ECHO) 'make built [$@] successfully. Now go save the stupid princess.'
	@$(ECHO) '-------------------------------------------------------'

# clean
.PHONY: clean
clean :
	rm -f *.o
	rm -f obj/*.o

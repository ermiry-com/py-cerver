TYPE		:= development

NATIVE		:= 0

COVERAGE	:= 0

DEBUG		:= 0

PTHREAD 	:= -l pthread
MATH		:= -lm

OPENSSL		:= -l ssl -l crypto

CURL		:= -l curl

DEFINES		:= -D _GNU_SOURCE

BASE_DEBUG	:= -D CERVER_DEBUG -D CERVER_STATS 				\
				-D CLIENT_DEBUG -D CLIENT_STATS 			\
				-D CONNECTION_DEBUG -D CONNECTION_STATS 	\
				-D HANDLER_DEBUG 							\
				-D PACKETS_DEBUG 							\
				-D AUTH_DEBUG 								\
				-D ADMIN_DEBUG								\
				-D FILES_DEBUG								\
				-D THREADS_DEBUG

HAND_DEBUG	:= -D HANDLER_DEBUG -D SOCKET_DEBUG
RECV_DEBUG	:= -D RECEIVE_DEBUG -D CLIENT_RECEIVE_DEBUG

EXTRA_DEBUG	:= $(HAND_DEBUG) $(RECV_DEBUG)

HTTP_DEBUG	:= -D HTTP_DEBUG -D HTTP_HEADERS_DEBUG			\
				-D HTTP_AUTH_DEBUG -D HTTP_MPART_DEBUG		\
				-D HTTP_RESPONSE_DEBUG						\
				-D HTTP_ADMIN_DEBUG

HTTP_EXTRA_DEBUG = HTTP_RECEIVE_DEBUG

DEVELOPMENT := $(BASE_DEBUG) $(HTTP_DEBUG)

CC          := gcc

GCCVGTEQ8 	:= $(shell expr `gcc -dumpversion | cut -f1 -d.` \>= 8)

SRCEXT      := c
DEPEXT      := d
OBJEXT      := o

# tests
TESTDIR		:= test
TESTBUILD	:= $(TESTDIR)/objs
TESTTARGET	:= $(TESTDIR)/bin
TESTCOVDIR	:= $(COVDIR)/test

TESTFLAGS	:= -g $(DEFINES) -Wall -Wno-unknown-pragmas -Wno-format

ifeq ($(TYPE), test)
	ifeq ($(COVERAGE), 1)
		TESTFLAGS += -fprofile-arcs -ftest-coverage
	endif
endif

ifeq ($(NATIVE), 1)
	TESTFLAGS += -march=native
endif

TESTLIBS	:= -L /usr/local/lib $(PTHREAD)

TESTLIBS += -l cerver

ifeq ($(TYPE), test)
	ifeq ($(COVERAGE), 1)
		TESTLIBS += -lgcov --coverage
	endif
endif

TESTINC		:= -I ./$(TESTDIR)

TESTS		:= $(shell find $(TESTDIR) -type f -name *.$(SRCEXT))
TESTOBJS	:= $(patsubst $(TESTDIR)/%,$(TESTBUILD)/%,$(TESTS:.$(SRCEXT)=.$(OBJEXT)))

TESTCOVS	:= $(patsubst $(TESTDIR)/%,$(TESTBUILD)/%,$(TESTS:.$(SRCEXT)=.$(SRCEXT).$(COVEXT)))

TESTAPP		:= ./$(TESTTARGET)/app/libapp.so
TESTAPPSRC  := $(shell find $(TESTDIR)/app -type f -name *.$(SRCEXT))

TESTAPPFGS	:= $(DEFINES) -D_FORTIFY_SOURCE=2 -O2 -fPIC

ifeq ($(TYPE), development)
	TESTAPPFGS += -g
endif

ifeq ($(DEBUG), 1)
	TESTAPPFGS += -D TEST_APP_DEBUG
endif

# check which compiler we are using
ifeq ($(CC), g++) 
	TESTAPPFGS += -std=c++11 -fpermissive
else
	TESTAPPFGS += -std=c11 -Wpedantic -pedantic-errors
endif

TESTAPPFGS += $(COMMON)

TESTAPPLIBS := -L /usr/local/lib -l cerver

TESTAPPLIB	:= -Wl,-rpath=./$(TESTTARGET)/app -L ./$(TESTTARGET)/app -l app

testapp:
	@mkdir -p ./$(TESTTARGET)/app
	$(CC) $(TESTAPPFGS) $(TESTAPPSRC) -shared -o $(TESTAPP) $(TESTAPPLIBS)

INTCLIENTIN		:= ./$(TESTBUILD)/client
INTCLIENTOUT	:= ./$(TESTTARGET)/client
INTCLIENTLIBS	:= $(TESTLIBS) -Wl,-rpath=./$(TESTTARGET)/app -L ./$(TESTTARGET)/app -l app

integration-client:
	$(CC) $(TESTINC) $(INTCLIENTIN)/ping.o -o $(INTCLIENTOUT)/ping $(TESTLIBS)

INTWEBCLIENTIN		:= ./$(TESTBUILD)/client/web
INTWEBCLIENTOUT		:= ./$(TESTTARGET)/client/web
INTWEBCLIENTLIBS	:= $(TESTLIBS) $(CURL)

integration-web-client:
	@mkdir -p ./$(TESTTARGET)/client/web
	$(CC) $(TESTINC) $(INTWEBCLIENTIN)/admin.o $(INTWEBCLIENTIN)/curl.o -o $(INTWEBCLIENTOUT)/admin $(INTWEBCLIENTLIBS)
	$(CC) $(TESTINC) $(INTWEBCLIENTIN)/api.o $(INTWEBCLIENTIN)/curl.o -o $(INTWEBCLIENTOUT)/api $(INTWEBCLIENTLIBS)
	$(CC) $(TESTINC) $(INTWEBCLIENTIN)/auth.o $(INTWEBCLIENTIN)/curl.o -o $(INTWEBCLIENTOUT)/auth $(INTWEBCLIENTLIBS)
	$(CC) $(TESTINC) $(INTWEBCLIENTIN)/jobs.o $(INTWEBCLIENTIN)/curl.o -o $(INTWEBCLIENTOUT)/jobs $(INTWEBCLIENTLIBS)
	$(CC) $(TESTINC) $(INTWEBCLIENTIN)/json.o $(INTWEBCLIENTIN)/curl.o -o $(INTWEBCLIENTOUT)/json $(INTWEBCLIENTLIBS)
	$(CC) $(TESTINC) $(INTWEBCLIENTIN)/multi.o $(INTWEBCLIENTIN)/curl.o -o $(INTWEBCLIENTOUT)/multi $(INTWEBCLIENTLIBS)
	$(CC) $(TESTINC) $(INTWEBCLIENTIN)/multiple.o $(INTWEBCLIENTIN)/curl.o -o $(INTWEBCLIENTOUT)/multiple $(INTWEBCLIENTLIBS)
	$(CC) $(TESTINC) $(INTWEBCLIENTIN)/query.o $(INTWEBCLIENTIN)/curl.o -o $(INTWEBCLIENTOUT)/query $(INTWEBCLIENTLIBS)
	$(CC) $(TESTINC) $(INTWEBCLIENTIN)/upload.o $(INTWEBCLIENTIN)/curl.o -o $(INTWEBCLIENTOUT)/upload $(INTWEBCLIENTLIBS)
	$(CC) $(TESTINC) $(INTWEBCLIENTIN)/web.o $(INTWEBCLIENTIN)/curl.o -o $(INTWEBCLIENTOUT)/web $(INTWEBCLIENTLIBS)
	$(CC) $(TESTINC) $(INTWEBCLIENTIN)/validation.o $(INTWEBCLIENTIN)/curl.o -o $(INTWEBCLIENTOUT)/validation $(INTWEBCLIENTLIBS)
	$(CC) $(TESTINC) $(INTWEBCLIENTIN)/worker.o $(INTWEBCLIENTIN)/curl.o -o $(INTWEBCLIENTOUT)/worker $(INTWEBCLIENTLIBS)
	$(CC) $(TESTINC) $(INTWEBCLIENTIN)/wrapper.o $(INTWEBCLIENTIN)/curl.o -o $(INTWEBCLIENTOUT)/wrapper $(INTWEBCLIENTLIBS)

integration: testout $(TESTOBJS)
	$(MAKE) integration-client
	$(MAKE) integration-web-client

testout:
	@mkdir -p ./$(TESTTARGET)
	@mkdir -p ./$(TESTTARGET)/client
	@mkdir -p ./$(TESTTARGET)/client/web

test: testout
	$(MAKE) $(TESTOBJS)
	$(MAKE) testapp
	$(MAKE) integration

# compile tests
$(TESTBUILD)/%.$(OBJEXT): $(TESTDIR)/%.$(SRCEXT)
	@mkdir -p $(dir $@)
	$(CC) $(TESTFLAGS) $(TESTINC) $(TESTLIBS) -c -o $@ $<
	@$(CC) $(TESTFLAGS) -MM $(TESTDIR)/$*.$(SRCEXT) > $(TESTBUILD)/$*.$(DEPEXT)
	@cp -f $(TESTBUILD)/$*.$(DEPEXT) $(TESTBUILD)/$*.$(DEPEXT).tmp
	@sed -e 's|.*:|$(TESTBUILD)/$*.$(OBJEXT):|' < $(TESTBUILD)/$*.$(DEPEXT).tmp > $(TESTBUILD)/$*.$(DEPEXT)
	@sed -e 's/.*://' -e 's/\\$$//' < $(TESTBUILD)/$*.$(DEPEXT).tmp | fmt -1 | sed -e 's/^ *//' -e 's/$$/:/' >> $(TESTBUILD)/$*.$(DEPEXT)
	@rm -f $(TESTBUILD)/$*.$(DEPEXT).tmp

# test-run:
# 	@bash test/run.sh

clear: clean-tests

clean: clear
	@$(RM) -rf $(TARGETDIR)

clean-tests:
	@$(RM) -rf $(TESTBUILD)
	@$(RM) -rf $(TESTTARGET)

.PHONY: all clean clear test

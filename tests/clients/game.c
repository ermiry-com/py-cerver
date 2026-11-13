#include <stdlib.h>
#include <stdio.h>
#include <stdbool.h>

#include <signal.h>
#include <pthread.h>

#include <cerver/cerver.h>
#include <cerver/packets.h>

#include <cerver/game/game.h>
#include <cerver/game/gametype.h>

// the game cerver of the e2e tier: the clients of pycerver create and join the lobbies
// of its game type, it runs until SIGINT or SIGTERM
// usage: game <port>

#define GAME_SERVER_NAME				"pycerver-game"
#define GAME_SERVER_GAME_TYPE			"pycerver"
#define GAME_SERVER_MAX_PLAYERS			2
#define GAME_SERVER_THREADS				2

#define GAME_SERVER_ARGUMENTS			2
#define GAME_SERVER_PORT_ARGUMENT		1
#define GAME_SERVER_PORT_BASE			10

static void *game_server_start (void *cerver_ptr) {

	(void) cerver_start ((Cerver *) cerver_ptr);

	return NULL;

}

static bool game_server_register_game_type (Cerver *cerver) {

	bool registered = false;

	GameType *game_type = game_type_create (GAME_SERVER_GAME_TYPE, NULL, NULL, NULL, NULL);
	if (game_type) {
		GameCerver *game_cerver = (GameCerver *) cerver->cerver_data;

		registered = !game_type_add_lobby_config (game_type, true, NULL, GAME_SERVER_MAX_PLAYERS)
			&& !game_type_register (game_cerver->game_types, game_type);

		if (!registered) game_type_delete (game_type);
	}

	return registered;

}

static Cerver *game_server_create (const u16 port) {

	Cerver *cerver = cerver_create (
		CERVER_TYPE_GAME, GAME_SERVER_NAME,
		port, PROTOCOL_TCP, false, CERVER_DEFAULT_CONNECTION_QUEUE
	);

	if (cerver) {
		cerver_set_reusable_address_flags (cerver, true);
		cerver_set_thpool_n_threads (cerver, GAME_SERVER_THREADS);
		cerver_set_handler_type (cerver, CERVER_HANDLER_TYPE_THREADS);

		if (!game_server_register_game_type (cerver)) {
			(void) cerver_teardown (cerver);
			cerver = NULL;
		}
	}

	return cerver;

}

static int game_server_run (Cerver *cerver, sigset_t *signals) {

	int retval = 1;

	pthread_t thread;
	if (!pthread_create (&thread, NULL, game_server_start, cerver)) {
		int signal_number = 0;
		(void) sigwait (signals, &signal_number);

		(void) cerver_shutdown (cerver);
		(void) pthread_join (thread, NULL);

		retval = 0;
	}

	return retval;

}

int main (int argc, const char **argv) {

	int retval = 1;

	if (argc == GAME_SERVER_ARGUMENTS) {
		// every thread of the cerver inherits the blocked signals, only sigwait () gets them
		sigset_t signals;
		(void) sigemptyset (&signals);
		(void) sigaddset (&signals, SIGINT);
		(void) sigaddset (&signals, SIGTERM);
		(void) pthread_sigmask (SIG_BLOCK, &signals, NULL);

		cerver_init ();

		Cerver *cerver = game_server_create (
			(u16) strtoul (argv[GAME_SERVER_PORT_ARGUMENT], NULL, GAME_SERVER_PORT_BASE)
		);

		if (cerver) {
			retval = game_server_run (cerver, &signals);

			if (cerver_teardown (cerver)) retval = 1;
		}

		cerver_end ();
	}

	else {
		(void) fprintf (stderr, "usage: %s <port>\n", argv[0]);
	}

	return retval;

}

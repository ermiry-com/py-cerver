#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include <cerver/http/http.h>
#include <cerver/http/status.h>

#include <cerver/http/json/json.h>

#include <cerver/utils/log.h>
#include <cerver/utils/utils.h>

#include "curl.h"

static const char *address = { "127.0.0.1:8080" };

static const char *token = { "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE2MjUxMDA1MTksImlkIjoiOTU1IiwibmFtZSI6IkVyaWNrIFNhbGFzIiwicm9sZSI6ImNvbW1vbiIsInVzZXJuYW1lIjoiZXJpY2sifQ.Pc1doof72ZhIixa3o5dKJE2zcUYoR9bljf_S6TuSYaiACrD27rYIIFqKIGRzOmqlZf5tEoBKfCAt6GRsvkisr958zh9WICNVuQ7CamKafRXy0Zzb8SLgNbd0eVcqQ1lI_NorhbkEFoNEpEam8g4BZSCcabUpiKtWQAbjCqankjK9nlaILf2BVvlIpkN6rbulF7zi-jJBNAJgKVEueBOkaJAtJZ2AKkigBTxKUYh6_MhyLZiv1m2PBgJJMxChwfPY1NKj1iC_-6W7iHP0K-gAd0yW_f9TL-Tm2ey73BU3kXFxF8H0gEM5cNUcZIV8FBFOUj6V5xT6gMv9GslqPMxTUJY0YPaTq-jLnSXgLSHkzdyB0RRY9EWVLKPg-f6MG_O4Fod-IwQDOgVCz3z2gSgOLkaFRFq5mklKai_8CErEKRrBlVA_RamTsYFgGTyWS6nTnmPuzo95rlxY9x6dYJm5bbkrh2W3qyH2TfI-Jm1_0IgbgujL1GuctohMy_vbNEzSiVHjRuLsSsjN4X0JHYuPyF_bheNnacq64cEWIex4ND3GK5h9DzN4jYj5OsHHNsAKZGVyoEYU5KHKMNhg0nNOrog_6KyZTt6RLsPFGITeswFcVo0AypAqLVIbTMtF346NAFe2pQo7tPPWHdnjL2Bqi64aG4QAb1hckiZwMWc67pI" };

static size_t auth_request_all_data_handler (
	void *contents, size_t size, size_t nmemb, void *storage
) {

	(void) strncpy ((char *) storage, (char *) contents, size * nmemb);

	return size * nmemb;

}

static unsigned int auth_request_custom_success (char *data_buffer) {

	unsigned int retval = 1;

	char actual_address[128] = { 0 };

	CURL *curl = curl_easy_init ();
	if (curl) {
		// POST /auth/custom
		(void) snprintf (actual_address, 128, "%s/auth/custom", address);
		retval = curl_post_form_value (
			curl, actual_address,
			HTTP_STATUS_OK,
			auth_request_all_data_handler, data_buffer,
			"key", "okay"
		);

		curl_easy_cleanup (curl);
	}

	return retval;

}

static unsigned int auth_request_custom_bad (char *data_buffer) {

	unsigned int retval = 1;

	char actual_address[128] = { 0 };

	CURL *curl = curl_easy_init ();
	if (curl) {
		// POST /auth/custom
		(void) snprintf (actual_address, 128, "%s/auth/custom", address);
		retval = curl_post_form_value (
			curl, actual_address,
			HTTP_STATUS_UNAUTHORIZED,
			auth_request_all_data_handler, data_buffer,
			"key", "bad"
		);

		curl_easy_cleanup (curl);
	}

	return retval;

}

static unsigned int auth_request_all_actual (
	CURL *curl
) {

	unsigned int errors = 0;

	char data_buffer[4096] = { 0 };
	char actual_address[128] = { 0 };

	// GET /test
	(void) printf ("GET /test\n");
	(void) snprintf (actual_address, 128, "%s/test", address);
	errors |= curl_simple_handle_data (
		curl, address,
		HTTP_STATUS_OK,
		auth_request_all_data_handler, data_buffer
	);

	// GET /auth/token
	(void) printf ("GET /auth/token\n");
	(void) snprintf (actual_address, 128, "%s/auth/token", address);
	errors |= curl_simple_with_auth (
		curl, actual_address,
		HTTP_STATUS_OK,
		token
	);

	// POST /auth/custom
	(void) printf ("POST /auth/custom - success\n");
	errors |= auth_request_custom_success (data_buffer);

	// POST /auth/custom
	(void) printf ("POST /auth/custom - bad\n");
	errors |= auth_request_custom_bad (data_buffer);

	return errors;

}

// perform requests to every route
static unsigned int auth_request_all (void) {

	unsigned int retval = 1;

	CURL *curl = curl_easy_init ();
	if (curl) {
		if (!auth_request_all_actual (curl)) {
			cerver_log_line_break ();
			cerver_log_line_break ();

			cerver_log_success (
				"auth_request_all () - All requests succeeded!"
			);

			cerver_log_line_break ();
			cerver_log_line_break ();

			retval = 0;
		}
	}

	curl_easy_cleanup (curl);

	return retval;

}

int main (int argc, char **argv) {

	int code = 0;

	cerver_log_init ();

	code = (int) auth_request_all ();

	cerver_log_end ();

	return code;

}
